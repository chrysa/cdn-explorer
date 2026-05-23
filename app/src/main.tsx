import React from "react";
import ReactDOM from "react-dom/client";
import * as Sentry from "@sentry/react";
import { browserTracingIntegration } from "@sentry/react";
import { App } from "./App";

if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN as string,
    environment: (import.meta.env.VITE_ENVIRONMENT as string) ?? "development",
    release: (import.meta.env.VITE_RELEASE as string) ?? "cdn-explorer@0.1.0",
    integrations: [browserTracingIntegration()],
    tracesSampleRate: 0.1,
    sendDefaultPii: false,
  });
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
