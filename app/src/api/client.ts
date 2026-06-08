import type {
  ExploreRequest,
  ExploreResponse,
  HealthStatus,
} from "@/domain/types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function fetchHealth(): Promise<HealthStatus> {
  const response = await fetch(`${BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed (${response.status})`);
  }
  return response.json() as Promise<HealthStatus>;
}

export async function exploreUrl(
  req: ExploreRequest,
): Promise<ExploreResponse> {
  const response = await fetch(`${BASE_URL}/api/explore`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Explore failed (${response.status}): ${detail}`);
  }
  return response.json() as Promise<ExploreResponse>;
}

export function buildDownloadUrl(fileUrl: string): string {
  return `${BASE_URL}/api/download?url=${encodeURIComponent(fileUrl)}`;
}
