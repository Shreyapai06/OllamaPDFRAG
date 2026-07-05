import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { HealthResponse, ModelInfo } from '../../types';

@Injectable({ providedIn: 'root' })
export class ModelsService {
  constructor(private api: ApiService) {}

  listModels(): Observable<{ models: ModelInfo[] }> {
    return this.api.http.get<{ models: ModelInfo[] }>(`${this.api.base}/models`);
  }

  getHealth(): Observable<HealthResponse> {
    return this.api.http.get<HealthResponse>(`${this.api.base}/health`);
  }
}
