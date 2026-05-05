import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ExplorePage } from "@/pages/ExplorePage";
import "./index.css";

const queryClient = new QueryClient();

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ExplorePage />
    </QueryClientProvider>
  );
}
