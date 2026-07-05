import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Message } from '../../../types';
import { ReasoningStepsComponent } from '../reasoning-steps/reasoning-steps.component';
import { SourcesGridComponent } from '../sources-grid/sources-grid.component';

@Component({
  selector: 'app-message-bubble',
  standalone: true,
  imports: [CommonModule, MatProgressSpinnerModule, ReasoningStepsComponent, SourcesGridComponent],
  template: `
    <div class="bubble-wrap" [class.user]="message.role === 'user'" [class.assistant]="message.role === 'assistant'">
      <div class="bubble">
        <app-reasoning-steps *ngIf="message.role === 'assistant'" [steps]="message.reasoning_steps ?? []" />
        <p class="content" [class.empty]="!message.content && message.isStreaming">
          {{ message.content }}
          <span *ngIf="message.isStreaming && !message.content" class="placeholder">Thinking…</span>
          <span *ngIf="message.isStreaming && message.content" class="cursor">█</span>
        </p>
        <app-sources-grid *ngIf="message.role === 'assistant'" [sources]="message.sources ?? []" />
      </div>
    </div>
  `,
  styles: [`
    .bubble-wrap { display: flex; margin-bottom: 16px; }
    .bubble-wrap.user { justify-content: flex-end; }
    .bubble-wrap.assistant { justify-content: flex-start; }
    .bubble { max-width: 80%; padding: 12px 16px; border-radius: 12px; }
    .user .bubble { background: #3f51b5; color: white; border-bottom-right-radius: 2px; }
    .assistant .bubble { background: #f5f5f5; color: rgba(0,0,0,0.87); border-bottom-left-radius: 2px; min-width: 200px; }
    .content { margin: 0; white-space: pre-wrap; word-break: break-word; font-size: 14px; line-height: 1.6; }
    .placeholder { opacity: 0.5; font-style: italic; }
    .cursor { animation: blink 1s step-end infinite; }
    @keyframes blink { 0%, 100% { opacity: 1 } 50% { opacity: 0 } }
  `],
})
export class MessageBubbleComponent {
  @Input() message!: Message;
}
