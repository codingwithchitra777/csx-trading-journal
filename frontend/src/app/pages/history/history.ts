import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './history.html'
})
export class HistoryComponent implements OnInit {
  readonly apiService = inject(ApiService);

  readonly trades = signal<any[]>([]);
  readonly loadingTrades = signal<boolean>(false);
  
  readonly tickersList = signal<any[]>([]);
  filterTicker = '';

  ngOnInit() {
    this.loadTickers();
    this.loadTrades();
  }

  loadTickers() {
    this.apiService.getPrices().subscribe({
      next: (data) => {
        this.tickersList.set(data);
      }
    });
  }

  loadTrades() {
    this.loadingTrades.set(true);
    const tickerParam = this.filterTicker ? this.filterTicker : undefined;
    this.apiService.getTrades(tickerParam).subscribe({
      next: (data) => {
        this.trades.set(data);
        this.loadingTrades.set(false);
      },
      error: () => this.loadingTrades.set(false)
    });
  }
  
  onFilterChange() {
    this.loadTrades();
  }
}
