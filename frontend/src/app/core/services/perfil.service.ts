import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { 
  Reporte, 
  ReportesPaginados, 
  CreateReporteRequest, 
  Categoria,
  Estadisticas 
} from '../models/reporte.model';

@Injectable({
  providedIn: 'root'
})
export class ReporteService {
  private apiUrl = `${environment.apiUrl}/reportes`;
  private adminUrl = `${environment.apiUrl}/admin`;

  constructor(private http: HttpClient) {}

  getReportes(params?: {
    page?: number;
    per_page?: number;
    categoria_id?: number;
    estado?: string;
    search?: string;
  }): Observable<ReportesPaginados> {
    let httpParams = new HttpParams();

    if (params) {
      Object.keys(params).forEach(key => {
        const value = (params as any)[key];
        if (value !== undefined && value !== null) {
          httpParams = httpParams.set(key, value.toString());
        }
      });
    }

    return this.http.get<ReportesPaginados>(this.apiUrl, { params: httpParams });
  }

  getReporte(id: number): Observable<Reporte> {
    return this.http.get<Reporte>(`${this.apiUrl}/${id}`);
  }

  createReporte(data: CreateReporteRequest): Observable<any> {
    const formData = new FormData();
    formData.append('titulo', data.titulo);
    formData.append('descripcion', data.descripcion);
    formData.append('categoria_id', data.categoria_id.toString());
    formData.append('latitud', data.latitud.toString());
    formData.append('longitud', data.longitud.toString());

    if (data.direccion_referencia) {
      formData.append('direccion_referencia', data.direccion_referencia);
    }

    if (data.imagen) {
      formData.append('imagen', data.imagen);
    }

    return this.http.post(`${this.apiUrl}`, formData);
  }

  // ← CORREGIR: cambiar de /mis-reportes a /mis-reportes/todos
  getMisReportes(page: number = 1): Observable<ReportesPaginados> {
    return this.http.get<ReportesPaginados>(`${this.apiUrl}/mis-reportes/todos`, {
      params: { page: page.toString() }
    });
  }

  toggleLike(id: number) {
    return this.http.post<any>(`${this.apiUrl}/${id}/like`, {});
  }

  // ← CORREGIR: cambiar de /categorias a /categorias/todas
  getCategorias(): Observable<Categoria[]> {
    return this.http.get<Categoria[]>(`${this.apiUrl}/categorias/todas`);
  }

  // Admin endpoints
  getAllReportesAdmin(params?: {
    page?: number;
    categoria_id?: number;
    estado?: string;
  }): Observable<ReportesPaginados> {
    let httpParams = new HttpParams();

    if (params) {
      Object.keys(params).forEach(key => {
        const value = (params as any)[key];
        if (value !== undefined && value !== null) {
          httpParams = httpParams.set(key, value.toString());
        }
      });
    }

    return this.http.get<ReportesPaginados>(`${this.adminUrl}/reportes`, { params: httpParams });
  }

  cambiarEstadoReporte(id: number, estado: string, comentario?: string): Observable<any> {
    return this.http.put(`${this.adminUrl}/reportes/${id}/estado`, { estado, comentario });
  }

  getEstadisticas(): Observable<Estadisticas> {
    return this.http.get<Estadisticas>(`${this.adminUrl}/estadisticas`);
  }

  getHistorialReporte(id: number): Observable<any> {
    return this.http.get(`${this.adminUrl}/reportes/${id}/historial`);
  }
}