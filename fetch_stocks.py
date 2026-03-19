"""
Fetches all Korean stock listings (KOSPI, KOSDAQ, ETF) from NAVER Finance API.
Saves to stocks_db.json for the search feature.
"""
import requests
import json
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def fetch_market(market_name, page_size=100):
    """Fetch all stocks from a specific market (KOSPI/KOSDAQ)"""
    all_stocks = []
    page = 1
    
    while True:
        try:
            url = f'https://m.stock.naver.com/api/stocks/marketValue/{market_name}?page={page}&pageSize={page_size}'
            resp = requests.get(url, headers=HEADERS, timeout=15)
            data = resp.json()
            stocks = data.get('stocks', [])
            
            if not stocks:
                break
            
            for s in stocks:
                all_stocks.append({
                    'symbol': s.get('itemCode', ''),
                    'name': s.get('stockName', ''),
                    'market': market_name,
                })
            
            total = data.get('totalCount', 0)
            if page * page_size >= total:
                break
            page += 1
            
        except Exception as e:
            print(f"  {market_name} page {page} 오류: {e}")
            break
    
    print(f"  {market_name}: {len(all_stocks)}개")
    return all_stocks

def fetch_etf():
    """Fetch all ETF listings"""
    try:
        url = 'https://finance.naver.com/api/sise/etfItemList.nhn'
        params = {'etfType': 0, 'targetColumn': 'market_sum', 'sortOrder': 'desc'}
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        data = resp.json()
        items = data.get('result', {}).get('etfItemList', [])
        
        results = []
        for item in items:
            results.append({
                'symbol': item.get('itemcode', ''),
                'name': item.get('itemname', ''),
                'market': 'ETF',
            })
        print(f"  ETF: {len(results)}개")
        return results
    except Exception as e:
        print(f"  ETF 오류: {e}")
        return []

if __name__ == "__main__":
    print("한국 전체 종목 데이터 수집 중...")
    
    all_stocks = []
    all_stocks.extend(fetch_market('KOSPI'))
    all_stocks.extend(fetch_market('KOSDAQ'))
    all_stocks.extend(fetch_etf())
    
    # Remove duplicates
    seen = set()
    unique = []
    for s in all_stocks:
        if s['symbol'] and s['symbol'] not in seen:
            seen.add(s['symbol'])
            unique.append(s)
    
    output = {
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'total_count': len(unique),
        'stocks': unique
    }
    
    with open('stocks_db.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False)
    
    print(f"\n완료! 총 {len(unique)}개 종목 → stocks_db.json")
