import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-reasoning-steps',
  standalone: true,
  imports: [CommonModule, MatExpansionModule, MatIconModule],
  template: `
    <mat-expansion-panel *ngIf="steps.length" class="reasoning-panel">
      <mat-expansion-panel-header>
        <mat-panel-title>
          <mat-icon class="think-icon">psychology</mat-icon>
          Reasoning ({{ steps.length }} step{{ steps.length !== 1 ? 's' : '' }})
        </mat-panel-title>
      </mat-expansion-panel-header>
      <ol class="steps">
        <li *ngFor="let step of steps" class="step">{{ step }}</li>
      </ol>
    </mat-expansion-panel>
  `,
  styles: [`
    .reasoning-panel { margin-bottom: 8px; background: #f9f9f9; }
    .think-icon { font-size: 18px; margin-right: 6px; vertical-align: middle; }
    .steps { margin: 0; padding-left: 20px; }
    .step { font-size: 13px; color: rgba(0,0,0,0.65); padding: 4px 0; }
  `],
})
export class ReasoningStepsComponent {
  @Input() steps: string[] = [];
}
