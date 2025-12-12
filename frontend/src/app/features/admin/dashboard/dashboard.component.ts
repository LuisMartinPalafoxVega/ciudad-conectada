import { Component, OnInit } from '@angular/core';
import { ReporteService } from '../../../core/services/reporte.service';
import { Estadisticas, Reporte } from '../../../core/models/reporte.model';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  estadisticas: Estadisticas | null = null;
  reportes: Reporte[] = [];
  loading = true;
  error = '';

  estadoSeleccionado: string | null = null;
  currentPage = 1;

  constructor(private reporteService: ReporteService) {}

  ngOnInit(): void {
    this.loadEstadisticas();
    this.loadReportes();
  }

  loadEstadisticas(): void {
    this.reporteService.getEstadisticas().subscribe({
      next: (stats) => {
        console.log('Estadísticas cargadas:', stats);
        this.estadisticas = stats;
      },
      error: (err) => {
        console.error('Error al cargar estadísticas', err);
        this.error = 'Error al cargar estadísticas';
      }
    });
  }
  ordenSeleccionado: string | null = null;

loadReportes(): void {
  this.loading = true;
  const params: any = {
    page: this.currentPage,
    per_page: 1000
  };

  if (this.estadoSeleccionado) {
    params.estado = this.estadoSeleccionado;
  }

  if (this.ordenSeleccionado) {
    params.orden = this.ordenSeleccionado;
  }

  this.reporteService.getAllReportesAdmin(params).subscribe({
    next: (response) => {
      this.reportes = response.items || [];
      this.loading = false;
    },
    error: (err) => {
      this.error = 'Error al cargar reportes';
      this.loading = false;
      this.reportes = [];
    }
  });
  }





  filterByEstado(estado: string | null): void {
    this.estadoSeleccionado = estado;
    this.currentPage = 1;
    this.loadReportes();
  }

  cambiarEstado(reporte: Reporte, nuevoEstado: string): void {
    const estadoTexto = this.getEstadoTexto(nuevoEstado);
    
    if (confirm(`¿Cambiar estado de "${reporte.titulo}" a "${estadoTexto}"?`)) {
      this.reporteService.cambiarEstadoReporte(reporte.id, nuevoEstado).subscribe({
        next: () => {
          // Actualizar el estado localmente
          reporte.estado = nuevoEstado as any;
          
          // Recargar estadísticas
          this.loadEstadisticas();
          
          alert('Estado actualizado exitosamente');
        },
        error: (err) => {
          console.error('Error al actualizar estado:', err);
          alert('Error al actualizar el estado del reporte');
        }
      });
    } else {
      // Si cancela, revertir el select al valor original
      const selectElement = event?.target as HTMLSelectElement;
      if (selectElement) {
        selectElement.value = reporte.estado;
      }
    }
  }

  getEstadoBadgeClass(estado: string): string {
    switch (estado) {
      case 'pendiente': return 'badge-pendiente';
      case 'en_proceso': return 'badge-proceso';
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

  confirmarEliminacion(reporte: Reporte): void {
  const confirmado = confirm(`¿Seguro que deseas eliminar el reporte #${reporte.id}?`);
  if (!confirmado) return;

  this.reporteService.eliminarReporte(reporte.id).subscribe({
    next: () => {
      // recarga lista desde el backend
      this.loadReportes();
    },
    error: () => {
      this.error = 'No se pudo eliminar el reporte';
    }
  });
}


}