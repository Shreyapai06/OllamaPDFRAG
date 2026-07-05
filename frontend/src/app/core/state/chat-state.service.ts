import { Injectable, OnDestroy } from '@angular/core';
import { BehaviorSubject, Subscription } from 'rxjs';
import { Message, Source, SSEEvent } from '../../types';

function uuidv4(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
  });
}
import { QueryService } from '../api/query.service';

@Injectable({ providedIn: 'root' })
export class ChatStateService implements OnDestroy {
  readonly messages$ = new BehaviorSubject<Message[]>([]);
  readonly sessionId$ = new BehaviorSubject<string | null>(null);
  readonly selectedModel$ = new BehaviorSubject<string>('llama-3.3-70b-versatile');
  readonly selectedPdfIds$ = new BehaviorSubject<string[] | null>(null);
  readonly isStreaming$ = new BehaviorSubject<boolean>(false);

  private streamSub: Subscription | null = null;

  constructor(private queryService: QueryService) {}

  ngOnDestroy(): void {
    this.streamSub?.unsubscribe();
  }

  submitQuestion(question: string): void {
    if (this.isStreaming$.value) return;

    const userMsg: Message = { id: uuidv4(), role: 'user', content: question };
    const assistantMsg: Message = {
      id: uuidv4(),
      role: 'assistant',
      content: '',
      sources: [],
      reasoning_steps: [],
      isStreaming: true,
    };

    this.messages$.next([...this.messages$.value, userMsg, assistantMsg]);
    this.isStreaming$.next(true);

    this.streamSub = this.queryService.streamQuery({
      question,
      model: this.selectedModel$.value,
      pdf_ids: this.selectedPdfIds$.value,
      session_id: this.sessionId$.value,
    }).subscribe({
      next: (event: SSEEvent) => this.handleEvent(event),
      error: () => this.finalizeLastMessage(),
      complete: () => this.finalizeLastMessage(),
    });
  }

  private handleEvent(event: SSEEvent): void {
    const msgs = [...this.messages$.value];
    const last = { ...msgs[msgs.length - 1] };

    switch (event.type) {
      case 'reasoning':
        last.reasoning_steps = [...(last.reasoning_steps ?? []), event.data];
        break;
      case 'token':
        last.content += event.data;
        break;
      case 'done':
        last.content = event.answer;
        last.sources = event.sources as Source[];
        last.isStreaming = false;
        this.isStreaming$.next(false);
        break;
      case 'session':
        this.sessionId$.next(event.data);
        return;
      case 'error':
        last.content += `\n\n[Error: ${event.data}]`;
        last.isStreaming = false;
        this.isStreaming$.next(false);
        break;
    }

    msgs[msgs.length - 1] = last;
    this.messages$.next(msgs);
  }

  private finalizeLastMessage(): void {
    const msgs = [...this.messages$.value];
    if (msgs.length) {
      const last = { ...msgs[msgs.length - 1], isStreaming: false };
      msgs[msgs.length - 1] = last;
      this.messages$.next(msgs);
    }
    this.isStreaming$.next(false);
    this.streamSub = null;
  }

  clearMessages(): void {
    this.streamSub?.unsubscribe();
    this.streamSub = null;
    this.messages$.next([]);
    this.sessionId$.next(null);
    this.isStreaming$.next(false);
  }

  togglePdfSelection(pdfId: string): void {
    const current = this.selectedPdfIds$.value ?? [];
    if (current.includes(pdfId)) {
      const next = current.filter(id => id !== pdfId);
      this.selectedPdfIds$.next(next.length ? next : null);
    } else {
      this.selectedPdfIds$.next([...current, pdfId]);
    }
  }

  isPdfSelected(pdfId: string): boolean {
    return this.selectedPdfIds$.value?.includes(pdfId) ?? false;
  }
}
