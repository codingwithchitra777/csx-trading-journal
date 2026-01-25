# csx-trading-journal

## Features

### Lowest Price First Matching
The trading journal uses **Lowest Price First** matching for all sell orders. This means:
- When you sell stock, it matches with your **lowest priced purchases first**
- Profit/Loss is maximized by selling the cheapest shares first
- Higher priced purchases remain in your position

### Commands

- `/buy$ABC 7300 100` - Buy 100 shares of ABC at 7300 riel
- `/sell$ABC 7400 100` - Sell 100 shares at 7400 riel (shows profit with lowest price matching + matched orders)
- `/stock ABC` - **NEW!** View detailed stock visualization with lowest price allocation (graphical chart)
- `/position ABC` - View current position summary (graphical chart)
- `/portfolio` - View your entire portfolio
- `/price$ABC` - Get latest price for ABC
- `/show_all` - View all market prices
- `/top_orders` - Top 5 most profitable orders
- `/top_tickers` - Top 5 most profitable tickers

### Visual Features

#### 📊 Stock Details Chart (`/stock ABC`)
Beautiful visualization showing:
- **Buy Orders Panel**: Lowest price purchases first
  - Shows sequence number, quantity, price
  - Displays remaining quantity for each lot
  - 🟢 Green dot = shares remaining, ⚪ White dot = fully sold
- **Sell Orders Panel**: All sales with matched information
  - Shows which buy orders were matched (lowest price first)
  - Displays profit/loss for each sale
  - Indented list of matched buy orders
- **Summary Section**: Complete position overview
  - Total bought, sold, and remaining quantities
  - Total realized profit/loss

#### 📈 Position Chart (`/position ABC`)
Shows your current position:
- Total bought and sold quantities
- Remaining quantity and percentage sold
- Number of open lots
- Details of remaining lots (up to 3)

### Lowest Price First Example

**Scenario:**
1. Buy 100 shares @ 7000 riel (lowest price)
2. Buy 100 shares @ 7100 riel
3. Buy 100 shares @ 7200 riel (highest price)
4. Sell 150 shares @ 7500 riel

**Lowest Price Matching:**
- Matches 100 shares from purchase #1 (7000) → Profit: 100 × (7500 - 7000) = 50,000 riel
- Matches 50 shares from purchase #2 (7100) → Profit: 50 × (7500 - 7100) = 20,000 riel
- **Total Profit: 70,000 riel** (before commissions)
- Purchase #3 (7200) remains in your position (50 shares from #2, 100 shares from #3)

**Bot Response:**
```
✅ SELL confirmed | Seq #4 | P/L: +70,000 riel
📦 Matched: #1 (100@7,000), #2 (50@7,100)
```

### Stock Details Command

Use `/stock ABC` to get a beautiful chart showing:
- All buy orders (most recent first) with remaining quantities
- All sell orders with matched buy orders
- Realized profit/loss for each sale
- Complete summary of your position

**Example Output:**
```
📋 ABC - STOCK DETAILS (LIFO)

📥 BUY ORDERS (Most Recent First):
🟢 #3: 100@7,200 | Remaining: 0
🟢 #2: 100@7,100 | Remaining: 50
🟢 #1: 100@7,000 | Remaining: 100

📤 SELL ORDERS:
#4: 150@7,500 | P/L: +50,000
  ↳ Matched #3: 100@7,200
  ↳ Matched #2: 50@7,100

📊 SUMMARY:
Total Bought: 300
Total Sold: 150
Remaining: 150
Realised P/L: +50,000 riel
```

## Recent Updates

### ✅ Fixed Issues
1. **Position command** - Now displays correct data (total bought, sold, remaining, sold %, open lots)
2. **Stock price display** - Improved error handling for price data from CSX API
3. **Stock command visualization** - Added beautiful graphical chart instead of text-only display

### 🎨 New Visual Features
- Stock detail chart with LIFO matching visualization
- Improved position card showing lot details
- Dark theme with gradient backgrounds
- Color-coded profit/loss indicators

## Demo Charts

Sample visualizations are available in:
- `demo_stock_chart.png` - Stock detail visualization
- `demo_position_chart.png` - Position card visualization