from app import fetch_stock_data
print('Testing stock data fetching from the app...')
data, figure = fetch_stock_data(['AAPL'])
print('\nResults:')
for ticker, info in data.items():
    source = info.get('source', 'unknown')
    price = info.get('current_price', 0)
    print(f'{ticker}: source={source}, price=${price:.2f}')
    if 'error' in info:
        print(f'  Error: {info["error"]}')
