import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { HealthBadgeComponent } from '../../shared/health-badge/health-badge.component';
import { ModelSelectorComponent } from '../../shared/model-selector/model-selector.component';
import { ChatStateService } from '../../core/state/chat-state.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, MatToolbarModule, MatButtonModule, MatIconModule, HealthBadgeComponent, ModelSelectorComponent],
  template: `
    <mat-toolbar color="primary" class="toolbar">
      <span class="title">RAG Assistant</span>
      <span class="spacer"></span>
      <app-model-selector />
      <button mat-icon-button matTooltip="Clear conversation" (click)="chatState.clearMessages()">
        <mat-icon>delete_sweep</mat-icon>
      </button>
      <app-health-badge />
    </mat-toolbar>
  `,
  styles: [`
    .toolbar { gap: 12px; }
    .title { font-size: 20px; font-weight: 500; letter-spacing: 0.5px; }
    .spacer { flex: 1; }
  `],
})
export class HeaderComponent {
  constructor(public chatState: ChatStateService) {}
}
