import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import * as L from 'leaflet';
import 'leaflet.heat/dist/leaflet-heat.js';
import { MapaService } from '../../../core/services/mapa.service';
import { ReporteService } from '../../../core/services/reporte.service';
import { Categoria } from '../../../core/models/reporte.model';

declare module 'leaflet' {
  function heatLayer(latlngs: any[], options?: any): any;
}

@Component({
  selector: 'app-mapa-calor',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './mapa-calor.component.html',
  styleUrls: ['./mapa-calor.component.css']
})
export class MapaCalorComponent implements OnInit, OnDestroy {
  map: L.Map | null = null;
  heatLayer: any = null;
  markersLayer: L.LayerGroup | null = null;
  
  categorias: Categoria[] = [];
  categoriaSeleccionada: number | null = null;
  estadoSeleccionado: string | null = null;
  
  modoVista: 'heatmap' | 'markers' | 'clusters' = 'heatmap';
  
  loading = false;
  totalReportes = 0;
  
  estadisticasZona: any = null;
  mostrandoEstadisticas = false;

  constructor(
    private mapaService: MapaService,
    private reporteService: ReporteService
  ) {}

  ngOnInit(): void {
    this.initMap();
    this.cargarCategorias();
    this.cargarDatosHeatmap();
  }

  ngOnDestroy(): void {
    if (this.map) {
      this.map.remove();
      this.map = null;
    }
  }

  initMap(): void {
    // Centrar en México (ajusta según tu ubicación)
    this.map = L.map('mapa-calor-container').setView([25.8, -109.08], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(this.map);

    this.markersLayer = L.layerGroup().addTo(this.map);

    // Evento para seleccionar zona
    this.map.on('click', (e: L.LeafletMouseEvent) => {
      this.mostrarEstadisticasZona(e.latlng);
    });
  }

  cargarCategorias(): void {
    this.reporteService.getCategorias().subscribe({
      next: (categorias) => {
        this.categorias = categorias;
      },
      error: (err) => console.error('Error al cargar categorías:', err)
    });
  }

  cargarDatosHeatmap(): void {
    this.loading = true;

    const filtros: any = {};
    if (this.categoriaSeleccionada) {
      filtros.categoria_id = this.categoriaSeleccionada;
    }
    if (this.estadoSeleccionado) {
      filtros.estado = this.estadoSeleccionado;
    }

    this.mapaService.obtenerDatosHeatmap(filtros).subscribe({
      next: (datos) => {
        this.totalReportes = datos.total;
        
        if (this.modoVista === 'heatmap') {
          this.mostrarHeatmap(datos.heatmap);
        } else if (this.modoVista === 'markers') {
          this.mostrarMarcadores(datos.markers);
        } else {
          this.mostrarClusters(datos.markers);
        }
        
        this.loading = false;
      },
      error: (err) => {
        console.error('Error al cargar datos:', err);
        this.loading = false;
      }
    });
  }

  mostrarHeatmap(datos: any[]): void {
    // Limpiar capas anteriores
    if (this.heatLayer) {
      this.map?.removeLayer(this.heatLayer);
    }
    if (this.markersLayer) {
      this.markersLayer.clearLayers();
    }

    // Crear heatmap
    const heatData = datos.map(d => [d.lat, d.lng, d.intensity]);
    
    this.heatLayer = (L as any).heatLayer(heatData, {
      radius: 25,
      blur: 15,
      maxZoom: 17,
      max: 1.0,
      gradient: {
        0.0: 'blue',
        0.5: 'yellow',
        0.7: 'orange',
        1.0: 'red'
      }
    }).addTo(this.map!);
  }

  mostrarMarcadores(datos: any[]): void {
    // Limpiar capas anteriores
    if (this.heatLayer) {
      this.map?.removeLayer(this.heatLayer);
      this.heatLayer = null;
    }
    if (this.markersLayer) {
      this.markersLayer.clearLayers();
    }

    // Crear marcadores personalizados por estado
    datos.forEach(marker => {
      const color = this.getColorEstado(marker.estado);
      
      const icon = L.divIcon({
        className: 'custom-marker',
        html: `
          <div style="
            background-color: ${color};
            width: 30px;
            height: 30px;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
          ">
            ${marker.categoria_icono}
          </div>
        `,
        iconSize: [30, 30],
        iconAnchor: [15, 15]
      });

      const leafletMarker = L.marker([marker.lat, marker.lng], { icon })
        .bindPopup(`
          <div style="min-width: 200px;">
            <h3 style="margin: 0 0 10px 0; color: #1e3c72;">${marker.titulo}</h3>
            <p style="margin: 5px 0;">
              <strong>Categoría:</strong> ${marker.categoria_icono} ${marker.categoria}
            </p>
            <p style="margin: 5px 0;">
              <strong>Estado:</strong> 
              <span style="
                padding: 3px 8px;
                background: ${color};
                color: white;
                border-radius: 4px;
                font-size: 12px;
              ">
                ${this.getEstadoTexto(marker.estado)}
              </span>
            </p>
            <a href="/detalle-reporte/${marker.id}" style="
              display: inline-block;
              margin-top: 10px;
              padding: 6px 12px;
              background: #1e3c72;
              color: white;
              text-decoration: none;
              border-radius: 4px;
              font-size: 13px;
            ">
              Ver detalles →
            </a>
          </div>
        `);

      this.markersLayer?.addLayer(leafletMarker);
    });
  }

  mostrarClusters(datos: any[]): void {
    // Similar a mostrarMarcadores pero con agrupación
    // Requiere leaflet.markercluster
    this.mostrarMarcadores(datos);
  }

  mostrarEstadisticasZona(latlng: L.LatLng): void {
    const bounds = 0.01; // Aprox 1km de radio
    
    this.mapaService.obtenerEstadisticasZona({
      lat_min: latlng.lat - bounds,
      lat_max: latlng.lat + bounds,
      lng_min: latlng.lng - bounds,
      lng_max: latlng.lng + bounds
    }).subscribe({
      next: (stats) => {
        this.estadisticasZona = stats;
        this.mostrandoEstadisticas = true;
      },
      error: (err) => console.error('Error al cargar estadísticas:', err)
    });
  }

  cambiarModoVista(modo: 'heatmap' | 'markers' | 'clusters'): void {
    this.modoVista = modo;
    this.cargarDatosHeatmap();
  }

  aplicarFiltros(): void {
    this.cargarDatosHeatmap();
  }

  limpiarFiltros(): void {
    this.categoriaSeleccionada = null;
    this.estadoSeleccionado = null;
    this.cargarDatosHeatmap();
  }

  getColorEstado(estado: string): string {
    switch (estado) {
      case 'pendiente': return '#FF9800';
      case 'en_proceso': return '#2196F3';
      case 'resuelto': return '#4CAF50';
      default: return '#666';
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
}