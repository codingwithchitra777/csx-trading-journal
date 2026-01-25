"""
Demo script to generate sample visualizations
This shows what the new stock detail chart looks like
"""

import matplotlib
matplotlib.use('Agg')

from app.chart_renderer import ChartRenderer
from datetime import datetime

print("Generating sample stock detail visualization...")

renderer = ChartRenderer()

# Sample data for demonstration
sample_buys = [
    {"seq": 3, "qty": 100, "price": 7200, "remaining": 0},  # Most recent, fully sold
    {"seq": 2, "qty": 100, "price": 7100, "remaining": 50},  # Partially sold
    {"seq": 1, "qty": 100, "price": 7000, "remaining": 100},  # Oldest, untouched
]

sample_sells = [
    {
        "seq": 4, 
        "qty": 150, 
        "price": 7500, 
        "pnl": 50000,
        "matched": [
            {"buySeq": 3, "qty": 100, "price": 7200},
            {"buySeq": 2, "qty": 50, "price": 7100},
        ]
    }
]

sample_summary = {
    "totalBought": 300,
    "totalSold": 150,
    "remaining": 150,
    "realisedPnl": 50000
}

# Generate the chart
img = renderer.stock_detail_card("ABC", sample_buys, sample_sells, [], sample_summary)

# Save to file
with open("/workspaces/csx-trading-journal/demo_stock_chart.png", "wb") as f:
    f.write(img.read())

print("✅ Sample stock detail chart saved to: demo_stock_chart.png")
print("\nThis chart shows:")
print("  📥 Buy orders (most recent first) with remaining quantities")
print("  📤 Sell orders with matched buy details")
print("  📊 Summary statistics (total bought, sold, remaining, P/L)")
print("\n" + "="*60)
print("LIFO Example Visualization:")
print("="*60)
print("\n📥 BUY ORDERS (Most Recent First):")
print("  🟢 #3: 100@7,200 | Remaining: 0")
print("  🟢 #2: 100@7,100 | Remaining: 50")
print("  🟢 #1: 100@7,000 | Remaining: 100")
print("\n📤 SELL ORDERS:")
print("  #4: 150@7,500 | P/L: +50,000")
print("    ↳ Matched #3: 100@7,200")
print("    ↳ Matched #2: 50@7,100")
print("\n📊 SUMMARY:")
print("  Total Bought: 300")
print("  Total Sold: 150")
print("  Remaining: 150")
print("  Realised P/L: +50,000 riel")
print("\n" + "="*60)

# Generate position card sample
print("\n\nGenerating sample position card...")

sample_position = {
    "totalBoughtQty": 300,
    "totalSoldQty": 150,
    "remainingQty": 150,
    "soldPercent": 50.0,
    "remainingLots": [
        {"seq": 1, "price": 7000, "qtyOpen": 100, "commission": 0, "orderDate": datetime.now()},
        {"seq": 2, "price": 7100, "qtyOpen": 50, "commission": 0, "orderDate": datetime.now()},
    ]
}

img2 = renderer.position_card("ABC", sample_position)

with open("/workspaces/csx-trading-journal/demo_position_chart.png", "wb") as f:
    f.write(img2.read())

print("✅ Sample position chart saved to: demo_position_chart.png")
print("\nPosition card shows:")
print("  • Total Bought: 300")
print("  • Total Sold: 150")
print("  • Remaining Qty: 150")
print("  • Sold %: 50.0%")
print("  • Open Lots: 2")
print("  • Lot details: Seq #1: 100@7,000")
print("                 Seq #2: 50@7,100")
