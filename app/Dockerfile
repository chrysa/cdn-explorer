# ── Stage 1: deps ─────────────────────────────────────────────────────────────
FROM node:22 AS deps

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps

# ── Stage 2: build ────────────────────────────────────────────────────────────
FROM deps AS build

# VITE_API_URL: empty string = relative calls (dev default)
#               http://localhost:8000 = direct calls (host-network Docker mode)
ARG VITE_API_URL=""
ENV VITE_API_URL=${VITE_API_URL}

COPY . .
RUN npm run build

# ── Stage 3: production ────────────────────────────────────────────────────────────────────────────────────
FROM deps AS production

COPY --from=build /app/dist ./dist

EXPOSE 4173
HEALTHCHECK --interval=30s --timeout=5s CMD wget -qO- http://localhost:4173/ || exit 1

CMD ["./node_modules/.bin/vite", "preview", "--host", "0.0.0.0", "--port", "4173"]

# ── Stage 4: dev ──────────────────────────────────────────────────────────────
FROM deps AS dev

COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]

# ── Stage 5: test ─────────────────────────────────────────────────────────────
FROM deps AS test

COPY . .
CMD ["npm", "test"]
