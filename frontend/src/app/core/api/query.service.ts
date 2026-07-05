import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { QueryRequest, QueryResponse, SSEEvent, StreamParams } from '../../types';

@Injectable({ providedIn: 'root' })
export class QueryService {
  constructor(private api: ApiService) {}

  queryBlocking(body: QueryRequest): Observable<QueryResponse> {
    return this.api.http.post<QueryResponse>(`${this.api.base}/query`, body);
  }

  streamQuery(params: StreamParams): Observable<SSEEvent> {
    return new Observable(observer => {
      const url = this.buildStreamURL(params);
      const es = new EventSource(url);
      es.onmessage = (e: MessageEvent) => {
        try {
          observer.next(JSON.parse(e.data) as SSEEvent);
        } catch {
          // skip malformed events
        }
      };
      es.onerror = () => {
        observer.error('SSE connection error');
        es.close();
      };
      return () => es.close();
    });
  }

  getMessages(sessionId: string): Observable<unknown[]> {
    return this.api.http.get<unknown[]>(`${this.api.base}/query/sessions/${sessionId}/messages`);
  }

  private buildStreamURL(params: StreamParams): string {
    const p = new URLSearchParams();
    p.set('question', params.question);
    p.set('model', params.model);
    if (params.session_id) p.set('session_id', params.session_id);
    if (params.pdf_ids?.length) {
      params.pdf_ids.forEach(id => p.append('pdf_ids', id));
    }
    return `${this.api.base}/query/stream?${p.toString()}`;
  }
}
