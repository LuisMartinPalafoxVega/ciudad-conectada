import { Component, OnInit, AfterViewInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { ReporteService } from '../../../core/services/reporte.service';
import { Reporte } from '../../../core/models/reporte.model';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../../environments/environment';
import { Comentario } from '../../../core/models/comentario.model';
import * as L from 'leaflet';

@Component({
  standalone: true,
  selector: 'app-detalle-reporte',
  templateUrl: './detalle-reporte.component.html',
  styleUrls: ['./detalle-reporte.component.css'],
  imports: [CommonModule, RouterModule, FormsModule]
})
export class DetalleReporteComponent implements OnInit, AfterViewInit, OnDestroy {
  
  reporte?: Reporte;
  comentarios: Comentario[] = [];
  loading = true;
  error = '';

  nuevoComentario = '';
  enviandoComentario = false;
  respondiendoA: number | null = null;
  textoRespuesta = '';
  editandoComentario: number | null = null;
  contenidoEditado = '';

  editandoTitulo = false;
  editandoDescripcion = false;
  tituloEditado = '';
  descripcionEditada = '';
  

  map: L.Map | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private reporteService: ReporteService
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.params['id']);
    this.cargarReporte(id);
    this.cargarComentarios(id);
  }

  ngAfterViewInit(): void {
    setTimeout(() => {
      if (this.reporte) {
        this.initMap();
      }
    }, 500);
  }

  ngOnDestroy(): void {
    if (this.map) {
      this.map.remove();
      this.map = null;
    }
  }

  // =====================================================
  //  RESTAURO initMap() (se había borrado accidentalmente)
  // =====================================================
  initMap(): void {
    if (!this.reporte || this.map) return;

    const mapElement = document.getElementById('detalle-map');
    if (!mapElement) return;

    this.map = L.map('detalle-map', {
      dragging: false,
      scrollWheelZoom: false,
      doubleClickZoom: false,
      touchZoom: false,
      zoomControl: false
    }).setView([this.reporte.latitud, this.reporte.longitud], 15);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(this.map);

    L.marker([this.reporte.latitud, this.reporte.longitud]).addTo(this.map);
  }

  // =====================================================
  //  CARGAR REPORTE + FIX FOTO USUARIO DEL REPORTE
  // =====================================================
  cargarReporte(id: number): void {
    this.loading = true;

    this.reporteService.getReporte(id).subscribe({
      next: (reporte) => {

        // FIX FOTO del autor del reporte
        if (reporte.usuario && (reporte.usuario as any).foto_url) {
          const foto = (reporte.usuario as any).foto_url;
          if (!foto.startsWith('http')) {
            (reporte.usuario as any).foto_url = environment.apiUrl + foto;
          }
        }

        this.reporte = reporte;
        this.loading = false;

        setTimeout(() => this.initMap(), 100);
      },
      error: () => {
        this.error = 'Error al cargar el reporte';
        this.loading = false;
      }
    });
  }

  // =====================================================
  //  CARGAR COMENTARIOS + FIX DE FOTOS
  // =====================================================
  cargarComentarios(reporteId: number): void {
  console.log('📥 Cargando comentarios para reporte:', reporteId);
  
  this.reporteService.getComentarios(reporteId).subscribe({
    next: (comentarios) => {
      console.log('📦 Comentarios recibidos del backend:', comentarios.length);
      
      // Normalizar fotos (agregar URL completa si falta)
      comentarios.forEach((c: any) => {
        if (c.usuario?.foto_url && !c.usuario.foto_url.startsWith('http')) {
          c.usuario.foto_url = environment.apiUrl + c.usuario.foto_url;
        }
      });

      // ✅ CONSTRUIR ÁRBOL DE COMENTARIOS
      // Crear un mapa de todos los comentarios por ID
      const mapa: Record<number, any> = {};
      comentarios.forEach((c: any) => {
        mapa[c.id] = { ...c, respuestas: [] };
      });

      // Separar comentarios principales y asignar respuestas
      const raiz: any[] = [];
      comentarios.forEach((c: any) => {
        if (c.parent_id) {
          // Es una respuesta, agregarlo al padre
          const padre = mapa[c.parent_id];
          if (padre) {
            padre.respuestas.push(mapa[c.id]);
          }
        } else {
          // Es un comentario principal
          raiz.push(mapa[c.id]);
        }
      });

      // Ordenar comentarios principales (más recientes primero)
      raiz.sort((a: any, b: any) =>
        new Date(b.fecha_creacion).getTime() - new Date(a.fecha_creacion).getTime()
      );

      // Ordenar respuestas de cada comentario (más antiguas primero)
      raiz.forEach((comentario: any) => {
        if (comentario.respuestas && comentario.respuestas.length > 0) {
          comentario.respuestas.sort((a: any, b: any) =>
            new Date(a.fecha_creacion).getTime() - new Date(b.fecha_creacion).getTime()
          );
        }
      });

      this.comentarios = raiz;
      
      console.log('✅ Comentarios organizados:', this.comentarios.length, 'principales');
      this.comentarios.forEach(c => {
        console.log(`  - ${c.id}: ${c.respuestas?.length || 0} respuestas`);
      });
    },
    error: (err) => {
      console.error('❌ Error al cargar comentarios:', err);
    }
  });
}


  // ============================================
  // EDICIÓN DE REPORTE
  // ============================================
  puedeEditarReporte(): boolean {
    if (!this.reporte) return false;
    const usuarioActual = JSON.parse(localStorage.getItem('currentUser') || '{}');
    return this.reporte.usuario.id === usuarioActual.id;
  }

  activarEdicionTitulo(): void {
    if (!this.reporte) return;
    this.tituloEditado = this.reporte.titulo;
    this.editandoTitulo = true;
  }

  activarEdicionDescripcion(): void {
    if (!this.reporte) return;
    this.descripcionEditada = this.reporte.descripcion;
    this.editandoDescripcion = true;
  }

  guardarTitulo(): void {
    if (!this.reporte || !this.tituloEditado.trim()) return;

    const formData = new FormData();
    formData.append('titulo', this.tituloEditado);

    this.reporteService.updateReporte(this.reporte.id, formData).subscribe({
      next: (reporteActualizado) => {
        this.reporte!.titulo = reporteActualizado.titulo;
        this.editandoTitulo = false;
      },
      error: (err) => {
        console.error('Error al actualizar título:', err);
        alert('Error al actualizar el título');
      }
    });
  }

  guardarDescripcion(): void {
    if (!this.reporte || !this.descripcionEditada.trim()) return;

    const formData = new FormData();
    formData.append('descripcion', this.descripcionEditada);

    this.reporteService.updateReporte(this.reporte.id, formData).subscribe({
      next: (reporteActualizado) => {
        this.reporte!.descripcion = reporteActualizado.descripcion;
        this.editandoDescripcion = false;
      },
      error: (err) => {
        console.error('Error al actualizar descripción:', err);
        alert('Error al actualizar la descripción');
      }
    });
  }

  cancelarEdicion(): void {
    this.editandoTitulo = false;
    this.editandoDescripcion = false;
  }

  eliminarReporte(): void {
    if (!this.reporte) return;

    if (!confirm('¿Estás seguro de que deseas eliminar este reporte? Esta acción no se puede deshacer.')) {
      return;
    }

    this.reporteService.deleteReporte(this.reporte.id).subscribe({
      next: () => {
        alert('Reporte eliminado exitosamente');
        this.router.navigate(['/feed']);
      },
      error: (err) => {
        console.error('Error al eliminar reporte:', err);
        alert('Error al eliminar el reporte');
      }
    });
  }

  // ============================================
  // COMENTARIOS Y RESPUESTAS
  // ============================================
  agregarComentario(): void {
  if (!this.reporte || !this.nuevoComentario.trim()) return;

  this.enviandoComentario = true;
  this.reporteService.createComentario(this.reporte.id, this.nuevoComentario).subscribe({
    next: (comentario) => {
      console.log('Comentario creado:', comentario);
      
      // Recargar todos los comentarios
      this.cargarComentarios(this.reporte!.id);
      
      this.nuevoComentario = '';
      this.enviandoComentario = false;
    },
    error: (err) => {
      console.error('Error al crear comentario:', err);
      alert('Error al publicar comentario');
      this.enviandoComentario = false;
    }
  });
}

  activarRespuesta(comentarioId: number): void {
    this.respondiendoA = comentarioId;
    this.textoRespuesta = '';
  }

  enviarRespuesta(parentId: number): void {
  if (!this.reporte || !this.textoRespuesta.trim()) return;

  // ✅ Evitar doble clic
  if (this.enviandoComentario) return;
  
  this.enviandoComentario = true;

  console.log('🔵 Enviando respuesta al comentario:', parentId);
  console.log('🔵 Contenido:', this.textoRespuesta);

  this.reporteService.createComentario(
    this.reporte.id, 
    this.textoRespuesta,
    parentId
  ).subscribe({
    next: (respuesta) => {
      console.log('✅ Respuesta creada:', respuesta);
      
      // ✅ SOLO recargar comentarios, NO agregar manualmente
      this.cargarComentarios(this.reporte!.id);
      
      this.cancelarRespuesta();
      this.enviandoComentario = false;
    },
    error: (err) => {
      console.error('❌ Error al crear respuesta:', err);
      alert('Error al publicar respuesta');
      this.enviandoComentario = false;
    }
  });
}


  cancelarRespuesta(): void {
    this.respondiendoA = null;
    this.textoRespuesta = '';
  }

  eliminarComentario(comentarioId: number): void {
  if (!this.reporte || !confirm('¿Eliminar este comentario?')) return;

  this.reporteService.deleteComentario(this.reporte.id, comentarioId).subscribe({
    next: () => {
      console.log('Comentario eliminado:', comentarioId);
      
      // Recargar todos los comentarios para mantener la estructura
      this.cargarComentarios(this.reporte!.id);
    },
    error: (err) => {
      console.error('Error al eliminar comentario:', err);
      alert('Error al eliminar comentario');
    }
  });
}

  puedeEliminarComentario(comentario: Comentario): boolean {
    const usuarioActual = JSON.parse(localStorage.getItem('currentUser') || '{}');
    return comentario.usuario_id === usuarioActual.id;
  }

  getNombreParaRespuesta(parentId: number): string {
    const comentarioPadre = this.comentarios.find(c => c.id === parentId);
    return comentarioPadre ? comentarioPadre.usuario.nombre : '';
  }

  getInitials(nombre: string): string {
    return nombre
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  }

  // Contar todos los comentarios incluyendo respuestas
getTotalComentarios(): number {
  let total = this.comentarios.length;
  
  this.comentarios.forEach(comentario => {
    if (comentario.respuestas && comentario.respuestas.length > 0) {
      total += comentario.respuestas.length;
    }
  });
  
  return total;
}

// Verificar si puede editar un comentario
puedeEditarComentario(comentario: Comentario): boolean {
  const usuarioActual = JSON.parse(localStorage.getItem('currentUser') || '{}');
  return comentario.usuario_id === usuarioActual.id;
}

// Activar edición de comentario
activarEdicionComentario(comentario: Comentario): void {
  this.editandoComentario = comentario.id;
  this.contenidoEditado = comentario.contenido;
}

// Cancelar edición de comentario
cancelarEdicionComentario(): void {
  this.editandoComentario = null;
  this.contenidoEditado = '';
}

// Guardar edición de comentario
guardarEdicionComentario(comentarioId: number): void {
  if (!this.reporte || !this.contenidoEditado.trim()) return;

  this.reporteService.updateComentario(
    this.reporte.id, 
    comentarioId, 
    this.contenidoEditado
  ).subscribe({
    next: () => {
      // Recargar comentarios para ver los cambios
      this.cargarComentarios(this.reporte!.id);
      this.cancelarEdicionComentario();
    },
    error: (err) => {
      console.error('Error al editar comentario:', err);
      alert('Error al editar el comentario');
    }
  });
}

  // ============================================
  // OTRAS FUNCIONES
  // ============================================
  toggleLike(): void {
    if (!this.reporte) return;
    
    this.reporteService.toggleLike(this.reporte.id).subscribe({
      next: (response) => {
        if (this.reporte && response) {
          this.reporte.usuario_dio_like = response.usuario_dio_like;
          this.reporte.total_likes = response.total_likes;
        }
      },
      error: (err) => console.error('Error al dar like:', err)
    });
  }

  verEnMapa(): void {
    if (this.reporte) {
      const url = `https://www.google.com/maps?q=${this.reporte.latitud},${this.reporte.longitud}`;
      window.open(url, '_blank');
    }
  }

  getBadgeClass(estado: string): string {
    switch (estado) {
      case 'pendiente': return 'badge-pendiente';
      case 'en_proceso': return 'badge-en_proceso';
      case 'resuelto': return 'badge-resuelto';
      default: return '';
    }
  }

  getEstadoTexto(estado: string): string {
    switch (estado) {
      case 'pendiente': return 'Pendiente';
      case 'en_proceso': return 'En Proceso';
      case 'resuelto': return 'Resuelto';
      default: return estado;
    }
  }

 getFotoUsuario(comentario: Comentario): string | null {
  if (!comentario.usuario) return null;

  if (comentario.usuario.foto_url) {

    // Si la foto no trae http, se le agrega el dominio del backend
    if (!comentario.usuario.foto_url.startsWith('http')) {
      return environment.apiUrl + comentario.usuario.foto_url;
    }

    return comentario.usuario.foto_url;
  }

  return null; // No tiene foto → usar iniciales
}

getImagenUrl(nombreImagen?: string): string {
  if (!nombreImagen || nombreImagen.trim() === '') {
    return 'assets/placeholder.jpg'; // o lo que uses por defecto
  }

  return `${environment.apiUrl}/uploads/reportes/${nombreImagen}`;
}


}

