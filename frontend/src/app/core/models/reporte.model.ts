import { Usuario } from './usuario.model';

export interface Categoria {
  id: number;
  nombre: string;
  icono: string;
  color: string;
}

export interface Reporte {
  id: number;
  titulo: string;
  descripcion: string;
  categoria: Categoria;
  latitud: number;
  longitud: number;
  direccion_referencia?: string;
  imagen_url?: string;
  estado: 'pendiente' | 'en_proceso' | 'resuelto';
  fecha_creacion: string;
  fecha_actualizacion: string;
  usuario: Usuario;
  total_likes: number;
  usuario_dio_like?: boolean;
}

export interface ReportesPaginados {
  items: Reporte[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface CreateReporteRequest {
  titulo: string;
  descripcion: string;
  categoria_id: number;
  latitud: number;
  longitud: number;
  direccion_referencia?: string;
  imagen?: File;
}

export interface Estadisticas {
  total_reportes: number;
  pendientes: number;
  en_proceso: number;
  resueltos: number;
  activos: number;
  porcentaje_resueltos: number;
  reportes_por_categoria: Array<{ nombre: string; total: number }>;
}

export interface Comentario {
  id: number;
  reporte_id: number;
  usuario_id: number;
  usuario: {
    id: number;
    nombre: string;
    email: string;
  };
  contenido: string;
  fecha_creacion: string;
}