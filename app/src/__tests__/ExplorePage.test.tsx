import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ExplorePage } from "@/pages/ExplorePage";

vi.mock("@/api/client", () => ({
  exploreUrl: vi.fn().mockResolvedValue({
    root_url: "https://cdn.example.com/docs/",
    total_nodes: 2,
    truncated: false,
    tree: [
      { name: "td-01.pdf", url: "https://cdn.example.com/docs/td-01.pdf", is_dir: false, size: null, children: [] },
      { name: "td-02.pdf", url: "https://cdn.example.com/docs/td-02.pdf", is_dir: false, size: null, children: [] },
    ],
  }),
  buildDownloadUrl: (url: string) => `/api/download?url=${encodeURIComponent(url)}`,
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("ExplorePage", () => {
  it("renders the URL input", () => {
    renderWithQuery(<ExplorePage />);
    expect(screen.getByLabelText("CDN URL")).toBeDefined();
  });

  it("shows results after exploring", async () => {
    renderWithQuery(<ExplorePage />);

    const input = screen.getByLabelText("CDN URL");
    fireEvent.change(input, { target: { value: "https://cdn.example.com/docs/" } });

    const button = screen.getByRole("button", { name: /explore/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/2 files found/i)).toBeDefined();
    });

    expect(screen.getByText("td-01.pdf")).toBeDefined();
    expect(screen.getByText("td-02.pdf")).toBeDefined();
  });
});
