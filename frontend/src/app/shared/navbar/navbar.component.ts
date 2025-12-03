import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { Usuario } from '../../core/models/usuario.model';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit {
  currentUser: Usuario | null = null;
  isMenuOpen = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {

    // ===============================
    // 1. Cargar usuario desde storage
    // ===============================
    const userFromStorage = localStorage.getItem('currentUser');

    if (userFromStorage) {
      const parsedUser = JSON.parse(userFromStorage);

      // ⭐ FIX FOTO AQUÍ
      if (parsedUser.foto_url && !parsedUser.foto_url.startsWith('http')) {
        parsedUser.foto_url = environment.apiUrl + parsedUser.foto_url;
      }

      this.currentUser = parsedUser;
      console.log('NAVBAR: usuario desde storage →', this.currentUser);
    }

    // ===============================
    // 2. Escuchar cambios (logout / new foto)
    // ===============================
    this.authService.currentUser$.subscribe(user => {

      // ⭐ FIX FOTO AQUÍ TAMBIÉN
      if (user?.foto_url && !user.foto_url.startsWith('http')) {
        user.foto_url = environment.apiUrl + user.foto_url;
      }

      this.currentUser = user;
      console.log('NAVBAR: usuario actualizado →', user);
    });
  }

  toggleMenu(): void {
    this.isMenuOpen = !this.isMenuOpen;
  }

  logout(): void {
    if (confirm('¿Estás seguro de que deseas cerrar sesión?')) {
      this.authService.logout();
      this.isMenuOpen = false;
    }
  }

  isAdmin(): boolean {
    return this.currentUser?.rol === 'administrador';
  }

  closeMenu(): void {
    this.isMenuOpen = false;
  }

  getInitials(nombre: string): string {
    return nombre
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  }
}
