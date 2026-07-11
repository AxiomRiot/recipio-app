FROM node:20-alpine AS base
WORKDIR /app

# Copy only the package.json files first for bettery layer caching. 
# If only application code changes (not deps), Docker resuses
# the cached npm install layer
FROM base AS deps

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml tsconfig.json ./
COPY packages/logger-ts/package.json ./packages/logger-ts/package.json
COPY packages/types-ts/package.json ./packages/types-ts/package.json
COPY services/core-api/package.json ./services/core-api/package.json

RUN npm install -g pnpm && pnpm install --frozen-lockfile --ignore-scripts

# BUILD STAGE
FROM deps AS build

# shared src
COPY packages/logger-ts ./packages/logger-ts
COPY packages/types-ts/ ./packages/types-ts

# service
COPY services/core-api ./services/core-api

# build shared workspace packages first, then core-api
RUN pnpm --filter @recipe-app/logger-ts build && \
    pnpm --filter @recipe-app/types-ts build && \
    pnpm --filter core-api build

# PRODUCTION STAGE
FROM base AS production
ENV NODE_ENV=production

COPY --from=build /app/node_modules ./app/node_modules
COPY --from=build /app/services/core-api/node_modules ./app/services/core-api/node_modules
COPY --from=build /app/services/core-api/dist ./app/services/core-api/dist
COPY --from=build /app/packages ./app/packages

WORKDIR /app

EXPOSE 1234

CMD ["node", "./app/services/core-api/dist/index.js"]