import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class VehicleService {
  // Base API URL - adjust if your server runs under a prefix
  private baseUrl = '/api';

  constructor(private http: HttpClient) {}

  // Fetch available model identifiers from backend
  getAvailableModels(): Observable<string[]> {
    return this.http.get<string[]>(`${this.baseUrl}/models`);
  }

  // Detect on image: send FormData with file + model
  detectVehicle(file: File, model: string): Observable<any> {
    const fd = new FormData();
    fd.append('file', file, file.name);
    fd.append('model', model);
    return this.http.post<any>(`${this.baseUrl}/detect-image`, fd);
  }

  // Detect on video: send FormData with file + model
  detectVideo(file: File, model: string): Observable<any> {
    const fd = new FormData();
    fd.append('file', file, file.name);
    fd.append('model', model);
    return this.http.post<any>(`${this.baseUrl}/detect-video`, fd);
  }

  // Train models: accepts either FormData (uploaded dataset) or JSON payload { model, dataset }
  trainModels(payload: any): Observable<any> {
    if (payload instanceof FormData) {
      return this.http.post<any>(`${this.baseUrl}/train`, payload);
    }
    return this.http.post<any>(`${this.baseUrl}/train`, payload, {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' })
    });
  }

  // Compare models: payload { models: string[], dataset?: string }
  compareModels(payload: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/compare`, payload, {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' })
    });
  }

  // Download processed file by name - returns blob
  downloadProcessedFile(name: string): Observable<Blob> {
    const params = `?name=${encodeURIComponent(name)}`;
    return this.http.get(`${this.baseUrl}/download${params}`, { responseType: 'blob' });
  }
}
