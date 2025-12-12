import { Component, OnInit } from '@angular/core';
import { ReporteService } from '../../../core/services/reporte.service';
import { AuthService } from '../../../core/services/auth.service';
import { Reporte, Categoria } from '../../../core/models/reporte.model';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { environment } from '../../../../environments/environment';  // ← IMPORTAR

@Component({
  selector: 'app-feed',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, DatePipe],
  templateUrl: './feed.component.html',
  styleUrls: ['./feed.component.css']
})
export class FeedComponent implements OnInit {
  reportes: Reporte[] = [];
  categorias: Categoria[] = [];
  loading = false;
  error = '';

  // Filtros
  searchText = '';
  categoriaSeleccionada: number | null = null;
  estadoSeleccionado: string | null = null;

  // Paginación
  currentPage = 1;
  totalPages = 1;
  hasNext = false;
  hasPrev = false;

  isAuthenticated = false;

  constructor(
    private reporteService: ReporteService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.isAuthenticated = this.authService.isAuthenticated();
    this.loadCategorias();
    this.loadReportes();
  }

  loadCategorias(): void {
    this.reporteService.getCategorias().subscribe({
      next: (categorias) => {
        this.categorias = categorias;
      },
      error: (err) => {
        console.error('Error al cargar categorías', err);
      }
    });
  }

  loadReportes(): void {
  this.loading = true;
  this.error = '';

    const params: any = {
      page: this.currentPage,
      per_page: 12
    };

    if (this.categoriaSeleccionada) params.categoria_id = this.categoriaSeleccionada;
    if (this.estadoSeleccionado) params.estado = this.estadoSeleccionado;
    if (this.searchText) params.search = this.searchText;

    this.reporteService.getReportes(params).subscribe({
      next: (response) => {
       console.log("RESPUESTA BACK:", response);
      
      // ✅ AGREGAR ESTE LOG PARA VER CADA REPORTE
        response.items?.forEach((reporte: Reporte) => {
          console.log(`Reporte ${reporte.id}: usuario_dio_like =`, reporte.usuario_dio_like);
        });
      
        this.reportes = response.items || [];
        this.totalPages = response.pages || 1;
        this.hasNext = response.has_next;
        this.hasPrev = response.has_prev;
        this.loading = false;
      },
      error: () => {
        this.error = 'Error al cargar reportes';
        this.loading = false;
     }
   });
  }

  onSearch(): void {
    this.currentPage = 1;
    this.loadReportes();
  }

  onCategoriaChange(categoriaId: number | null): void {
    this.categoriaSeleccionada = categoriaId;
    this.currentPage = 1;
    this.loadReportes();
  }

  onEstadoChange(estado: string | null): void {
    this.estadoSeleccionado = estado;
    this.currentPage = 1;
    this.loadReportes();
  }

  clearFilters(): void {
    this.searchText = '';
    this.categoriaSeleccionada = null;
    this.estadoSeleccionado = null;
    this.currentPage = 1;
    this.loadReportes();
  }

  nextPage(): void {
    if (this.hasNext) {
      this.currentPage++;
      this.loadReportes();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  prevPage(): void {
    if (this.hasPrev) {
      this.currentPage--;
      this.loadReportes();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  toggleLike(reporte: Reporte): void {
    if (!this.isAuthenticated) return;

    this.reporteService.toggleLike(reporte.id).subscribe({
      next: (response) => {
        if (response && typeof response === 'object') {
          if ('usuario_dio_like' in response && 'total_likes' in response) {
            reporte.usuario_dio_like = response.usuario_dio_like;
            reporte.total_likes = response.total_likes;
          }
        } else {
          reporte.usuario_dio_like = !reporte.usuario_dio_like;
          reporte.total_likes += reporte.usuario_dio_like ? 1 : -1;
        }
      },
      error: (err) => console.error('Error al dar like:', err)
    });
  }

  getEstadoBadgeClass(estado: string): string {
    switch (estado) {
      case 'pendiente': return 'badge-pendiente';
      case 'en_proceso': return 'badge-proceso';
      case 'resuelto': return 'badge-resuelto';
      default: return '';
    }
  }

  getCategoriaImagen(categoriaNombre: string): string {
    if (!categoriaNombre) return 'assets/placeholder.jpg';
    const nombre = categoriaNombre.toLowerCase();

    if (nombre.includes('agua') || nombre.includes('fuga')) return 'assets/fugas.jpg';
    if (nombre.includes('luminaria') || nombre.includes('poste')) return 'assets/luminaria.jpg';
    if (nombre.includes('baches') || nombre.includes('pavimento')) return 'assets/bache.jpg';
    if (nombre.includes('basura') || nombre.includes('limpieza')) return 'assets/basura.jpg';

    return 'assets/placeholder.jpg';
  }

  limpiarNombre(nombre: string): string {
    if (!nombre) return '';
    return nombre
      .replace(/^water\s*/i, '')
      .replace(/^lightbulb\s*/i, '')
      .trim();
  }

  // ← CORREGIR ESTA FUNCIÓN
  getImagenUrl(nombreImagen?: string): string {
    if (!nombreImagen || nombreImagen.trim() === '') {
      return 'assets/placeholder.jpg';
    }

    // Construir URL completa: http://localhost:8000/uploads/reportes/nombre.jpg
    return `${environment.apiUrl}/uploads/reportes/${nombreImagen}`;
  }

  getEstadoTexto(estado: string): string {
    switch (estado) {
      case 'pendiente': return 'Pendiente';
      case 'en_proceso': return 'En Proceso';
      case 'resuelto': return 'Resuelto';
      default: return estado;
    }
  }
}