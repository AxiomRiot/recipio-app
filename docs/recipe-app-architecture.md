# Recipe App — Architecture Reference

A living reference for every architectural decision made during the design of the recipe app. Covers service design, Kafka event schema, folder structure, shared packages, logging, deployment, and interview talking points.

---

## Table of Contents

1. [Project Goals](#project-goals)
2. [Frontend Features](#frontend-features)
3. [Services Overview](#services-overview)
4. [Folder Structure](#folder-structure)
5. [Shared Packages](#shared-packages)
6. [Kafka Architecture](#kafka-architecture)
7. [Event Schema](#event-schema)
8. [Core-API Architecture](#core-api-architecture)
9. [Scraper Service Architecture](#scraper-service-architecture)
10. [Gateway and Core-API Interaction](#gateway-and-core-api-interaction)
11. [Logging](#logging)
12. [Deployment](#deployment)
13. [Key Architectural Decisions](#key-architectural-decisions)
14. [Interview Talking Points](#interview-talking-points)

---

## Project Goals

- A recipe app you actually use day-to-day (scrape recipes, generate grocery lists, weekly meal planning, recommendations)
- A portfolio project demonstrating senior-level architecture thinking: distributed systems, event-driven design, polyglot services, shared contracts
- Intentionally complicated in ways that are *load-bearing* (each complexity decision solves a real problem), not decorative

---
## Frontend Features
- User can provide URL for the application to scrape
- User can create their own recipes manually
- User can view all recipes via pagination
- User can filter on recipes by category, ingredients, cuisine
- User can generate a custom meal plan with random or based on nutritional guidelines 
- User can generate a grocery list based on user defined recipes or meal plan

## Services Overview

| Service | Language | Owns | Does Not Own |
|---|---|---|---|
| `gateway` | Node/TypeScript | Auth (JWT), routing, rate limiting | Business logic, DB access |
| `core-api` | Node/TypeScript | Recipes, users, meal plans, grocery lists | Crawl state, HTML parsing |
| `crawler` | Python | URL discovery, crawl state, per-domain rate limiting | HTML parsing |
| `scraper` | Python | Parsing one URL → structured recipe | Discovery, retry policy |
| `recommendation` | Python | Similarity search, meal plan suggestions | Recipe data writes |

### Why these boundaries

- **Crawler and scraper are separate** because discovery (stateful, manages visited URLs, respects robots.txt) and parsing (stateless, one URL → one recipe) are different problems with different scaling profiles. The scraper is horizontally scalable; the crawler is not.
- **Recommendation is separate** because its failure mode is independent — if recommendations are down, recipes still work. Separate failure domains.
- **No dedicated logging service** — a logging *service* that other services call is an anti-pattern. If it's slow or down, do you block the caller? Instead, each service writes structured JSON to stdout; a log aggregator (Promtail) ships it to a central store (Loki).
- **A scheduler/job-service gap exists** — something needs to trigger "generate this week's meal plan" or "remind me to cook Tuesday's dinner." Currently a cron job in core-api; worth knowing it's a real seam.

---

## Folder Structure

```
recipe-app/
  services/
    gateway/          # Node/TypeScript — auth, routing, rate limiting
    core-api/         # Node/TypeScript — recipes, users, meal plans
    scraper/          # Python — parses one URL into a structured recipe
    crawler/          # Python — discovers recipe URLs from a site
    recommendation/   # Python — similarity, suggestions, meal planning
  packages/
    ts-types/         # Shared TypeScript types (Recipe, MealPlan, etc.)
    kafka-client-ts/  # Shared EventProducer/EventConsumer classes
    logger-ts/        # Shared Winston logger factory
    events/           # Canonical event schemas (JSON Schema) + topics.json
    py-utils/         # Shared Python utilities (Kafka base classes, domain helpers)
  apps/
    web/              # Frontend (React/Next.js)
  infra/
    compose/          # Split Docker Compose files for local dev
    kafka/            # topics.yml + create-topics.sh
    terraform/        # (future) cloud provisioning
    monitoring/       # (future) Prometheus + Grafana dashboards
    scripts/          # replay-dlq.py, seed-dev-data.py, reset-local-stack.sh
  docker-compose.yml  # Dev shortcut at root
  Makefile            # make dev, make test, make lint
  pnpm-workspace.yaml
  README.md
```

### Key structural decisions

- **Monorepo** — shared packages (`ts-types`, `events`, `kafka-client-ts`) make a monorepo the obvious choice. Polyrepo would mean duplicating or versioning these separately with no real benefit at this scale.
- **`apps/` vs `services/`** — convention: `apps/` = things users interact with; `services/` = things other services interact with.
- **Build context is repo root** — all Dockerfiles use `context: .` (repo root) so they can reach `packages/`. Docker Compose `build.context` must be `../..` from `infra/compose/`.

---

## Shared Packages

### `packages/events/` — canonical source of truth

Contains the JSON Schema for every Kafka event and `topics.json`. Every language-specific package derives from here. Neither TypeScript nor Python should hardcode event shapes or topic strings.

```json
// packages/events/topics.json
{
  "CRAWL_REQUESTED": "crawl-requested",
  "SCRAPE_REQUESTED": "scrape-requested",
  "RECIPE_PARSED": "recipe-parsed",
  "SCRAPE_FAILED": "scrape-failed",
  "RECIPE_EVENT": "recipe-event",
  "MEAL_PLAN_EVENT": "meal-plan-event"
}
```

### `packages/ts-types/` — TypeScript types

Imports from `packages/events/` via `resolveJsonModule`. Exports typed constants and the `TopicName` union.

```typescript
// packages/ts-types/topics.ts
import topicsJson from '../events/topics.json'

export const Topics = topicsJson as const
export type TopicName = typeof Topics[keyof typeof Topics]
// TopicName = "crawl-requested" | "scrape-requested" | "recipe-parsed" | ...
```

**Important**: Use `as const` not `satisfies Record<string, string>`. The `satisfies` keyword validates the shape but widens the values to `string`, breaking `TopicName`'s literal union.

Event schemas use Zod, exported as both a schema and an inferred type:

```typescript
export const RecipeParsedEventSchema = z.object({
  header: z.object({ event_id: z.uuid(), timestamp: z.date() }),
  event_type: z.literal('recipe-parsed'),
  payload: z.object({ ... }),
})
export type RecipeParsedEvent = z.infer<typeof RecipeParsedEventSchema>

export const EventSchemasByTopic = {
  'recipe-parsed': RecipeParsedEventSchema,
  'scrape-requested': ScrapeRequestedEventSchema,
} as const

export type EventPayloadMap = {
  [K in keyof typeof EventSchemasByTopic]: z.infer<typeof EventSchemasByTopic[K]>
}
```

### `packages/kafka-client-ts/` — shared Kafka client

Wraps KafkaJS with typed producers and consumers. Classes, not standalone functions, because Kafka connections are stateful — they need to hold an open connection between calls.

```typescript
export class EventProducer {
  async connect(): Promise<void>
  async publish<T>(topic: TopicName, key: string, event: EventEnvelope<T>): Promise<void>
  async disconnect(): Promise<void>
}

export type MessageHandler<T extends TopicName> = (
  topic: T,
  event: EventPayloadMap[T],
  raw: { key: string | null }
) => Promise<void>

export class EventConsumer {
  async subscribe<T extends TopicName>(topics: T[], handler: MessageHandler<T>): Promise<void>
  async disconnect(): Promise<void>
}
```

**Key implementation details:**

- `isKnownTopic(topic: string): topic is TopicName` type guard — uses `topic in EventSchemasByTopic` for genuine control-flow narrowing instead of a cast. Fixes `EventSchemasByTopic[topic as TopicName]` index error.
- Three failure modes in `eachMessage`, three behaviors:
  - JSON parse failure → log + `return` (bad data, don't retry)
  - Schema validation failure → log + `return` (bad contract, not transient)
  - Handler throws → log + `throw` (transient failure, let KafkaJS retry)
- Instantiate producer/consumer **once at startup** in `index.ts`, inject via constructors. Never `new EventProducer()` inside a service method — that reconnects per call and exhausts connections under load.

### `packages/logger-ts/` — shared logger factory

```typescript
import winston from 'winston'

export function createServiceLogger(serviceName: string) {
  return winston.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    defaultMeta: { service: serviceName },
    format: winston.format.combine(
      winston.format.timestamp(),
      winston.format.json(),
    ),
    transports: [new winston.transports.Console()],
  })
}
```

Each service creates one instance at module level and imports it everywhere:

```typescript
// services/core-api/src/logger.ts
import { createServiceLogger } from '@recipe-app/logger-ts'
export const logger = createServiceLogger('core-api')
```

`defaultMeta: { service: serviceName }` tags every log line automatically — no call site has to remember. This is what makes `{service="core-api"}` work as a Loki label query.

### `packages/py-utils/` — shared Python utilities

Shared *behavior* (Kafka base classes, domain extraction, retry helpers, robots.txt parsing) used by both scraper and crawler. **Not** the event schemas — those live in each Python service's own `schemas.py` (only the relevant subset per service), validated by Pydantic at runtime.

Install as editable local package in Python services:

```
# services/scraper/requirements.txt
-e ../../packages/py-utils
kafka-python==2.0.2
beautifulsoup4==4.12.3
pydantic==2.6.1
```

---

## Kafka Architecture

### Why Kafka (not a managed queue like SQS)

Self-hosted Kafka forces engagement with the real concepts: partitioning, consumer groups, offset management, rebalancing. Managed queues abstract these away — useful in production, less educational.

### Topics

| Topic | Partitions | Key | Retention | Notes |
|---|---|---|---|---|
| `crawl-requested` | 3 | `userId` | 7 days | Single-URL submits skip this entirely |
| `scrape-requested` | 6 | **domain** | 7 days | Partition by domain for per-domain rate limiting |
| `recipe-parsed` | 6 | `userId` | 14 days | Consumed by core-api AND recommendation |
| `scrape-failed` | 3 | `userId` | 30 days | DLQ — longer retention for manual review |
| `recipe-event` | 6 | `userId` | 30 days | viewed/cooked/saved/skipped — feeds recommendations |
| `meal-plan-event` | 3 | `userId` | 14 days | |

### Partition key decisions

- **Most topics: `userId`** — guarantees ordering per user, natural sharding key, collocates one user's events on the same partition.
- **`scrape-requested`: domain** — all requests to `allrecipes.com` land on the same partition/consumer instance, making per-domain rate limiting trivial without cross-instance coordination.

### Scraper scalability

Scraper is stateless (one URL in, one recipe out) → horizontally scalable. Multiple instances form one consumer group on `scrape-requested`. Kafka distributes partition assignments automatically. **Ceiling: you cannot have more active consumer instances than partitions.** 6 partitions = max 6 concurrent scraper instances.

### `crawlId` threading

A `crawl-requested` event generates a `crawlId` that propagates into every child `scrape-requested` event and up into `recipe-parsed`. This is how you track crawl completion ("17 of 23 recipes imported") and query "all recipes from this crawl job" — without it, you'd have no way to know when a crawl is done.

### Topic configuration

```yaml
# infra/kafka/topics.yml
topics:
  - name: scrape-requested
    partitions: 6
    replication_factor: 1       # single broker for local dev; use 3 in production
    retention_ms: 604800000     # 7 days
    cleanup_policy: delete
  # ... etc
```

```bash
# infra/kafka/create-topics.sh
# Uses --if-not-exists for idempotency (safe to run every docker compose up)
# Reads topics.yml via yq, loops over entries calling kafka-topics.sh --create
```

Run as a one-shot Docker Compose service that depends on `kafka: service_healthy`.

---

## Event Schema

### Envelope pattern

Every event shares the same outer shape regardless of topic:

```typescript
{
  header: {
    event_id: string    // uuid, idempotency key
    timestamp: Date
  }
  event_type: string    // literal — discriminant for multi-type topics
  payload: { ... }      // topic-specific
}
```

**Why `event_type` when the topic already identifies the event?**

- `recipe-event` carries four sub-types (viewed/cooked/saved/skipped) on one topic — the topic alone can't distinguish them.
- Events leave Kafka context (logs, DLQ replay, audit tables) — `event_type` keeps the payload self-describing.
- Zod's `z.discriminatedUnion('event_type', [...])` gives exhaustiveness checking when handling a multi-type topic.
- Makes the envelope self-describing for logging, debugging, and replay tooling.

### Event flows by scenario

**Single URL scrape:**
```
core-api → [scrape-requested] → scraper → [recipe-parsed] → core-api + recommendation
```

**Whole site crawl:**
```
core-api → [crawl-requested] → crawler → N × [scrape-requested] → scraper (N instances)
```

**Scrape failure after 3 attempts:**
```
scraper → [scrape-failed DLQ] → core-api (marks recipe status = failed)
```

**User behaviour:**
```
core-api → [recipe-event: viewed/cooked] → recommendation (updates preference model)
```

---

## Core-API Architecture

### Layer stack

```
Request
  ↓
Routes          — defines endpoint + attaches middleware
  ↓
Controllers     — parse input, shape validate (Zod), call service, map errors to HTTP
  ↓
Services        — business logic, business validation, DB queries, Kafka produces
  ↓
db/             — Prisma schema and queries
kafka/          — producers (emit events) and consumers (handle incoming events)
```

### Layer rules

- **Controllers never import Prisma directly** — DB access only through services.
- **Services are HTTP-agnostic** — they throw domain errors (`ValidationError`, `ConflictError`), never touch `req`/`res`.
- **Controllers make one service call per handler** — orchestration of multiple services belongs in a higher-level service (e.g. `mealPlanOrchestrator.ts`), not in the controller.
- **Consumers call the same service layer that controllers do** — `recipeParsedConsumer.ts` calls `recipeService.createFromScrape()`, the same function an HTTP controller would call if a user created a recipe manually. One business-logic entry point, two ways in.

### Dependency injection

Producer/consumer are created **once at startup** in `index.ts` and injected into services via constructors:

```typescript
// services/core-api/src/index.ts
const producer = new EventProducer(kafka)
await producer.connect()
const recipeService = new RecipeService({ db: prisma, producer })
const recipeController = new RecipeController({ recipeService })

process.on('SIGTERM', async () => {
  await producer.disconnect()
  server.close()
})
```

This makes services unit-testable — in a test, pass `{ db: fakePrisma, producer: { publish: jest.fn() } }`.

### Validation split

- **Shape validation** (right fields, right types) → controller, using Zod's `safeParse`. Malformed input never reaches the service.
- **Business validation** (recipe already exists, user owns this meal plan) → service. Requires DB access and domain knowledge.

---

## Scraper Service Architecture

### Internal flow

```
consumer.py
  → schemas.py (validate ScrapeRequestedEvent)
  → parser.py (fetch URL, extract recipe)
    → JSON-LD first (structured recipe markup)
    → fallback: heuristic HTML parsing
  → schemas.py (build RecipeParsedEvent)
  → producer.py (publish to recipe-parsed)
```

On failure: `consumer.py` catches `ParseError`/`FetchTimeoutError` from `parser.py`, retries with exponential backoff, eventually emits to `scrape-failed` DLQ.

### File responsibilities

| File | Owns | Does not own |
|---|---|---|
| `consumer.py` | Kafka consumer loop, retry/backoff policy | Parsing logic |
| `parser.py` | HTML fetch + recipe extraction, raises clean exceptions | Kafka, retry decisions |
| `producer.py` | Kafka producer, publishes results | What to publish or when |
| `schemas.py` | Pydantic models for inbound/outbound events | Kafka, HTTP, business logic |

`parser.py` is a pure function (URL in, structured dict or exception out). If you swapped domains (job listings instead of recipes), only this file changes.

`schemas.py` is touched twice per message: once to validate the inbound `ScrapeRequestedEvent`, once to build the outbound `RecipeParsedEvent`. It never touches Kafka or HTTP — pure data definitions, easy to unit test.

### Rate limiting

Per-domain rate limit coordination between multiple stateless scraper instances: a shared Redis key (`rate_limit:allrecipes.com`) that instances check before fetching. If set (recent 429 received), requeue the message with a delay instead of processing.

---

## Gateway and Core-API Interaction

### Request flow

```
Frontend
  → Gateway: validates JWT, strips Authorization header,
             injects X-User-Id header, checks rate limit
  → Core-API: trusts X-User-Id (request came from gateway),
              runs business logic, returns result
```

### Trust boundary

Core-API should only accept requests from the Gateway, not the open internet:

- In Docker Compose: core-api on internal network, not exposed on a public port
- Optionally: core-api checks for `X-Internal-Secret` header the gateway always attaches

### What the gateway owns vs. doesn't

| Concern | Gateway | Core-API |
|---|---|---|
| JWT validation | ✓ | ✗ |
| Rate limiting per user | ✓ | ✗ |
| CORS headers | ✓ | ✗ |
| Recipe business logic | ✗ | ✓ |
| Kafka producing | ✗ | ✓ |
| Auth logic | ✓ only | ✗ |

### Routing to recommendation service

The frontend calls `/api/recommendations` the same way it calls `/api/recipes`. The gateway makes the two services look like one coherent API — the frontend never knows a split exists.

---

## Logging

### Architecture

```
Each service writes structured JSON to stdout
  → Promtail (Docker socket discovery on Compose, DaemonSet on k3s)
  → Loki (label-indexed log store)
  → Grafana (query UI)
```

No dedicated logging *service* — that's an anti-pattern (if it's down, do callers block?).

### Why Loki over Elasticsearch

Loki only indexes labels (service name, log level), not full log text. Much lighter to run, much less operational overhead. Grafana is the same UI you'd use for metrics, so one tool instead of Kibana + Grafana.

### Promtail on Docker Compose

Uses `docker_sd_configs` (Docker socket) for container auto-discovery. The `docker: {}` pipeline stage unwraps Docker's log envelope. The `json` stage promotes `service` and `level` fields from inside the JSON log line into real Loki labels.

### Promtail on k3s

Uses `kubernetes_sd_configs: role: pod` for auto-discovery. The `cri: {}` stage unwraps containerd's log format instead of Docker's. Everything else identical.

### Why the configs only differ by one line (hostname)

Docker Compose: `url: http://loki:3100`
k3s: `url: http://loki.logging.svc.cluster.local:3100`

Application code, log format, labels — none of it changes. The `defaultMeta: { service: 'core-api' }` in Winston and the Promtail `json` pipeline stage that reads it are built to work together regardless of environment.

### Querying in Grafana

```
{service="core-api"} |= "scrapeRequestId"
{service="scraper"} |= "scrapeRequestId"
```

Filter by `scrapeRequestId` across both services side by side to trace one message's full journey — possible because `scrapeRequestId` is a structured field (not buried in an interpolated string) in both services' log output.

---

## Deployment

### Current: Docker Compose on laptop

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Target: k3s across 4 × Raspberry Pi 5

- Pi 5 8GB RAM each, 32GB total cluster — enough headroom for Kafka's JVM + full stack
- k3s (not full K8s) — single binary, built for ARM64/Pi hardware specifically
- One Pi runs `k3s server` (control plane), three run `k3s agent`
- **Why k3s over Docker Compose here**: Compose can only use one machine. With 4 nodes, you want the scheduler to distribute workloads across them — that's the actual problem k3s solves. On a single Pi, Compose would have been fine.

### CI/CD: GitHub Actions → home server

```
git push → GitHub Actions:
  1. Build each service image (context: repo root for packages/ access)
  2. Push to GHCR (free, auth via GITHUB_TOKEN)
  3. SSH into home server via Tailscale tunnel
  4. kubectl apply -f k8s/ (or docker compose pull && up -d during transition)
```

**Tailscale** for the SSH tunnel — home server isn't publicly addressable, Tailscale lets GitHub's runners join your private network without exposing SSH to the open internet.

### Docker Compose file split

```
infra/compose/
  docker-compose.yml          # shared base (networks, volumes, env vars)
  docker-compose.dev.yml      # build: for each service (local dev)
  docker-compose.prod.yml     # image: ghcr.io/... for each service (CI/server)
  docker-compose.kafka.yml    # Kafka + Zookeeper/KRaft + topic-init
  docker-compose.data.yml     # Postgres + pgvector, Redis
  docker-compose.logging.yml  # Loki + Promtail + Grafana
```

### Dockerfile structure (core-api as example)

Multi-stage build:
1. `deps` stage — copy `package.json` files only, run `pnpm install --frozen-lockfile` (cached if deps unchanged)
2. `build` stage — copy source, run `pnpm --filter core-api build`
3. `production` stage — copy only `dist/` and `node_modules`, discard everything else

Build context must be repo root (`context: ../..`) so Dockerfile can `COPY packages/` into the image.

### pnpm workspaces

```yaml
# pnpm-workspace.yaml
packages:
  - "services/*"
  - "packages/*"
  - "apps/*"
```

Services depend on shared packages via `"@recipe-app/ts-types": "workspace:*"`. pnpm symlinks `node_modules/@recipe-app/ts-types` → `packages/ts-types`. Never write `pnpm-lock.yaml` by hand — run `pnpm install` at the repo root to generate it.

---

## Key Architectural Decisions

### Things decided and why

| Decision | Reasoning |
|---|---|
| Kafka over SQS/RabbitMQ | Forces real partition/consumer-group understanding; interview talking points |
| Monorepo | Shared packages make polyrepo painful — one PR to update an event schema |
| `packages/events/` as canonical source | Prevents schema drift between TypeScript and Python services |
| Partition `scrape-requested` by domain | Collocates domain traffic on one consumer instance → trivial rate limiting |
| `eventType` inside every event | Topics with multiple sub-types (recipe-event) need a discriminant; envelope self-describing outside Kafka context |
| No logging service | Anti-pattern — a dependency in the call path of a non-critical concern |
| DI at startup in `index.ts` | Single lifecycle owner; services become unit-testable with fakes |
| Controller/service split | Services stay HTTP-agnostic — Kafka consumers can call the same service methods |
| `isKnownTopic` type guard over cast | Real runtime check + genuine TS narrowing vs. a lie to the compiler |
| Promtail over Fluentd | Lighter, native Loki pairing, same tool in both Compose and k3s environments |
| k3s over Docker Compose on 4 Pis | Compose can only use one host; 4 nodes need a scheduler |
| k3s over full K8s | Single binary, ARM64 native, built for Pi-class hardware |

### Things explicitly deferred and why

| Deferred | When to add it |
|---|---|
| `terraform/` | When actually deploying to cloud, not before |
| `monitoring/` (Prometheus/Grafana metrics) | Once services are stable and you have real traffic to observe |
| Formal DI container (InversifyJS) | When hand-wired DI in `index.ts` becomes unwieldy across dozens of services |
| Schema codegen (JSON Schema → TS/Python types) | When hand-syncing two files becomes a real drift problem |
| k3s migration | After app logic proven end-to-end on Compose |
| `user-service` split from core-api | Not worth the network hop until users and recipes genuinely need independent scaling |

---

## Interview Talking Points

### System design

- **Fan-out via queue**: one `crawl-requested` event fans out into N `scrape-requested` events. If 3 fail, retry only those 3 — not the whole crawl.
- **Partition key tradeoff**: `userId` for most topics (ordering per user) vs. `domain` for scrape-requested (rate-limit colocation). Same key design, different tradeoff, different answer.
- **Read vs write path separation**: status store (Postgres) separate from the queue because Kafka is bad at point-lookups. "How did we get this recipe's current status?" goes to Postgres, not Kafka.
- **Hot partition problem**: partitioning `scrape-requested` by domain creates a hot partition if one domain sends disproportionate volume. Know the tradeoff before being asked.
- **Replication factor**: `1` for local dev (single broker), `3` for production (minimum for fault tolerance). Being able to state this distinction cold matters.

### Distributed systems

- **Idempotency keys**: duplicate scrape requests (retry-at-the-edge) shouldn't double-scrape. `event_id` in the header is the deduplication key.
- **Schema drift**: without `packages/events/` as canonical source, TypeScript and Python services independently defining `RecipeParsedEvent` will silently diverge. The failure mode is a consumer throwing a confusing null-pointer error three calls deep, not a clear "wrong shape" error at the boundary.
- **Circuit breaker**: if AllRecipes starts returning 429s, all 6 scraper instances should back off — coordinated via a shared Redis key, not individually.
- **DLQ as a topic, not a DB table**: lets you replay failures through the same consumer machinery (the `replay-dlq.py` script) instead of building a separate repair path.

### Code architecture

- **Why services are HTTP-agnostic**: Kafka consumers call the same service methods HTTP controllers do. If `recipeService.createFromScrape()` knew about `req`/`res`, it couldn't be called from a Kafka consumer without wrapping it in fake HTTP objects.
- **Why one logger instance per service**: `defaultMeta: { service: 'core-api' }` tags every log line automatically. Multiple logger instances risk a typo'd `service: "core_api"` splitting your Loki query results silently.
- **The `as const` vs `satisfies` distinction**: `satisfies Record<string, string>` validates shape but widens values to `string`, breaking `TopicName`'s literal union. `as const` preserves literal types. Knowing the difference shows real TypeScript depth.
- **Why the consumer class owns schema validation**: a malformed message fails at the boundary with a clear error, not three service calls deep with a confusing `undefined.ingredients`. The `isKnownTopic` guard is a runtime check that also enables TypeScript control-flow narrowing — two benefits from one line.
