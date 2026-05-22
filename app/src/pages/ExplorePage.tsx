import { useState, useCallback } from "react";
import { useMutation } from "@tanstack/react-query";
import type { ExploreResponse } from "@/domain/types";
import { exploreUrl, buildDownloadUrl } from "@/api/client";
import { FileTree } from "@/components/FileTree";
import { ScanLog } from "@/components/ScanLog";
import { Search, Download } from "lucide-react";
import styles from "./ExplorePage.module.css";

export function ExplorePage() {
  const [url, setUrl] = useState("");
  const [selected, setSelected] = useState<Set<string>>(new Set());

  const { mutate, data, isPending, error, reset } = useMutation<
    ExploreResponse,
    Error,
    string
  >({
    mutationFn: (inputUrl) => exploreUrl({ url: inputUrl }),
    onSuccess: () => setSelected(new Set()),
  });

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (url.trim()) {
        reset();
        mutate(url.trim());
      }
    },
    [url, mutate, reset],
  );

  const toggleSelected = useCallback((fileUrl: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(fileUrl)) {
        next.delete(fileUrl);
      } else {
        next.add(fileUrl);
      }
      return next;
    });
  }, []);

  const downloadSelected = useCallback(() => {
    selected.forEach((fileUrl) => {
      const a = document.createElement("a");
      a.href = buildDownloadUrl(fileUrl);
      a.download = fileUrl.split("/").pop() ?? "file";
      a.click();
    });
  }, [selected]);

  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>CDN Explorer</h1>
        <p className={styles.subtitle}>
          Navigate and download files from public CDN directory listings.
        </p>
      </header>

      <form className={styles.form} onSubmit={handleSubmit}>
        <input
          className={styles.input}
          type="url"
          placeholder="https://cdn.example.com/resources/"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
          aria-label="CDN URL"
        />
        <button className={styles.button} type="submit" disabled={isPending}>
          <Search size={16} />
          {isPending ? "Exploring…" : "Explore"}
        </button>
      </form>

      {error && (
        <div className={styles.error} role="alert">
          {error.message}
        </div>
      )}

      {data && (
        <section className={styles.results}>
          <div className={styles.resultsMeta}>
            <span>
              <strong>{data.total_nodes}</strong> file
              {data.total_nodes !== 1 ? "s" : ""} found
              {data.truncated && " (results truncated — too many files)"}
            </span>
            {selected.size > 0 && (
              <button className={styles.downloadBtn} onClick={downloadSelected}>
                <Download size={14} />
                Download {selected.size} selected
              </button>
            )}
          </div>

          <div className={styles.tree}>
            <FileTree
              nodes={data.tree}
              selected={selected}
              onToggle={toggleSelected}
            />
          </div>

          <ScanLog log={data.log ?? []} />
        </section>
      )}
    </main>
  );
}
