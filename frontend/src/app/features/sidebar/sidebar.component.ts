import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDividerModule } from '@angular/material/divider';
import { PdfService } from '../../core/api/pdf.service';
import { ChatStateService } from '../../core/state/chat-state.service';
import { PDF } from '../../types';
import { PdfCardComponent } from './pdf-card/pdf-card.component';
import { PdfUploadComponent } from './pdf-upload/pdf-upload.component';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, MatDividerModule, PdfCardComponent, PdfUploadComponent],
  template: `
    <div class="sidebar-inner">
      <app-pdf-upload (uploaded)="loadPDFs()" />
      <mat-divider />
      <div class="pdf-list">
        <div *ngIf="loading" class="hint">Loading PDFs…</div>
        <div *ngIf="!loading && pdfs.length === 0" class="hint">No PDFs uploaded yet.</div>
        <app-pdf-card
          *ngFor="let pdf of pdfs"
          [pdf]="pdf"
          [selected]="chatState.isPdfSelected(pdf.pdf_id)"
          (selectionChange)="onSelection(pdf.pdf_id)"
          (deleteClick)="deletePDF(pdf.pdf_id)"
        />
      </div>
    </div>
  `,
  styles: [`
    .sidebar-inner { display: flex; flex-direction: column; gap: 12px; padding: 12px; height: 100%; box-sizing: border-box; }
    .pdf-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 0; margin-top: 8px; }
    .hint { font-size: 13px; color: rgba(0,0,0,0.45); text-align: center; padding: 16px 0; }
  `],
})
export class SidebarComponent implements OnInit {
  pdfs: PDF[] = [];
  loading = false;

  constructor(
    private pdfService: PdfService,
    public chatState: ChatStateService,
  ) {}

  ngOnInit(): void {
    this.loadPDFs();
  }

  loadPDFs(): void {
    this.loading = true;
    this.pdfService.listPDFs().subscribe({
      next: pdfs => { this.pdfs = pdfs; this.loading = false; },
      error: () => { this.loading = false; },
    });
  }

  onSelection(pdfId: string): void {
    this.chatState.togglePdfSelection(pdfId);
  }

  deletePDF(pdfId: string): void {
    this.pdfService.deletePDF(pdfId).subscribe({
      next: () => { this.loadPDFs(); },
    });
  }
}
