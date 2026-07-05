import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { PDF } from '../../../types';

@Component({
  selector: 'app-pdf-card',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatCheckboxModule, MatIconModule, MatButtonModule, MatTooltipModule],
  template: `
    <mat-card class="pdf-card" [class.selected]="selected">
      <mat-card-content>
        <div class="row">
          <mat-checkbox [checked]="selected" (change)="selectionChange.emit($event.checked)" color="primary" />
          <div class="info">
            <div class="name" [matTooltip]="pdf.name">{{ pdf.name }}</div>
            <div class="meta">{{ pdf.doc_count }} chunks · {{ pdf.page_count }} pages</div>
          </div>
          <button mat-icon-button color="warn" (click)="deleteClick.emit()" matTooltip="Delete PDF">
            <mat-icon>delete</mat-icon>
          </button>
        </div>
      </mat-card-content>
    </mat-card>
  `,
  styles: [`
    .pdf-card { margin-bottom: 8px; cursor: pointer;
      transition: box-shadow 0.2s; }
    .pdf-card.selected { background: rgba(63,81,181,0.08); }
    .row { display: flex; align-items: center; gap: 8px; }
    .info { flex: 1; min-width: 0; }
    .name { font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 13px; }
    .meta { font-size: 11px; color: rgba(0,0,0,0.54); margin-top: 2px; }
  `],
})
export class PdfCardComponent {
  @Input() pdf!: PDF;
  @Input() selected = false;
  @Output() selectionChange = new EventEmitter<boolean>();
  @Output() deleteClick = new EventEmitter<void>();
}
