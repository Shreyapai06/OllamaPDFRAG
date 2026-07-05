import { Component, Input, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatExpansionModule } from '@angular/material/expansion';
import { AgGridModule } from 'ag-grid-angular';
import { ColDef, GridReadyEvent, GridApi } from 'ag-grid-community';
import { Source } from '../../../types';

@Component({
  selector: 'app-sources-grid',
  standalone: true,
  imports: [CommonModule, MatExpansionModule, AgGridModule],
  template: `
    <mat-expansion-panel *ngIf="sources.length" class="sources-panel">
      <mat-expansion-panel-header>
        <mat-panel-title>Sources ({{ sources.length }})</mat-panel-title>
      </mat-expansion-panel-header>
      <div class="grid-wrapper ag-theme-material">
        <ag-grid-angular
          [rowData]="sources"
          [columnDefs]="columnDefs"
          [defaultColDef]="defaultColDef"
          [domLayout]="'autoHeight'"
          (gridReady)="onGridReady($event)"
        />
      </div>
    </mat-expansion-panel>
  `,
  styles: [`
    .sources-panel { margin-top: 8px; }
    .grid-wrapper { width: 100%; }
  `],
})
export class SourcesGridComponent implements OnChanges {
  @Input() sources: Source[] = [];

  private gridApi: GridApi | null = null;

  columnDefs: ColDef[] = [
    { field: 'pdf_name',    headerName: 'Document',  flex: 2, sortable: true, filter: true },
    { field: 'page_number', headerName: 'Page',      width: 80,  sortable: true },
    { field: 'chunk_index', headerName: 'Chunk',     width: 80,  sortable: true },
    {
      field: 'rrf_score',
      headerName: 'Score',
      width: 100,
      sortable: true,
      valueFormatter: p => p.value != null ? p.value.toFixed(4) : '-',
    },
  ];

  defaultColDef: ColDef = {
    resizable: true,
    suppressMovable: false,
  };

  onGridReady(params: GridReadyEvent): void {
    this.gridApi = params.api;
  }

  ngOnChanges(): void {
    this.gridApi?.setGridOption('rowData', this.sources);
  }
}
