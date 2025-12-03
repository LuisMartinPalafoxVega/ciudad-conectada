export interface Usuario {
  id: number;
  nombre: string;
  email: string;
  rol: 'ciudadano' | 'administrador';
  activo: boolean;
  fecha_registro: string;
  foto_url?: string; // ✅ Agregar este campo
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  nombre: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  usuario: Usuario;
}