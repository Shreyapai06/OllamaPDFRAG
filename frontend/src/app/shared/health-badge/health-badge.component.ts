import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ModelsService } from '../../core/api/models.service';
import { HealthResponse } from '../../types';

@Component({
  selector: 'app-health-badge',
  standalone: true,
  imports: [CommonModule, MatTooltipModule],
  template: `
    <span class="badge" [class.ok]="health?.groq_connected" [class.degraded]="!health?.groq_connected"
          [matTooltip]="tooltip">
      <span class="dot"></span>
      Groq: {{ health?.groq_connected ? 'OK' : 'Offline' }}
      <span *ngIf="health" class="stats"> · {{ health.total_pdfs }} PDFs · {{ health.total_chunks }} chunks</span>
    </span>
  `,
  styles: [`
    .badge { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; padding: 4px 10px;
             border-radius: 12px; background: rgba(255,255,255,0.15); }
    .dot { width: 8px; height: 8px; border-radius: 50%; }
    .ok .dot { background: #4caf50; }
    .degraded .dot { background: #f44336; }
    .stats { opacity: 0.75; font-size: 11px; }
  `],
})
export class HealthBadgeComponent implements OnInit {
  health: HealthResponse | null = null;
  tooltip = 'Checking connection…';

  constructor(private modelsService: ModelsService) {}

  ngOnInit(): void {
    this.modelsService.getHealth().subscribe({
      next: h => {
        this.health = h;
        this.tooltip = h.groq_connected ? 'Groq API connected' : 'Groq API unreachable';
      },
      error: () => { this.tooltip = 'Health check failed'; },
    });
  }
}
