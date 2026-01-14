import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# --- 1. CONFIGURACIÓN DEL SISTEMA ---
st.set_page_config(page_title="Radar Estrategia Golden", layout="wide")
st.title("💎 Panel Maestro: Estrategia Golden")

# --- 2. LISTADOS (188 ACTIVOS) ---
cedears_usa = ["MMM", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AMZN", "AAPL", "BA", "BABA", "BBD", "BCS", "BHP", "BIDU", "BIIB", "BP", "BRK-B", "BSBR", "C", "CAT", "CHTR", "CL", "COST", "CRM", "CSCO", "CVS", "CVX", "DD", "DE", "DIS", "EBAY", "FDX", "GE", "GFI", "GILD", "GLD", "GOOGL", "GS", "HAL", "HD", "HMC", "HON", "HPQ", "HSBC", "IBM", "INTC", "ITUB", "JD", "JNJ", "JPM", "KO", "LLY", "LMT", "MA", "MCD", "MDT", "MELI", "MO", "MRK", "MSFT", "MSI", "MU", "NEM", "NFLX", "NKE", "NVDA", "ORCL", "PBR", "PEP", "PFE", "PG", "PYPL", "QCOM", "RTX", "SBUX", "SCHW", "SLB", "SNAP", "SONY", "SPY", "T", "TGT", "TM", "TSLA", "TSM", "TXN", "UAL", "UNH", "UNP", "V", "VALE", "VZ", "WFC", "WMT", "XOM", "ZM", "QQQ", "DIA", "EEM", "IWM", "XLF", "XLE", "XLU", "XLK", "XLV", "XLP", "XLI", "XLB", "XLC", "GDX", "EWZ", "ARKK", "BITO", "IREN", "RIOT", "MARA", "COIN", "MSTR", "PLTR", "AI", "U", "SNOW", "PATH", "SE", "SHOP", "SPOT", "UBER", "ABNB"]
activos_arg = ["ALUA.BA", "BBAR.BA", "BMA.BA", "BYMA.BA", "CEPU.BA", "COME.BA", "CRES.BA", "EDN.BA", "GGAL.BA", "LOMA.BA", "MIRG.BA", "PAMP.BA", "SUPV.BA", "TECO2.BA", "TGNO4.BA", "TGSU2.BA", "TRAN.BA", "TXAR.BA", "VALO.BA", "YPFD.BA", "AGRO.BA", "AUSO.BA", "BHIP.BA", "BOLT.BA", "BPAT.BA", "CADO.BA", "CAPX.BA", "CARC.BA", "CECO2.BA", "CELU.BA", "CGPA2.BA", "CTIO.BA", "DGCU2.BA", "DOME.BA", "DYCA.BA", "FERR.BA", "FIPL.BA", "GAMI.BA", "GARO.BA", "GBAN.BA", "GCLA.BA", "GRIM.BA", "HAVA.BA", "INTR.BA", "INVJ.BA", "IRSA.BA", "LEDE.BA", "LONG.BA", "METR.BA", "MOLA.BA", "MOLI.BA", "MORI.BA", "OEST.BA", "PATA.BA", "PATR.BA", "PGR.BA", "RIGO.BA", "ROSE.BA", "SAMI.BA", "SEMI.BA", "VIST.BA", "RICH.BA"]
TODOS_LOS_TICKERS = cedears_usa + activos_arg

# --- 3. EL MOTOR DE ANÁLISIS ---
def analizar_activo(ticker):
    try:
        # Descarga de datos
        data = yf.download(ticker, period="4mo", interval="1d", progress=False)
        if len(data) < 30: return None
        
        info = yf.Ticker(ticker).info
        close = data['Close']
        precio = float(close.iloc[-1])
        
        # Media Móvil 20
        sma = float(close.rolling(window=20).mean().iloc[-1])
        
        # RSI 14
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
        
        # ATR 14
        hl = data['High'] - data['Low']
        hc = np.abs(data['High'] - data['Close'].shift())
        lc = np.abs(data['Low'] - data['Close'].shift())
        tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
        atr = float(tr.rolling(14).mean().iloc[-1])
        
        # Salidas
        sl = precio - (atr * 2)
        tp = precio + (atr * 3)
        
        # Tendencia y Estrategia
        tendencia = "BULL 🐂" if precio > sma else "BEAR 🐻"
        estrategia = "GOLDEN 💎" if (tendencia == "BULL 🐂" and 30 < rsi < 70) else tendencia

        return {
            "Mercado": "ARG" if ".BA" in ticker else "USA",
            "Ticker": ticker,
            "Empresa": info.get('longName', 'N/A'),
            "Industria": info.get('industry', 'N/A'),
            "Precio": round(precio, 2),
            "SMA 20": round(sma, 2),
            "RSI": round(rsi, 2),
            "ATR": round(atr, 2),
            "Stop Loss": round(sl, 2),
            "Take Profit": round(tp, 2),
            "Tendencia": tendencia,
            "Estrategia": estrategia
        }
    except:
        return None

@st.cache_data(ttl=600)
def ejecutar_proceso(lista):
    with ThreadPoolExecutor(max_workers=15) as executor:
        resultados = list(executor.map(analizar_activo, lista))
    return [r for r in resultados if r is not None]

# --- 4. INTERFAZ ---
if st.button('🚀 INICIAR ESCANEO MAESTRO'):
    with st.spinner('Analizando mercado...'):
        resultados = ejecutar_proceso(TODOS_LOS_TICKERS)
        if resultados:
            df = pd.DataFrame(resultados)
            st.success(f"Escaneo completo: {len(df)} activos analizados.")
            st.dataframe(df, use_container_width=True)
        else:
            st.error("No se pudieron obtener datos. Reintente.")
