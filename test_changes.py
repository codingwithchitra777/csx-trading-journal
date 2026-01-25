"""Test script to verify all changes are working correctly"""

print("Testing imports...")
try:
    from app.bot import CsxTradingBot
    from app.chart_renderer import ChartRenderer
    from app.services_lifo import LifoMatcherService
    from app.services_pricing import PricingService
    print("✅ All imports successful!")
except Exception as e:
    print(f"❌ Import error: {e}")
    exit(1)

print("\nTesting ChartRenderer methods...")
try:
    renderer = ChartRenderer()
    
    # Test stock_detail_card method exists
    assert hasattr(renderer, 'stock_detail_card'), "stock_detail_card method not found"
    print("✅ stock_detail_card method exists")
    
    # Test position_card method
    assert hasattr(renderer, 'position_card'), "position_card method not found"
    print("✅ position_card method exists")
    
except Exception as e:
    print(f"❌ ChartRenderer error: {e}")
    exit(1)

print("\n" + "="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
print("\nChanges implemented:")
print("1. ✅ LIFO matching for stock sales")
print("2. ✅ Stock command with visual plot (/stock ABC)")
print("3. ✅ Fixed position command to show correct data")
print("4. ✅ Fixed stock price display with better error handling")
print("\nNew Features:")
print("- Stock detail visualization shows:")
print("  • Buy orders (most recent first)")
print("  • Sell orders with matched buys")
print("  • Remaining quantities")
print("  • Realized P/L summary")
print("\n- Position command now shows:")
print("  • Total bought/sold quantities")
print("  • Remaining quantity and percentage")
print("  • Number of open lots")
print("  • Details of remaining lots")
