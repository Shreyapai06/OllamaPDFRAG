import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { PdfService } from '../../../core/api/pdf.service';

@Component({
  selector: 'app-pdf-upload',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatButtonModule, MatProgressBarModule],
  template: `
    <div class="drop-zone"
         [class.drag-over]="isDragOver"
         (dragover)="onDragOver($event)"
         (dragleave)="isDragOver = false"
         (drop)="onDrop($event)"
         (click)="fileInput.click()">
      <mat-icon>upload_file</mat-icon>
      <span>Drop PDF or click to upload</span>
      <input #fileInput type="file" accept=".pdf" hidden (change)="onFileChange($event)" />
    </div>
    <mat-progress-bar *ngIf="progress !== null" mode="determinate" [value]="progress" />
    <div *ngIf="error" class="error">{{ error }}</div>
  `,
  styles: [`
    .drop-zone { border: 2px dashed rgba(0,0,0,0.25); border-radius: 8px; padding: 16px;
                 display: flex; flex-direction: column; align-items: center; gap: 8px;
                 cursor: pointer; text-align: center; font-size: 13px; color: rgba(0,0,0,0.54);
                 transition: border-color 0.2s, background 0.2s; margin-bottom: 8px; }
    .drop-zone:hover, .drop-zone.drag-over { border-color: #3f51b5; background: rgba(63,81,181,0.05); }
    .error { color: #f44336; font-size: 12px; margin-top: 4px; }
  `],
})
export class PdfUploadComponent {
  @Output() uploaded = new EventEmitter<void>();

  isDragOver = false;
  progress: number | null = null;
  error: string | null = null;

  constructor(private pdfService: PdfService) {}

  onDragOver(e: DragEvent): void {
    e.preventDefault();
    this.isDragOver = true;
  }

  onDrop(e: DragEvent): void {
    e.preventDefault();
    this.isDragOver = false;
    const file = e.dataTransfer?.files[0];
    if (file?.type === 'application/pdf') this.upload(file);
    else this.error = 'Only PDF files are supported';
  }

  onFileChange(e: Event): void {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (file) this.upload(file);
  }

  private upload(file: File): void {
    this.error = null;
    this.progress = 0;
    this.pdfService.uploadPDF(file).subscribe({
      next: pct => { this.progress = pct; },
      error: () => {
        this.error = 'Upload failed. Please try again.';
        this.progress = null;
      },
      complete: () => {
        this.progress = null;
        this.uploaded.emit();
      },
    });
  }
}
