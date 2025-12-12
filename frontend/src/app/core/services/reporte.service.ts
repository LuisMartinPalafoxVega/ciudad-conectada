import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpHeaders} from '@angular/common/http';
import { Observable } from 'rxjs';
import { Comentario } from '../models/comentario.model';
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

  // ✓ corregido (evita doble /api/api)
  private apiUrl = `${environment.apiUrl}/reportes`;
  private adminUrl = `${environment.apiUrl}/admin`;

  constructor(private http: HttpClient) {}

  // ============================================
  // REPORTES
  // ============================================

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

    return this.http.get<ReportesPaginados>(`${this.apiUrl}`, { params: httpParams });
  }

  getReporte(id: number): Observable<Reporte> {
    return this.http.get<Reporte>(`${this.apiUrl}/detalle/${id}`);
  }

  createReporte(data: CreateReporteRequest, usuario_id?: number): Observable<any> {
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

    // Si se proporciona usuario_id, usarlo, si no, el backend usa el current_user
    if (usuario_id) {
      formData.append('usuario_id', usuario_id.toString());
    }
    
    return this.http.post(`${this.apiUrl}`, formData);
  }

  updateReporte(id: number, formData: FormData): Observable<Reporte> {
    return this.http.put<Reporte>(`${this.apiUrl}/${id}`, formData);
  }

  deleteReporte(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }

  getMisReportes(page: number = 1): Observable<ReportesPaginados> {
    return this.http.get<ReportesPaginados>(`${this.apiUrl}/mis-reportes/todos`, {
      params: { page: page.toString() }
    });
  }

  toggleLike(id: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${id}/like`, {});
  }

  getCategorias(): Observable<Categoria[]> {
    return this.http.get<Categoria[]>(`${environment.apiUrl}/categorias/todas`);
  }

  // ============================================
  // COMENTARIOS
  // ============================================

  getComentarios(reporteId: number): Observable<Comentario[]> {
    return this.http.get<Comentario[]>(`${this.apiUrl}/${reporteId}/comentarios`);
  }

  createComentario(reporteId: number, contenido: string, parentId: number | null = null) {
  return this.http.post<any>(
    `${this.apiUrl}/${reporteId}/comentarios`,
    { contenido, parent_id: parentId }
  );
}


  deleteComentario(reporteId: number, comentarioId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${reporteId}/comentarios/${comentarioId}`);
  }

  verificarDuplicado(formData: FormData): Observable<any> {
  return this.http.post(`${this.apiUrl}/verificar-duplicado`, formData);
}

  // ============================================
  // ADMIN ENDPOINTS
  // ============================================

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

  eliminarReporte(id: number): Observable<void> {
  return this.http.delete<void>(`${this.adminUrl}/reportes/${id}`);
  }


  getHistorialReporte(id: number): Observable<any> {
    return this.http.get(`${this.adminUrl}/reportes/${id}/historial`);
  }
  updateComentario(reporteId: number, comentarioId: number, contenido: string): Observable<any> {
  return this.http.put(
    `${this.apiUrl}/${reporteId}/comentarios/${comentarioId}`,
    { contenido }
  );

  

  
}

}