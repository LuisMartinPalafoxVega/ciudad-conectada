import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { importProvidersFrom } from '@angular/core';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';


// Services y guards
import { AuthService } from './app/core/services/auth.service';
import { ReporteService } from './app/core/services/reporte.service';
import { AuthGuard, AdminGuard } from './app/core/guards/auth.guard';
import { AuthInterceptor } from './app/core/interceptors/auth.interceptor';
import { routes } from './app/app.routes';

bootstrapApplication(AppComponent, {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([AuthInterceptor])),
    importProvidersFrom(CommonModule, ReactiveFormsModule, FormsModule),
    AuthService,
    ReporteService,
    AuthGuard,
    AdminGuard
  ]
}).catch(err => console.error(err));
