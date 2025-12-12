import { Routes } from '@angular/router';
import { LoginComponent } from './features/auth/login/login.component';
import { RegisterComponent } from './features/auth/register/register.component';
import { FeedComponent } from './features/reportes/feed/feed.component';
import { MapaCalorComponent } from './features/reportes/mapa-calor/mapa-calor.component';
import { NuevoReporteComponent } from './features/reportes/nuevo-reporte/nuevo-reporte.component';
import { DashboardComponent } from './features/admin/dashboard/dashboard.component';
import { AuthGuard, AdminGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },

  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },

  { path: 'feed', component: FeedComponent, canActivate: [AuthGuard] },

  { path: 'nuevo-reporte', component: NuevoReporteComponent, canActivate: [AuthGuard] },

  { 
    path: 'detalle-reporte/:id',
    loadComponent: () =>
      import('./features/reportes/detalle-reporte/detalle-reporte.component')
        .then(m => m.DetalleReporteComponent),
    canActivate: [AuthGuard]
  },

  {
    path: 'perfil',
    loadComponent: () =>
      import('./features/usuario/perfil/perfil.component')
        .then(m => m.PerfilComponent),
    canActivate: [AuthGuard]
  },

  {
    path: 'mis-reportes',
    loadComponent: () =>
      import('./features/reportes/mis-reportes/mis-reportes.component')
        .then(m => m.MisReportesComponent),
    canActivate: [AuthGuard]
  },

  // ✅ NUEVA RUTA: Mapa de Calor
  {
    path: 'mapa-calor',
    loadComponent: () =>
      import('./features/reportes/mapa-calor/mapa-calor.component')
        .then(m => m.MapaCalorComponent),
    canActivate: [AuthGuard]
  },

  { path: 'admin', component: DashboardComponent, canActivate: [AdminGuard] },

  { path: '**', redirectTo: 'login' }
];