import { Component } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-spinner',
  standalone: true,
  imports: [MatProgressSpinnerModule],
  template: `<mat-spinner diameter="24" />`,
  styles: [':host { display: inline-flex; align-items: center; }'],
})
export class SpinnerComponent {}
