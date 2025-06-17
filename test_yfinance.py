import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def test_stock_fetch():
    print("=== Testing yfinance connectivity ===")
    
    # Test basic connection
    try:
        stock = yf.Ticker("AAPL")
        print(f"✓ Created ticker object for AAPL")
        
        # Test basic info
        try:
            info = stock.info
            if info:
                print(f"✓ Basic info available: {info.get('longName', 'Unknown')}")
            else:
                print("✗ No basic info available")
        except Exception as e:
            print(f"✗ Error getting info: {e}")
        
        # Test with different approaches
        approaches = [
            ("1d", "1 day"),
            ("5d", "5 days"),
            ("1mo", "1 month")
        ]
        
        for period, desc in approaches:
            try:
                print(f"\nTrying {desc} ({period})...")
                hist = stock.history(period=period, auto_adjust=True, prepost=True)
                if not hist.empty:
                    print(f"✓ Got {len(hist)} data points")
                    print(f"  Latest close: ${hist['Close'].iloc[-1]:.2f}")
                    print(f"  Date range: {hist.index[0]} to {hist.index[-1]}")
                    return True
                else:
                    print(f"✗ Empty data for {period}")
            except Exception as e:
                print(f"✗ Error with {period}: {e}")
        
        # Try alternative method
        print(f"\nTrying alternative download method...")
        data = yf.download("AAPL", period="5d", auto_adjust=True)
        if not data.empty:
            print(f"✓ Download method worked: {len(data)} points")
            print(f"  Latest close: ${data['Close'].iloc[-1]:.2f}")
            return True
        else:
            print("✗ Download method failed")
            
    except Exception as e:
        print(f"✗ General error: {e}")
    
    return False

if __name__ == "__main__":
    success = test_stock_fetch()
    if success:
        print("\n🎉 Stock fetching is working!")
    else:
        print("\n❌ Stock fetching failed - may need to use mock data")
