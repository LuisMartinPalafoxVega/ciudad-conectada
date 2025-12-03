export interface Comentario {
  id: number;
  contenido: string;
  reporte_id: number;
  usuario_id: number;
  parent_id?: number;

  usuario: {
    id: number;
    nombre: string;
    email: string;
    foto_url?: string | null;  // ✅ AGREGAR
  };

  fecha_creacion: string;
  respuestas?: Comentario[];
}
