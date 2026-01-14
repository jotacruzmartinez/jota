import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Estrategia Golden", layout="wide")
st.title("💰 Mis Oportunidades de Inversión")

# --- LISTADOS ACTUALIZADOS ---
cedears = ["MMM", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AMZN", "AAPL", "BA", "BABA", "BBD", "BCS", "BHP", "BIDU", "BIIB", "BP", "BRK-B", "BSBR", "C", "CAT", "CHTR", "CL", "COST", "CRM", "CSCO", "CVS", "CVX", "DD", "DE", "DIS", "EBAY", "FDX", "GE", "GFI", "GILD", "GLD", "GOOGL", "GS", "HAL", "HD", "HMC", "HON", "HPQ", "HSBC", "IBM", "INTC", "ITUB", "JD", "JNJ", "JPM", "KO", "LLY", "LMT", "MA", "MCD", "MDT", "MELI", "MO", "MRK", "MSFT", "MSI", "MU", "NEM", "NFLX", "NKE", "NVDA", "ORCL", "PBR", "PEP", "PFE", "PG", "PYPL", "QCOM", "RTX", "SBUX", "SCHW", "SLB", "SNAP", "SONY", "SPY", "T", "TGT", "TM", "TSLA", "TSM", "TXN", "UAL", "UNH", "UNP", "V", "VALE", "VZ", "WFC", "WMT", "XOM", "ZM", "QQQ", "DIA", "EEM", "IWM", "XLF", "XLE", "XLU", "XLK", "XLV", "XLP", "XLI", "XLB", "XLC", "GDX", "EWZ", "ARKK", "BITO", "IREN", "RIOT", "MARA", "COIN", "MSTR", "PLTR", "AI", "U", "SNOW", "PATH", "SE", "SHOP", "SPOT", "UBER", "ABNB"]
merval = ["ALUA.BA", "BBAR.BA", "BMA.BA", "BYMA.BA", "CEPU.BA", "COME.BA", "CRES.BA", "EDN.BA", "GGAL.BA", "LOMA.BA", "MIRG.BA", "PAMP.BA", "SUPV.BA", "TECO2.BA", "TGNO4.BA", "TGSU2.BA", "TRAN.BA", "TXAR.BA", "VALO.BA", "YPFD.BA", "AGRO.BA", "AUSO.BA", "BHIP.BA", "BOLT.BA", "BPAT.BA", "CADO.BA", "CAPX.BA", "CARC.BA", "CECO2.BA", "CELU.BA", "CGPA2.BA", "CTIO.BA", "DGCU2.BA", "DOME.BA", "DYCA.BA", "FERR.BA", "FIPL.BA", "GAMI.BA", "GARO.BA", "GBAN.BA", "GCLA.BA", "GRIM.BA", "HAVA.BA", "INTR.BA", "INVJ.BA", "IRSA.BA", "LEDE.BA", "LONG.BA", "METR.BA", "MOLA.BA", "MOLI.BA", "MORI.BA", "OEST.BA", "PATA.BA", "PATR.BA", "PGR.BA", "RIGO.BA", "ROSE.BA", "SAMI.BA", "SEMI.BA", "VIST.BA", "RICH.BA"]
TODOS = cedears + merval

def analizar(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if len(df) < 25: return None
        
        # Datos básicos
        close = df['Close']
        precio = float(close.iloc[-1])
        sma = float(close.rolling(20).mean().iloc[-1])
        
        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
        
        # ATR y Salidas (Según imagen 07)
        tr = pd.concat([df['High']-df['Low'], abs(df['High']-close.shift()), abs(df['Low']-close.shift())], axis=1).max(axis=1)
        atr = float(tr.rolling(14).mean().iloc[-1])
        sl = precio - (atr * 2) # Imagen 07: ATR x 2
        tp = precio + (atr * 3) # Ratio R/B 1:2 o superior
        
        # Estados (Según imagen 09)
        tendencia = "BULL 🐂" if precio > sma else "BEAR 🐻"
        estado = "GOLDEN 💎" if (tendencia == "BULL 🐂" and 30 < rsi < 70) else tendencia

        return {
            "Mercado": "ARG" if ".BA" in ticker else "USA",
            "Ticker": ticker,
            "Precio": round(precio, 2),
            "Media 20": round(sma, 2),
            "RSI": round(rsi, 2),
            "ATR": round(atr, 2),
            "Stop Loss": round(sl, 2),
            "Take Profit": round(tp, 2),
            "Tendencia": tendencia,
            "Estado": estado
        }
    except:
        return None

# --- EJECUCIÓN ---
if st.button('🚀 Iniciar Escaneo Maestro'):
    with st.spinner('Analizando 188 activos...'):
        with ThreadPoolExecutor(max_workers=10) as executor:
            res = list(executor.map(analizar, TODOS))
        
        final_df = pd.DataFrame([r for r in res if r is not None])
        if not final_df.empty:
            st.success(f"Escaneo finalizado. {len(final_df)} activos encontrados.")
            st.dataframe(final_df.sort_values("Estado", ascending=False), use_container_width=True)
