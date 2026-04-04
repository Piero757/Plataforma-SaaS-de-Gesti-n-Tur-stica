FROM node:20-alpine AS base
WORKDIR /app
RUN apk add --no-cache openssl

# ─── DEPENDENCIES ────────────────────────────────────────────────
FROM base AS deps
COPY package*.json ./
RUN npm ci --only=production

# ─── BUILD ───────────────────────────────────────────────────────
FROM base AS build
COPY package*.json ./
RUN npm ci
COPY . .
RUN npx prisma generate
RUN npm run build

# ─── PRODUCTION IMAGE ─────────────────────────────────────────────
FROM base AS production
ENV NODE_ENV=production

# Copiar dependencias y build
COPY --from=deps /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY --from=build /app/prisma ./prisma
COPY --from=build /app/node_modules/.prisma ./node_modules/.prisma

# Usuario no-root
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs

EXPOSE 4000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -q --spider http://localhost:4000/health || exit 1

CMD ["node", "dist/server.js"]
