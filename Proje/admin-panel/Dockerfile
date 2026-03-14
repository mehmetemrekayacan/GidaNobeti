FROM node:20-alpine AS base
WORKDIR /app

# Install dependencies once for better layer caching
FROM base AS deps
COPY package.json package-lock.json* ./
RUN npm install

# Development stage (next dev)
FROM base AS dev
ENV NODE_ENV=development
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "3000"]

# Build stage (expects output: "standalone" in next.config)
FROM base AS builder
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production stage (standalone)
FROM node:20-alpine AS standalone
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]