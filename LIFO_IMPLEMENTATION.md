# LIFO Implementation Summary

## Changes Made

### 1. New File: `app/services_lifo.py`
- Created `LifoMatcherService` class
- Implements Last In First Out matching for stock sales
- Reverses the buy order list to match most recent purchases first
- Calculates profit based on LIFO matching

### 2. Updated: `app/bot.py`

#### Import Changes
- Changed from `services_fifo` to `services_lifo`
- Changed from `FifoMatcherService` to `LifoMatcherService`

#### Service Initialization
- Changed `self.fifo` to `self.lifo`
- Uses `LifoMatcherService` instead of `FifoMatcherService`

#### Sell Command Enhancement
- Now shows which buy orders were matched
- Displays matched order sequence numbers and quantities
- Format: `📦 Matched: #3 (100@7,200), #2 (50@7,100)`

#### New Command: `/stock ABC`
- Shows detailed stock information with LIFO allocation
- Displays buy orders (most recent first)
- Shows remaining quantity for each buy order
- Lists all sell orders with matched buy orders
- Displays realized P/L for each sale
- Provides complete summary

### 3. Updated: `README.md`
- Added LIFO documentation
- Included example scenario
- Added command reference

## How LIFO Works

When you sell shares, the system:
1. Retrieves all your buy orders for that stock
2. **Reverses the list** to get most recent purchases first
3. Matches the sale quantity against the most recent buys
4. Calculates profit based on the matched prices
5. Updates remaining quantities for each buy order

## Example

**Your Purchases:**
- Buy #1: 100 shares @ 7,000 (oldest)
- Buy #2: 100 shares @ 7,100
- Buy #3: 100 shares @ 7,200 (newest)

**You Sell:** 150 shares @ 7,500

**LIFO Matching:**
1. Match 100 shares from Buy #3 @ 7,200 → Profit: 30,000
2. Match 50 shares from Buy #2 @ 7,100 → Profit: 20,000
3. **Total Profit: 50,000 riel**

**Remaining Position:**
- Buy #1: 100 shares @ 7,000 (fully available)
- Buy #2: 50 shares @ 7,100 (partially used)
- Buy #3: 0 shares (fully matched)

## Testing

Run the bot and try these commands:
```
/buy$ABC 7000 100
/buy$ABC 7100 100
/buy$ABC 7200 100
/sell$ABC 7500 150
/stock ABC
```

The sell command will show:
- P/L calculation based on LIFO
- Which buy orders were matched
- Remaining quantities

The stock command will show:
- Complete allocation details
- Buy orders sorted by most recent first
- Remaining quantities for each buy
- Matched buys for each sell

## Benefits of LIFO

1. **Tax Planning**: In some jurisdictions, LIFO can minimize capital gains
2. **Recent Cost Basis**: Matches sales against most recent (likely higher) purchase prices
3. **Position Management**: Keeps older, potentially lower-cost shares in your position
4. **Clear Tracking**: Easy to see which specific purchases are used for each sale
