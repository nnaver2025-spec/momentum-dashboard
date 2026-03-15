import yfinance as yf
import pandas as pd
import json
from datetime import datetime

def get_macro_data():
    macro_dict = {"US10Y": 0.0, "DXY": 0.0}
    try:
        tnx = yf.Ticker("^TNX").history(period="5d")
        if not tnx.empty: 
            macro_dict["US10Y"] = round(float(tnx['Close'].iloc[-1]), 3)
        
        dxy = yf.Ticker("DX-Y.NYB").history(period="5d")
        if not dxy.empty: 
            macro_dict["DXY"] = round(float(dxy['Close'].iloc[-1]), 2)
    except Exception as e:
        print(f"Macro data error: {e}")
        
    return macro_dict

def get_momentum_stocks():
    url = 'https://en.wikipedia.org/wiki/List_of_S&P_500_companies'
    table = pd.read_html(url)[0]
    tickers = table['Symbol'].tolist()[:100] 

    spy = yf.download('SPY', period="3mo")['Close']
    spy_return = (spy.iloc[-1] - spy.iloc[0]) / spy.iloc[0]

    results = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            if len(hist) < 200: continue

            current_price = float(hist['Close'].iloc[-1])
            ma50 = float(hist['Close'].rolling(window=50).mean().iloc[-1])
            ma200 = float(hist['Close'].rolling(window=200).mean().iloc[-1])
            high52w = float(hist['Close'].max())

            if current_price > ma50 and ma50 > ma200:
                if current_price >= high52w * 0.95:
                    hist_3mo = hist.tail(63) 
                    stock_return = (hist_3mo['Close'].iloc[-1] - hist_3mo['Close'].iloc[0]) / hist_3mo['Close'].iloc[0]

                    if stock_return > spy_return:
                        results.append({
                            "ticker": ticker, "price": round(current_price, 2),
                            "ma50": round(ma50, 2), "ma200": round(ma200, 2),
                            "high52w": round(high52w, 2), "return_3mo_pct": round(stock_return * 100, 2)
                        })
        except: continue
    return sorted(results, key=lambda x: x['return_3mo_pct'], reverse=True)[:5]

if __name__ == "__main__":
    macro_data = get_macro_data()
    momentum_data = get_momentum_stocks()
    final_output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "macro_indicators": macro_data,
        "top_momentum_stocks": momentum_data
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4)
