import { Component, OnInit, AfterViewInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import * as L from 'leaflet';
import { ReporteService } from '../../../core/services/reporte.service';
import { Categoria } from '../../../core/models/reporte.model';

@Component({
  selector: 'app-nuevo-reporte',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './nuevo-reporte.component.html',
  styleUrls: ['./nuevo-reporte.component.css']
})
export class NuevoReporteComponent implements OnInit, AfterViewInit {
  reporteForm: FormGroup;
  categorias: Categoria[] = [];
  loading = false;
  error = '';

  map: L.Map | null = null;
  marker: L.Marker | null = null;

  imagenPreview: string | null = null;
  imagenFile: File | null = null;

  constructor(
    private fb: FormBuilder,
    private reporteService: ReporteService,
    private router: Router
  ) {
    this.reporteForm = this.fb.group({
      titulo: ['', [Validators.required, Validators.maxLength(200)]],
      descripcion: ['', [Validators.required, Validators.maxLength(1000)]],
      categoria_id: ['', Validators.required],
      latitud: ['', Validators.required],
      longitud: ['', Validators.required],
      direccion_referencia: ['', Validators.maxLength(300)]
    });
  }

  ngOnInit(): void {
    this.loadCategorias();
  }

  ngAfterViewInit(): void {
    this.initMap();
  }

  /** 🔹 Cargar categorías desde el servicio */
  loadCategorias(): void {
    this.reporteService.getCategorias().subscribe({
      next: (categorias) => {
        this.categorias = categorias || [];
      },
      error: (err) => {
        console.error('Error al cargar categorías', err);
      }
    });
  }

  /** 🔹 Inicializa el mapa Leaflet */
  initMap(): void {
    this.map = L.map('map').setView([19.4326, -99.1332], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(this.map);

    this.map.on('click', (e: L.LeafletMouseEvent) => {
      this.setLocation(e.latlng.lat, e.latlng.lng);
    });
  }

  /** 🔹 Usa la ubicación actual del usuario */
  useMyLocation(): void {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          this.setLocation(lat, lng);
          this.map?.setView([lat, lng], 15);
        },
        () => {
          alert('No se pudo obtener tu ubicación. Marca manualmente en el mapa.');
        }
      );
    } else {
      alert('Tu navegador no soporta geolocalización');
    }
  }

  /** 🔹 Establece marcador en el mapa y actualiza el formulario */
  setLocation(lat: number, lng: number): void {
    if (this.marker && this.map) {
      this.map.removeLayer(this.marker);
    }

    if (this.map) {
      this.marker = L.marker([lat, lng]).addTo(this.map);
    }

    this.reporteForm.patchValue({
      latitud: lat.toFixed(6),
      longitud: lng.toFixed(6)
    });
  }

  /** 🔹 Procesa la imagen seleccionada */
  onImageSelected(event: Event): void {
    const target = event.target as HTMLInputElement;
    if (!target.files || target.files.length === 0) return;

    const file = target.files[0];

    // Validar tamaño máximo 5MB
    if (file.size > 5 * 1024 * 1024) {
      alert('La imagen no debe superar 5MB');
      return;
    }

    // Validar tipo
    if (!['image/jpeg', 'image/png', 'image/jpg'].includes(file.type)) {
      alert('Solo se permiten imágenes JPG y PNG');
      return;
    }

    this.imagenFile = file;

    // Crear vista previa
    const reader = new FileReader();
    reader.onload = (e: any) => {
      this.imagenPreview = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  /** 🔹 Elimina imagen seleccionada */
  removeImage(): void {
    this.imagenFile = null;
    this.imagenPreview = null;
  }

  async verificarDuplicado(): Promise<boolean> {
  const formData = new FormData();
  formData.append('titulo', this.reporteForm.value.titulo);
  formData.append('descripcion', this.reporteForm.value.descripcion);
  formData.append('latitud', this.reporteForm.value.latitud);
  formData.append('longitud', this.reporteForm.value.longitud);
  formData.append('categoria_id', this.reporteForm.value.categoria_id);

  return new Promise((resolve) => {
    this.reporteService.verificarDuplicado(formData).subscribe({
      next: (resultado) => {
        if (resultado.es_duplicado) {
          const reportes = resultado.reportes_similares
            .map((r: any) => `• ${r.titulo} (${r.similitud}% similar)\n  ${r.razon}`)
            .join('\n\n');
          
          const confirmar = confirm(
            `⚠️ POSIBLE DUPLICADO\n\n` +
            `Similitud: ${resultado.similitud}%\n\n` +
            `Reportes similares:\n${reportes}\n\n` +
            `¿Deseas crear el reporte de todas formas?`
          );
          
          resolve(!confirmar); // true = cancelar, false = continuar
        } else {
          resolve(false); // No es duplicado, continuar
        }
      },
      error: () => {
        resolve(false); // Si falla la verificación, permitir crear
      }
    });
  });
}
  /** 🔹 Envía el formulario */
 async onSubmit(): Promise<void> {
  if (this.reporteForm.invalid) {
    Object.keys(this.reporteForm.controls).forEach(key => {
      this.reporteForm.get(key)?.markAsTouched();
    });
    return;
  }

  // ✅ VERIFICAR DUPLICADO CON IA
  const cancelar = await this.verificarDuplicado();
  if (cancelar) {
    return; // Usuario canceló
  }

  this.loading = true;
  this.error = '';

  const reporteData = {
    ...this.reporteForm.value,
    imagen: this.imagenFile
  };

  this.reporteService.createReporte(reporteData).subscribe({
    next: () => {
      alert('✅ Reporte creado exitosamente');
      this.router.navigate(['/feed']);
    },
    error: (err) => {
      this.error = err.error?.error || 'Error al crear reporte';
      this.loading = false;
    }
  });
}

  // 🔹 Getters para validación
  get titulo() { return this.reporteForm.get('titulo'); }
  get descripcion() { return this.reporteForm.get('descripcion'); }
  get categoria_id() { return this.reporteForm.get('categoria_id'); }
  get latitud() { return this.reporteForm.get('latitud'); }
  get longitud() { return this.reporteForm.get('longitud'); }
}
