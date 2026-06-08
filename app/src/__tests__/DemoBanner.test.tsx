import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DemoBanner } from "@/components/DemoBanner";
import type { HealthStatus } from "@/domain/types";
import * as client from "@/api/client";

vi.mock("@/api/client");
const mockHealth = client.fetchHealth as ReturnType<typeof vi.fn>;

function health(demoMode: boolean): HealthStatus {
  return { status: "ok", demo_mode: demoMode };
}

function renderBanner() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <DemoBanner />
    </QueryClientProvider>,
  );
}

describe("DemoBanner", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the amber DEMO banner when demo mode is active", async () => {
    mockHealth.mockResolvedValue(health(true));
    renderBanner();
    const banner = await screen.findByTestId("demo-banner");
    expect(banner).toBeDefined();
    expect(banner.getAttribute("role")).toBe("status");
    expect(banner.textContent).toContain("DEMO");
    expect(banner.textContent?.toLowerCase()).toContain("fixture data");
  });

  it("renders nothing when demo mode is off", async () => {
    mockHealth.mockResolvedValue(health(false));
    renderBanner();
    await waitFor(() => expect(mockHealth).toHaveBeenCalled());
    expect(screen.queryByTestId("demo-banner")).toBeNull();
  });
});
