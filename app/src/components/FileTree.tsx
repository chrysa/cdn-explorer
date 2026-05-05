import { useState } from "react";
import type { FileNode } from "@/domain/types";
import { buildDownloadUrl } from "@/api/client";
import { ChevronRight, ChevronDown, Folder, File, Download } from "lucide-react";
import styles from "./FileTree.module.css";

interface Props {
  nodes: FileNode[];
  selected: Set<string>;
  onToggle: (url: string) => void;
}

interface NodeProps {
  node: FileNode;
  selected: Set<string>;
  onToggle: (url: string) => void;
  depth: number;
}

function FileNodeRow({ node, selected, onToggle, depth }: NodeProps) {
  const [open, setOpen] = useState(false);
  const isChecked = selected.has(node.url);

  return (
    <li className={styles.node} style={{ paddingLeft: `${depth * 16}px` }}>
      <div className={styles.row}>
        {node.is_dir ? (
          <button className={styles.chevron} onClick={() => setOpen((v) => !v)} aria-label="toggle">
            {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          </button>
        ) : (
          <span className={styles.chevronPlaceholder} />
        )}

        <span className={styles.icon}>
          {node.is_dir ? <Folder size={14} /> : <File size={14} />}
        </span>

        {!node.is_dir && (
          <input
            type="checkbox"
            checked={isChecked}
            onChange={() => onToggle(node.url)}
            aria-label={`Select ${node.name}`}
          />
        )}

        <span className={styles.name}>{node.name}</span>

        {!node.is_dir && (
          <a
            href={buildDownloadUrl(node.url)}
            download={node.name}
            className={styles.downloadBtn}
            aria-label={`Download ${node.name}`}
          >
            <Download size={12} />
          </a>
        )}
      </div>

      {node.is_dir && open && node.children.length > 0 && (
        <ul className={styles.list}>
          {node.children.map((child) => (
            <FileNodeRow
              key={child.url}
              node={child}
              selected={selected}
              onToggle={onToggle}
              depth={depth + 1}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

export function FileTree({ nodes, selected, onToggle }: Props) {
  if (nodes.length === 0) {
    return <p className={styles.empty}>No files found at this URL.</p>;
  }

  return (
    <ul className={styles.list}>
      {nodes.map((node) => (
        <FileNodeRow key={node.url} node={node} selected={selected} onToggle={onToggle} depth={0} />
      ))}
    </ul>
  );
}
