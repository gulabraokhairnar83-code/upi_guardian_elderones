# syntax=docker/dockerfile:1
# UPI Guardian - Production Hardened Frontend Container

# Stage 1: Build
FROM node:20-alpine as builder

WORKDIR /app

# Copy dependency specifications
COPY package.json package-lock.json* ./

# Clean installation of dependencies
RUN npm ci

# Copy application source code
COPY . .

# Build argument for backend API URL (defaults to production placeholder)
ARG VITE_API_BASE_URL=http://localhost:5000/api
ARG VITE_USE_MOCK_API=false
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_USE_MOCK_API=$VITE_USE_MOCK_API

# Run production build
RUN npm run build

# Stage 2: Production Runner
FROM node:20-alpine as runner

WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000

# Install lightweight serve utility for production static artifact hosting
RUN npm install -g serve && rm -rf /root/.npm

# Copy built public distribution assets
COPY --from=builder /app/.output/public ./public
COPY --from=builder /app/package.json ./

# Switch to non-root user
USER node

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:3000/ || exit 1

CMD ["serve", "-s", "public", "-l", "3000"]
