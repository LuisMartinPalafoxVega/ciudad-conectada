import { Component, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ReporteService } from '../../../core/services/reporte.service';
import { Reporte, ReportesPaginados } from '../../../core/models/reporte.model';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-mis-reportes',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './mis-reportes.component.html',
  styleUrls: ['./mis-reportes.component.css']
})
export class MisReportesComponent implements OnInit {
  reportes: Reporte[] = [];
  loading = true;
  currentPage = 1;
  totalPages = 1;

  constructor(
    private reporteService: ReporteService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.cargarReportes();
  }

  cargarReportes(page: number = 1): void {
    this.loading = true;
    this.reporteService.getMisReportes(page).subscribe({
      next: (data: ReportesPaginados) => {
        this.reportes = data.items;
        this.currentPage = data.page;
        this.totalPages = data.pages;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error al cargar reportes:', err);
        this.loading = false;
      }
    });
  }

  verDetalle(id: number): void {
    this.router.navigate(['/reportes', id]);
  }

  cambiarPagina(page: number): void {
    if (page >= 1 && page <= this.totalPages) {
      this.cargarReportes(page);
      window.scrollTo({ top: 0, behavior: 'smooth' });
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

  getImagenUrl(nombreImagen?: string): string {
    if (!nombreImagen || nombreImagen.trim() === '') {
      return 'assets/placeholder.jpg';
    }
    return `${environment.apiUrl}/uploads/reportes/${nombreImagen}`;
  }

  getPaginationArray(): number[] {
    const pages: number[] = [];
    const maxVisible = 5;
    
    if (this.totalPages <= maxVisible) {
      for (let i = 1; i <= this.totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (this.currentPage <= 3) {
        for (let i = 1; i <= maxVisible; i++) {
          pages.push(i);
        }
      } else if (this.currentPage >= this.totalPages - 2) {
        for (let i = this.totalPages - maxVisible + 1; i <= this.totalPages; i++) {
          pages.push(i);
        }
      } else {
        for (let i = this.currentPage - 2; i <= this.currentPage + 2; i++) {
          pages.push(i);
        }
      }
    }
    
    return pages;
  }

  get totalReportes(): number {
  return this.reportes.length;
}

get reportesPendientes(): number {
  return this.reportes.filter(r => r.estado === 'pendiente').length;
}

get reportesResueltos(): number {
  return this.reportes.filter(r => r.estado === 'resuelto').length;
}

get reportesEnProceso(): number {
  return this.reportes.filter(r => r.estado === 'en_proceso').length;
}

}
