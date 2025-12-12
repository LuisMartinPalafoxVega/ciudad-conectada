import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface HeatmapData {
  lat: number;
  lng: number;
  intensity: number;
}

export interface MarkerData {
  id: number;
  lat: number;
  lng: number;
  titulo: string;
  estado: string;
  categoria: string;
  categoria_color: string;
  categoria_icono: string;
  fecha: string;
}

export interface HeatmapResponse {
  heatmap: HeatmapData[];
  markers: MarkerData[];
  total: number;
}

export interface EstadisticasZona {
  total: number;
  pendientes: number;
  en_proceso: number;
  resueltos: number;
  por_categoria: {
    nombre: string;
    color: string;
    total: number;
  }[];
}

export interface TimelineData {
  timeline: {
    fecha: string;
    total: number;
  }[];
}

export interface ZonaCritica {
  total: number;
  pendientes: number;
  lat: number;
  lng: number;
}

@Injectable({
  providedIn: 'root'
})
export class MapaService {
  private apiUrl = `${environment.apiUrl}/mapa-calor`;

  constructor(private http: HttpClient) {}

  obtenerDatosHeatmap(filtros?: {
    categoria_id?: number;
    estado?: string;
    fecha_inicio?: string;
    fecha_fin?: string;
  }): Observable<HeatmapResponse> {
    let params = new HttpParams();
    
    if (filtros) {
      Object.keys(filtros).forEach(key => {
        const value = (filtros as any)[key];
        if (value !== undefined && value !== null) {
          params = params.set(key, value.toString());
        }
      });
    }

    return this.http.get<HeatmapResponse>(`${this.apiUrl}/heatmap`, { params });
  }

  obtenerEstadisticasZona(bounds: {
    lat_min: number;
    lat_max: number;
    lng_min: number;
    lng_max: number;
  }): Observable<EstadisticasZona> {
    let params = new HttpParams()
      .set('lat_min', bounds.lat_min.toString())
      .set('lat_max', bounds.lat_max.toString())
      .set('lng_min', bounds.lng_min.toString())
      .set('lng_max', bounds.lng_max.toString());

    return this.http.get<EstadisticasZona>(`${this.apiUrl}/estadisticas-zona`, { params });
  }

  obtenerTimeline(dias: number = 30): Observable<TimelineData> {
    const params = new HttpParams().set('dias', dias.toString());
    return this.http.get<TimelineData>(`${this.apiUrl}/timeline`, { params });
  }

  obtenerZonasCriticas(limite: number = 5): Observable<{ zonas_criticas: ZonaCritica[] }> {
    const params = new HttpParams().set('limite', limite.toString());
    return this.http.get<{ zonas_criticas: ZonaCritica[] }>(`${this.apiUrl}/zonas-criticas`, { params });
  }
}