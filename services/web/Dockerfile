# ── Build stage ──────────────────────────────────────────
FROM node:22-alpine AS build

WORKDIR /app

# Install dependencies first (cache-friendly)
COPY services/web/package.json services/web/package-lock.json* ./
RUN npm install

# Copy source and build
COPY services/web/ ./
RUN npm run build

# ── Production stage ─────────────────────────────────────
FROM node:22-alpine

WORKDIR /app

# Only copy the built output and production deps
COPY --from=build /app/build ./build
COPY --from=build /app/package.json ./
RUN npm install --omit=dev 2>/dev/null || true

ENV NODE_ENV=production
ENV PORT=3000
ENV API_URL=http://api:8000

EXPOSE 3000

CMD ["node", "build/index.js"]
