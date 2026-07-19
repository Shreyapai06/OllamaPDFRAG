import { Component } from '@angular/core';
import { MatSidenavModule } from '@angular/material/sidenav';
import { HeaderComponent } from './features/header/header.component';
import { SidebarComponent } from './features/sidebar/sidebar.component';
import { ChatComponent } from './features/chat/chat.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [MatSidenavModule, HeaderComponent, SidebarComponent, ChatComponent],
  template: `
    <div class="shell">
      <app-header />
      <mat-sidenav-container class="sidenav-container">
        <mat-sidenav mode="side" opened class="sidenav">
          <app-sidebar />
        </mat-sidenav>
        <mat-sidenav-content class="main-content">
          <app-chat />
        </mat-sidenav-content>
      </mat-sidenav-container>
    </div>
  `,
  styles: [`
    .shell { display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
    .sidenav-container { flex: 1; min-height: 0; }
    .sidenav { width: 280px; border-right: 1px solid rgba(0,0,0,0.12); overflow-y: auto; }
    app-chat { display: flex; flex-direction: column; height: 100%; }
  `],
})
export class AppComponent {}
