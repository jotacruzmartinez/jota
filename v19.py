import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Estrategia Golden", layout="wide")
st.title("💎 Radar Maestro: Estrategia Golden")

# Lista unificada de 188 activos (USA + ARG)
TODOS = ["MMM", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AMZN", "AAPL", "BA", "BABA", "BBD", "BCS", "BHP", "BIDU", "BIIB", "BP", "BRK-B", "BSBR", "C", "CAT", "CHTR", "CL", "COST", "CRM", "CSCO", "CVS", "CVX", "DD", "DE", "DIS", "EBAY", "FDX", "GE", "GFI", "GILD", "GLD", "GOOGL", "GS", "HAL", "HD", "HMC", "HON", "HPQ", "HSBC", "IBM", "INTC", "ITUB", "JD", "JNJ", "JPM", "KO", "LLY", "LMT", "MA", "MCD", "MDT", "MELI", "MO", "MRK", "MSFT", "MSI", "MU", "NEM", "NFLX", "NKE", "NVDA", "ORCL", "PBR", "PEP", "PFE", "PG", "PYPL", "QCOM", "RTX", "SBUX", "SCHW", "SLB", "SNAP", "SONY", "SPY", "T", "TGT", "TM", "TSLA", "TSM", "TXN", "UAL", "UNH", "UNP", "V", "VALE", "VZ", "WFC", "WMT", "XOM", "ZM", "QQQ", "DIA", "EEM", "IWM", "XLF", "XLE", "XLU", "XLK", "XLV", "XLP", "XLI", "XLB", "XLC", "GDX", "EWZ", "ARKK", "BITO", "IREN", "RIOT", "MARA", "COIN", "MSTR", "PLTR", "AI", "U", "SNOW", "PATH", "SE", "SHOP", "SPOT", "UBER", "ABNB", "ALUA.BA", "BBAR.BA", "BMA.BA", "BYMA.BA", "CEPU.BA", "COME.BA", "CRES.BA", "EDN.BA", "GGAL.BA", "LOMA.BA", "MIRG.BA", "PAMP.BA", "SUPV.BA", "TECO2.BA", "TGNO4.BA", "TGSU2.BA", "TRAN.BA", "TXAR.BA", "VALO.BA", "YPFD.BA", "AGRO.BA", "AUSO.BA", "BHIP.BA", "BOLT.BA", "BPAT.BA", "CADO.BA", "CAPX.BA", "CARC.BA", "CECO2.BA", "CELU.BA", "CGPA2.BA", "CTIO.BA", "DGCU2.BA", "DOME.BA", "DYCA.BA", "FERR.BA", "FIPL.BA", "GAMI.BA", "GARO.BA", "GBAN.BA", "GCLA.BA", "GRIM.BA", "HAVA.BA", "INTR.BA", "INVJ.BA", "IRSA.BA", "LEDE.BA", "LONG.BA", "METR.BA", "MOLA.BA", "MOLI.BA", "MORI.BA", "OEST.BA", "PATA.BA", "PATR.BA", "PGR.BA", "RIGO.BA", "ROSE.BA", "SAMI.BA", "SEMI.BA", "VIST.BA", "RICH.BA"]

def analizar_activo(ticker):
    try:
        data = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if len(data) < 25: return None
        close = data['Close']
        precio = float(close.iloc[-1])
        sma20 = float(close.rolling(20).mean().iloc[-1])
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
        tr = pd.concat([data['High']-data['Low'], abs(data['High']-close.shift()), abs(data['Low']-close.shift())], axis=1).max(axis=1)
        atr = float(tr.rolling(14).mean().iloc[-1])
        
        return {
            "Ticker": ticker,
            "Precio": round(precio, 2),
            "RSI": round(rsi, 2),
            "Stop Loss": round(precio - (atr * 2), 2),
            "Take Profit": round(precio + (atr * 3), 2),
            "Estado": "GOLDEN 💎" if (precio > sma20 and 30 < rsi < 70) else ("BULL 🐂" if precio > sma20 else "BEAR 🐻")
        }
    except: return None

if st.button('🚀 EJECUTAR ESCÁNER'):
    with st.spinner('Analizando...'):
        with ThreadPoolExecutor(max_workers=10) as ex:
            res = list(ex.map(analizar_activo, TODOS))
        df = pd.DataFrame([r for r in res if r is not None])
        st.dataframe(df.sort_values("Estado", ascending=False), use_container_width=True)
