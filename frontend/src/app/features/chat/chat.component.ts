import { Component, ElementRef, ViewChild, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { ChatStateService } from '../../core/state/chat-state.service';
import { MessageBubbleComponent } from './message-bubble/message-bubble.component';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    CommonModule, FormsModule,
    MatInputModule, MatButtonModule, MatIconModule, MatFormFieldModule,
    MessageBubbleComponent,
  ],
  template: `
    <div class="chat-container">
      <div #scrollContainer class="messages">
        <div *ngIf="(chatState.messages$ | async)?.length === 0" class="empty-state">
          <p>Upload a PDF and ask a question to get started.</p>
        </div>
        <app-message-bubble
          *ngFor="let msg of (chatState.messages$ | async)"
          [message]="msg"
        />
      </div>
      <div class="input-row">
        <mat-form-field appearance="outline" class="question-field">
          <mat-label>Ask a question…</mat-label>
          <input matInput [(ngModel)]="question" (keydown.enter)="submit()"
                 [disabled]="(chatState.isStreaming$ | async) === true"
                 placeholder="What is this document about?" />
        </mat-form-field>
        <button mat-fab color="primary"
                [disabled]="!question.trim() || (chatState.isStreaming$ | async)"
                (click)="submit()">
          <mat-icon>send</mat-icon>
        </button>
      </div>
    </div>
  `,
  styles: [`
    .chat-container { display: flex; flex-direction: column; height: 100%; overflow: hidden; }
    .messages { flex: 1; overflow-y: auto; padding: 16px; }
    .empty-state { display: flex; align-items: center; justify-content: center; height: 100%;
                   color: rgba(0,0,0,0.38); font-size: 14px; }
    .input-row { display: flex; align-items: center; gap: 12px; padding: 12px 16px;
                 border-top: 1px solid rgba(0,0,0,0.1); }
    .question-field { flex: 1; }
  `],
})
export class ChatComponent implements AfterViewChecked {
  @ViewChild('scrollContainer') private scrollContainer!: ElementRef<HTMLDivElement>;

  question = '';
  private shouldScroll = false;

  constructor(public chatState: ChatStateService) {}

  ngAfterViewChecked(): void {
    // Only auto-scroll while streaming or right after the user submits — not on every tick
    if (this.shouldScroll || this.chatState.isStreaming$.value) {
      const el = this.scrollContainer?.nativeElement;
      if (el) el.scrollTop = el.scrollHeight;
      this.shouldScroll = false;
    }
  }

  submit(): void {
    const q = this.question.trim();
    if (!q || this.chatState.isStreaming$.value) return;
    this.question = '';
    this.shouldScroll = true;
    this.chatState.submitQuestion(q);
  }
}
