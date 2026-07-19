import { Injectable, NgZone } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { QueryRequest, QueryResponse, SSEEvent, StreamParams } from '../../types';

@Injectable({ providedIn: 'root' })
export class QueryService {
  constructor(private api: ApiService, private zone: NgZone) {}

  queryBlocking(body: QueryRequest): Observable<QueryResponse> {
    return this.api.http.post<QueryResponse>(`${this.api.base}/query`, body);
  }

  streamQuery(params: StreamParams): Observable<SSEEvent> {
    return new Observable(observer => {
      const url = this.buildStreamURL(params);
      const es = new EventSource(url);

      es.onmessage = (e: MessageEvent) => {
        // Run inside Angular zone so change detection fires on every token
        this.zone.run(() => {
          try {
            const event = JSON.parse(e.data) as SSEEvent;
            observer.next(event);
            // Server closes connection after "session" event — complete cleanly
            if (event.type === 'session') {
              es.close();
              observer.complete();
            }
          } catch {
            // skip malformed frames
          }
        });
      };

      // onerror fires on both real errors AND normal server-side close.
      // Only treat it as an error if the stream is still open (CONNECTING or OPEN).
      es.onerror = () => {
        this.zone.run(() => {
          if (es.readyState === EventSource.CLOSED) {
            // Normal end-of-stream close — complete rather than error
            observer.complete();
          } else {
            observer.error('SSE connection error');
          }
          es.close();
        });
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