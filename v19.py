import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="Radar Estrategia Golden", layout="wide")
st.title("💎 Radar Maestro: Estrategia Golden")

# --- LISTADOS COMPLETOS (188 ACTIVOS) ---
cedears = ["MMM", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AMZN", "AAPL", "BA", "BABA", "BBD", "BCS", "BHP", "BIDU", "BIIB", "BP", "BRK-B", "BSBR", "C", "CAT", "CHTR", "CL", "COST", "CRM", "CSCO", "CVS", "CVX", "DD", "DE", "DIS", "EBAY", "FDX", "GE", "GFI", "GILD", "GLD", "GOOGL", "GS", "HAL", "HD", "HMC", "HON", "HPQ", "HSBC", "IBM", "INTC", "ITUB", "JD", "JNJ", "JPM", "KO", "LLY", "LMT", "MA", "MCD", "MDT", "MELI", "MO", "MRK", "MSFT", "MSI", "MU", "NEM", "NFLX", "NKE", "NVDA", "ORCL", "PBR", "PEP", "PFE", "PG", "PYPL", "QCOM", "RTX", "SBUX", "SCHW", "SLB", "SNAP", "SONY", "SPY", "T", "TGT", "TM", "TSLA", "TSM", "TXN", "UAL", "UNH", "UNP", "V", "VALE", "VZ", "WFC", "WMT", "XOM", "ZM", "QQQ", "DIA", "EEM", "IWM", "XLF", "XLE", "XLU", "XLK", "XLV", "XLP", "XLI", "XLB", "XLC", "GDX", "EWZ", "ARKK", "BITO", "IREN", "RIOT", "MARA", "COIN", "MSTR", "PLTR", "AI", "U", "SNOW", "PATH", "SE", "SHOP", "SPOT", "UBER", "ABNB"]
merval = ["ALUA.BA", "BBAR.BA", "BMA.BA", "BYMA.BA", "CEPU.BA", "COME.BA", "CRES.BA", "EDN.BA", "GGAL.BA", "LOMA.BA", "MIRG.BA", "PAMP.BA", "SUPV.BA", "TECO2.BA", "TGNO4.BA", "TGSU2.BA", "TRAN.BA", "TXAR.BA", "VALO.BA", "YPFD.BA", "AGRO.BA", "AUSO.BA", "BHIP.BA", "BOLT.BA", "BPAT.BA", "CADO.BA", "CAPX.BA", "CARC.BA", "CECO2.BA", "CELU.BA", "CGPA2.BA", "CTIO.BA", "DGCU2.BA", "DOME.BA", "DYCA.BA", "FERR.BA", "FIPL.BA", "GAMI.BA", "GARO.BA", "GBAN.BA", "GCLA.BA", "GRIM.BA", "HAVA.BA", "INTR.BA", "INVJ.BA", "IRSA.BA", "LEDE.BA", "LONG.BA", "METR.BA", "MOLA.BA", "MOLI.BA", "MORI.BA", "OEST.BA", "PATA.BA", "PATR.BA", "PGR.BA", "RIGO.BA", "ROSE.BA", "SAMI.BA", "SEMI.BA", "VIST.BA", "RICH.BA"]
TODOS = cedears + merval

# --- MOTOR TÉCNICO ---
def analizar_activo(ticker):
    try:
        data = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if len(data) < 25: return None
        
        # Info básica
        t_info = yf.Ticker(ticker).info
        precio = float(data['Close'].iloc[-1])
        sma20 = float(data['Close'].rolling(20).mean().iloc[-1])
        
        # RSI 14
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
        
        # ATR 14 y Salidas
        tr = pd.concat([data['High']-data['Low'], abs(data['High']-data['Close'].shift()), abs(data['Low']-data['Close'].shift())], axis=1).max(axis=1)
        atr = float(tr.rolling(14).mean().iloc[-1])
        sl = precio - (atr * 2) # Regla: ATR x 2
        tp = precio + (atr * 3)
        
        # Estados (Bull/Bear/Golden)
        tendencia = "BULL 🐂" if precio > sma20 else "BEAR 🐻"
        estado = "GOLDEN 💎" if (tendencia == "BULL 🐂" and 30 < rsi < 70) else tendencia

        return {
            "Mercado": "ARG" if ".BA" in ticker else "USA",
            "Ticker": ticker,
            "Empresa": t_info.get('longName', 'N/A'),
            "Industria": t_info.get('industry', 'N/A'),
            "Precio": round(precio, 2),
            "SMA 20": round(sma20, 2),
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
if st.button('🚀 EJECUTAR ESCÁNER MAESTRO'):
    with st.spinner('Analizando el mercado...'):
        with ThreadPoolExecutor(max_workers=10) as executor:
            resultados = list(executor.map(analizar_activo, TODOS))
        
        df_final = pd.DataFrame([r for r in resultados if r is not None])
        if not df_final.empty:
            st.success(f"Escaneo exitoso para {len(df_final)} activos.")
            st.dataframe(df_final.sort_values("Estado", ascending=False), use_container_width=True)
        else:
            st.error("No se pudieron obtener datos. Verificá tu conexión.")
