import { useQuery } from "@tanstack/react-query";
import { fetchHealth } from "@/api/client";
import styles from "./DemoBanner.module.css";

/**
 * Persistent amber strip shown at the top of the app while demo mode is active
 * (backend DEMO_MODE flag — the crawler serves fixture data and contacts no
 * real CDN). Polls /health and renders nothing when demo mode is off.
 */
export function DemoBanner() {
  const { data } = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
    staleTime: 60_000,
    refetchInterval: 60_000,
  });

  if (!data?.demo_mode) return null;

  return (
    <div className={styles.banner} role="status" data-testid="demo-banner">
      <span className={styles.tag}>DEMO</span>
      <span>
        You&apos;re exploring with fixture data. No real CDN is contacted and no
        credentials are used.
      </span>
    </div>
  );
}
