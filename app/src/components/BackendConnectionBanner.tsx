import { useBackendStatus } from "../hooks/useBackendStatus";

export function BackendConnectionBanner() {
  const isDown = useBackendStatus();

  if (!isDown) return null;

  return (
    <div
      role="alert"
      aria-live="assertive"
      className="sticky top-0 z-50 flex items-center justify-center gap-2 bg-red-600 px-4 py-2 text-sm text-white"
    >
      <span aria-hidden="true">⚠️</span>
      <span>Unable to reach the server. Please check your connection.</span>
    </div>
  );
}
