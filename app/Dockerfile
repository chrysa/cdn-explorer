# ── Stage 1: deps ─────────────────────────────────────────────────────────────
FROM node:22 AS deps

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps

# ── Stage 2: build ────────────────────────────────────────────────────────────
FROM deps AS build

# VITE_API_URL: empty string = relative calls via nginx proxy (dev default)
#               http://localhost:8000 = direct calls (host-network Docker mode)
ARG VITE_API_URL=""
ENV VITE_API_URL=${VITE_API_URL}

COPY . .
RUN npm run build

# ── Stage 3: production (nginx) ───────────────────────────────────────────────
FROM nginx:1.27-alpine AS production

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s CMD wget -qO- http://localhost/ || exit 1

# ── Stage 4: dev ──────────────────────────────────────────────────────────────
FROM deps AS dev

COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]

# ── Stage 5: test ─────────────────────────────────────────────────────────────
FROM deps AS test

COPY . .
CMD ["npm", "test"]
