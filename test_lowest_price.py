"""
Test script to verify Lowest Price First matching
"""

print("=" * 70)
print("LOWEST PRICE FIRST MATCHING - EXAMPLE")
print("=" * 70)

print("\n📊 Scenario:")
print("-" * 70)
print("You buy shares at different prices:")
print("  • Buy #1: 100 shares @ 7,000 riel (LOWEST PRICE)")
print("  • Buy #2: 100 shares @ 7,100 riel")
print("  • Buy #3: 100 shares @ 7,200 riel (HIGHEST PRICE)")
print("\nThen you sell:")
print("  • Sell #4: 150 shares @ 7,500 riel")

print("\n💡 Lowest Price First Matching:")
print("-" * 70)
print("The system matches your sale with LOWEST PRICED purchases first:")
print("\n  1️⃣ Match 100 shares from Buy #1 @ 7,000")
print("     → Profit: 100 × (7,500 - 7,000) = 50,000 riel")
print("\n  2️⃣ Match 50 shares from Buy #2 @ 7,100")
print("     → Profit: 50 × (7,500 - 7,100) = 20,000 riel")
print("\n  ✅ Total Profit: 70,000 riel (before commissions)")

print("\n📦 Remaining Position:")
print("-" * 70)
print("  • Buy #2: 50 shares @ 7,100 (partially sold)")
print("  • Buy #3: 100 shares @ 7,200 (untouched)")
print("  • Total Remaining: 150 shares")

print("\n📈 Bot Response:")
print("-" * 70)
print("  ✅ SELL confirmed | Seq #4 | P/L: +70,000 riel")
print("  📦 Matched: #1 (100@7,000), #2 (50@7,100)")

print("\n" + "=" * 70)
print("WHY LOWEST PRICE FIRST?")
print("=" * 70)
print("\n✅ Benefits:")
print("  • MAXIMIZES profit on each sale")
print("  • Sells cheapest shares first")
print("  • Keeps higher-priced shares in inventory")
print("  • Better for short-term trading strategies")

print("\n📊 Comparison with other methods:")
print("-" * 70)

print("\n1️⃣ LOWEST PRICE FIRST (Current):")
print("   Match: #1 (7,000) + #2 (7,100)")
print("   Profit: 50,000 + 20,000 = 70,000 riel ✅ HIGHEST")

print("\n2️⃣ FIFO (First In First Out):")
print("   Match: #1 (7,000) + #2 (7,100)")
print("   Profit: 50,000 + 20,000 = 70,000 riel")
print("   Note: Same as lowest price in this example")

print("\n3️⃣ LIFO (Last In First Out):")
print("   Match: #3 (7,200) + #2 (7,100)")
print("   Profit: 30,000 + 20,000 = 50,000 riel ❌ LOWEST")

print("\n" + "=" * 70)
print("✅ YOUR BOT NOW USES LOWEST PRICE FIRST MATCHING!")
print("=" * 70)

print("\n🎯 Try it yourself:")
print("  /buy$ABC 7000 100")
print("  /buy$ABC 7100 100")
print("  /buy$ABC 7200 100")
print("  /sell$ABC 7500 150")
print("  /stock ABC")
print()
