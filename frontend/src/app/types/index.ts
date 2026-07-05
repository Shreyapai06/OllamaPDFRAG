export interface PDF {
  pdf_id: string;
  name: string;
  doc_count: number;
  page_count: number;
  upload_timestamp: string;
}

export interface Source {
  pdf_name: string | null;
  pdf_id: string | null;
  chunk_index: number;
  page_number: number | null;
  rrf_score: number | null;
}

export interface QueryResponse {
  answer: string;
  sources: Source[];
  reasoning_steps: string[];
  iterations_used: number;
  session_id: string;
  metadata: { model_used: string; chunks_retrieved: number };
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  reasoning_steps?: string[];
  isStreaming?: boolean;
}

export interface HealthResponse {
  status: string;
  groq_connected: boolean;
  total_pdfs: number;
  total_chunks: number;
}

export interface ModelInfo {
  name: string;
  note?: string;
}

export interface StreamParams {
  question: string;
  model: string;
  pdf_ids?: string[] | null;
  session_id?: string | null;
}

export interface QueryRequest {
  question: string;
  model: string;
  pdf_ids?: string[] | null;
  session_id?: string | null;
}

// SSE event union
export type SSEEvent =
  | { type: 'reasoning'; data: string }
  | { type: 'token'; data: string }
  | { type: 'done'; answer: string; sources: Source[] }
  | { type: 'session'; data: string }
  | { type: 'error'; data: string };
