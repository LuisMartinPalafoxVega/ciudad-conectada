import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, AbstractControl, ValidationErrors } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../../../core/services/auth.service';
import { Usuario } from '../../../core/models/usuario.model';
import { environment } from '../../../../environments/environment';


interface UsuarioDetalle extends Usuario {
  total_reportes?: number;
  reportes_pendientes?: number;
  reportes_resueltos?: number;
  foto_url?: string;
}

@Component({
  selector: 'app-perfil',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './perfil.component.html',
  styleUrls: ['./perfil.component.css']
})
export class PerfilComponent implements OnInit {
  loading = true;
  activeTab: 'info' | 'password' = 'info';
  
  infoForm: FormGroup;
  passwordForm: FormGroup;
  
  actualizandoInfo = false;
  cambiandoPassword = false;
  uploadingPhoto = false;
  
  successMessage: string | null = null;
  errorMessage: string | null = null;

  usuario: UsuarioDetalle = {
    id: 0,
    nombre: '',
    email: '',
    rol: 'ciudadano',
    activo: true,
    fecha_registro: '',
    total_reportes: 0,
    reportes_pendientes: 0,
    reportes_resueltos: 0,
    foto_url: undefined
  };

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private http: HttpClient
  ) {
    this.infoForm = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(3)]],
      email: [{value: '', disabled: true}]
    });

    this.passwordForm = this.fb.group({
      passwordActual: ['', Validators.required],
      nuevaPassword: ['', [Validators.required, Validators.minLength(8), this.passwordValidator]],
      confirmarPassword: ['', Validators.required]
    }, { validators: this.passwordMatchValidator });
  }

  ngOnInit() {
    this.cargarPerfil();
  }

  cargarPerfil() {
  this.loading = true;
  
  const userStr = localStorage.getItem('currentUser');
  if (userStr) {
    const user = JSON.parse(userStr);

    // 🔥 AQUI SE REPARA EL PROBLEMA 🔥
    if (user.foto_url && !user.foto_url.startsWith('http')) {
      user.foto_url = `${environment.apiUrl}${user.foto_url}`;
    }

    this.usuario = {
      ...user,
      total_reportes: 15,
      reportes_pendientes: 3,
      reportes_resueltos: 12
    };

    this.infoForm.patchValue({
      nombre: this.usuario.nombre,
      email: this.usuario.email
    });
  }
  
  this.loading = false;
}


  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;

    const file = input.files[0];

    // Validar tipo de archivo
    if (!file.type.startsWith('image/')) {
      this.showError('Por favor selecciona una imagen válida');
      return;
    }

    // Validar tamaño (máximo 5MB)
    if (file.size > 5 * 1024 * 1024) {
      this.showError('La imagen no debe superar 5MB');
      return;
    }

    this.uploadPhoto(file);
  }

  uploadPhoto(file: File) {
  this.uploadingPhoto = true;

  const formData = new FormData();
  formData.append('file', file);

  this.http.post<{mensaje: string, url: string}>(
    `${environment.apiUrl}/usuarios/avatar`,
    formData
  ).subscribe({
    next: (response) => {
      // Construir la URL completa de la foto
      const fotoUrl = `${environment.apiUrl}${response.url}`;
      
      // Actualizar la foto en el componente
      this.usuario.foto_url = fotoUrl;
      
      // ✅ Actualizar usuario completo
      const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
      currentUser.foto_url = fotoUrl;
      
      // ✅ Usar el método público del AuthService
      this.authService.updateCurrentUser(currentUser);
      
      this.uploadingPhoto = false;
      this.showSuccess('Foto de perfil actualizada correctamente');
      
      console.log('✅ Foto actualizada:', fotoUrl);
    },
    error: (error) => {
      console.error('❌ Error al subir foto:', error);
      this.uploadingPhoto = false;
      this.showError('Error al subir la foto. Intenta de nuevo.');
    }
  });
}

  actualizarInfo() {
    if (this.infoForm.invalid) return;

    this.actualizandoInfo = true;
    
    setTimeout(() => {
      this.usuario.nombre = this.infoForm.value.nombre;
      
      const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
      currentUser.nombre = this.usuario.nombre;
      localStorage.setItem('currentUser', JSON.stringify(currentUser));
      
      this.actualizandoInfo = false;
      this.showSuccess('Información actualizada correctamente');
    }, 1500);
  }

  cambiarPassword() {
    if (this.passwordForm.invalid) return;

    this.cambiandoPassword = true;
    
    setTimeout(() => {
      this.cambiandoPassword = false;
      this.passwordForm.reset();
      this.showSuccess('Contraseña cambiada exitosamente');
    }, 1500);
  }

  cancelarEdicion() {
    this.infoForm.patchValue({
      nombre: this.usuario.nombre,
      email: this.usuario.email
    });
  }

  cancelarPassword() {
    this.passwordForm.reset();
  }

  showSuccess(message: string) {
    this.successMessage = message;
    setTimeout(() => this.successMessage = null, 5000);
  }

  showError(message: string) {
    this.errorMessage = message;
    setTimeout(() => this.errorMessage = null, 5000);
  }

  passwordValidator(control: AbstractControl): ValidationErrors | null {
    const value = control.value;
    if (!value) return null;

    const hasUpperCase = /[A-Z]/.test(value);
    const hasNumber = /[0-9]/.test(value);
    const hasSpecialChar = /[@$!%*?&]/.test(value);

    const valid = hasUpperCase && hasNumber && hasSpecialChar;
    return valid ? null : { passwordStrength: true };
  }

  passwordMatchValidator(group: AbstractControl): ValidationErrors | null {
    const password = group.get('nuevaPassword')?.value;
    const confirm = group.get('confirmarPassword')?.value;
    
    return password === confirm ? null : { passwordMismatch: true };
  }

  get nombre() { return this.infoForm.get('nombre'); }
  get passwordActual() { return this.passwordForm.get('passwordActual'); }
  get nuevaPassword() { return this.passwordForm.get('nuevaPassword'); }
  get confirmarPassword() { return this.passwordForm.get('confirmarPassword'); }
}