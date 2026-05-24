import { useState } from "react";
import styles from "./ScanLog.module.css";

interface ScanLogProps {
  log: string[];
}

export function ScanLog({ log }: ScanLogProps) {
  const [open, setOpen] = useState(false);

  if (log.length === 0) return null;

  return (
    <details
      className={styles.details}
      open={open}
      onToggle={(e) => setOpen((e.currentTarget as HTMLDetailsElement).open)}
    >
      <summary className={styles.summary}>
        Scan log <span className={styles.count}>{log.length} entries</span>
      </summary>
      <pre className={styles.log}>
        {log.map((line, i) => (
          <LogLine key={i} line={line} />
        ))}
      </pre>
    </details>
  );
}

function LogLine({ line }: { line: string }) {
  let cls = styles.lineDefault;
  if (line.includes("✗") || line.includes("✘")) cls = styles.lineError;
  else if (line.includes("✔") || line.includes("📄")) cls = styles.lineSuccess;
  else if (line.includes("⚠") || line.includes("↷")) cls = styles.lineWarn;
  else if (line.includes("→")) cls = styles.lineVisit;

  return (
    <span className={`${styles.line} ${cls}`}>
      {line}
      {"\n"}
    </span>
  );
}
