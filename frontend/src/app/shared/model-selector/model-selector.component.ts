import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { ModelsService } from '../../core/api/models.service';
import { ChatStateService } from '../../core/state/chat-state.service';
import { ModelInfo } from '../../types';

@Component({
  selector: 'app-model-selector',
  standalone: true,
  imports: [CommonModule, FormsModule, MatSelectModule, MatFormFieldModule],
  template: `
    <mat-form-field appearance="outline" class="model-field">
      <mat-label>Model</mat-label>
      <mat-select [(ngModel)]="selectedModel" (ngModelChange)="onModelChange($event)">
        <mat-option *ngFor="let m of models" [value]="m.name">
          {{ m.name }}<span *ngIf="m.note" class="note"> — {{ m.note }}</span>
        </mat-option>
      </mat-select>
    </mat-form-field>
  `,
  styles: [`
    .model-field { width: 260px; }
    .note { font-size: 11px; opacity: 0.6; }
    mat-form-field { --mdc-outlined-text-field-label-text-color: white;
                     --mdc-outlined-text-field-outline-color: rgba(255,255,255,0.5); }
  `],
})
export class ModelSelectorComponent implements OnInit {
  models: ModelInfo[] = [];
  selectedModel = 'llama-3.3-70b-versatile';

  constructor(
    private modelsService: ModelsService,
    private chatState: ChatStateService,
  ) {}

  ngOnInit(): void {
    this.selectedModel = this.chatState.selectedModel$.value;
    this.modelsService.listModels().subscribe({
      next: res => { this.models = res.models; },
      error: () => {
        this.models = [{ name: 'llama-3.3-70b-versatile', note: 'Best reasoning' }];
      },
    });
  }

  onModelChange(model: string): void {
    this.chatState.selectedModel$.next(model);
  }
}
