FROM node:20-alpine AS base
WORKDIR /app

# Copy only the package.json files first for bettery layer caching. 
# If only application code changes (not deps), Docker resuses
# the cached npm install layer
FROM base AS deps

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml tsconfig.json ./
COPY packages/logger-ts/package.json ./packages/logger-ts/package.json
COPY packages/types/package.json ./packages/types/package.json
COPY services/core-api/package.json ./services/core-api/package.json

RUN npm install -g pnpm && pnpm install --frozen-lockfile --ignore-scripts

# BUILD STAGE
FROM deps AS build

# shared src
COPY packages/logger-ts ./packages/logger-ts
COPY packages/types/ ./packages/types
COPY packages/events ./packages/events

# service
COPY services/core-api ./services/core-api

# only run pnpm against core-api service and deps
RUN pnpm --filter core-api build

# PRODUCTION STAGE
FROM base AS production
ENV NODE_ENV=production

COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/services/core-api ./app
COPY --from=build /app/packages ./packages

WORKDIR /app

EXPOSE 3000

CMD ["tail", "-f", "/dev/null"]