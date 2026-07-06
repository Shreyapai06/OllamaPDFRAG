import { Injectable } from '@angular/core';
import { HttpEventType, HttpRequest } from '@angular/common/http';
import { Observable, map, filter } from 'rxjs';
import { ApiService } from './api.service';
import { PDF } from '../../types';

@Injectable({ providedIn: 'root' })
export class PdfService {
  constructor(private api: ApiService) {}

  listPDFs(): Observable<PDF[]> {
    return this.api.http.get<PDF[]>(`${this.api.base}/pdfs`);
  }

  uploadPDF(file: File): Observable<number> {
    const form = new FormData();
    form.append('file', file);
    const req = new HttpRequest('POST', `${this.api.base}/pdfs/upload`, form, {
      reportProgress: true,
    });
    return this.api.http.request(req).pipe(
      filter(e => e.type === HttpEventType.UploadProgress || e.type === HttpEventType.Response),
      map(e => {
        if (e.type === HttpEventType.UploadProgress && e.total) {
          return Math.round((100 * e.loaded) / e.total);
        }
        return 100;
      })
    );
  }

  deletePDF(pdfId: string): Observable<void> {
    return this.api.http.delete<void>(`${this.api.base}/pdfs/${pdfId}`);
  }
}
