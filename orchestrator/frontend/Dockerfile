# ─── build: compile the SPA ──────────────────────────────────────────────────
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

# ─── serve: static assets via nginx ──────────────────────────────────────────
FROM nginx:1.27-alpine AS serve
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Vite base=/app/ emits assets expecting to live under /app/.
COPY --from=build /app/dist /usr/share/nginx/html/app
