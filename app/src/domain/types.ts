export interface FileNode {
  name: string;
  url: string;
  is_dir: boolean;
  size: string | null;
  children: FileNode[];
}

export interface ExploreResponse {
  root_url: string;
  total_nodes: number;
  tree: FileNode[];
  truncated: boolean;
  log: string[];
}

export interface ExploreRequest {
  url: string;
}
