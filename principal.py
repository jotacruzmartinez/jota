import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# Configuración de la página
st.set_page_config(page_title="Radar Maestro Golden", layout="wide")
st.title("💰 Mis Oportunidades de Inversión")
st.write("Presioná el botón para escanear el mercado en tiempo real.")

# LISTA COMPLETA DE 188 ACTIVOS (USA + ARG)
TODOS = ["MMM", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AMZN", "AAPL", "BA", "BABA", "BBD", "BCS", "BHP", "BIDU", "BIIB", "BP", "BRK-B", "BSBR", "C", "CAT", "CHTR", "CL", "COST", "CRM", "CSCO", "CVS", "CVX", "DD", "DE", "DIS", "EBAY", "FDX", "GE", "GFI", "GILD", "GLD", "GOOGL", "GS", "HAL", "HD", "HMC", "HON", "HPQ", "HSBC", "IBM", "INTC", "ITUB", "JD", "JNJ", "JPM", "KO", "LLY", "LMT", "MA", "MCD", "MDT", "MELI", "MO", "MRK", "MSFT", "MSI", "MU", "NEM", "NFLX", "NKE", "NVDA", "ORCL", "PBR", "PEP", "PFE", "PG", "PYPL", "QCOM", "RTX", "SBUX", "SCHW", "SLB", "SNAP", "SONY", "SPY", "T", "TGT", "TM", "TSLA", "TSM", "TXN", "UAL", "UNH", "UNP", "V", "VALE", "VZ", "WFC", "WMT", "XOM", "ZM", "QQQ", "DIA", "EEM", "IWM", "XLF", "XLE", "XLU", "XLK", "XLV", "XLP", "XLI", "XLB", "XLC", "GDX", "EWZ", "ARKK", "BITO", "IREN", "RIOT", "MARA", "COIN", "MSTR", "PLTR", "AI", "U", "SNOW", "PATH", "SE", "SHOP", "SPOT", "UBER", "ABNB", "ALUA.BA", "BBAR.BA", "BMA.BA", "BYMA.BA", "CEPU.BA", "COME.BA", "CRES.BA", "EDN.BA", "GGAL.BA", "LOMA.BA", "MIRG.BA", "PAMP.BA", "SUPV.BA", "TECO2.BA", "TGNO4.BA", "TGSU2.BA", "TRAN.BA", "TXAR.BA", "VALO.BA", "YPFD.BA", "AGRO.BA", "AUSO.BA", "BHIP.BA", "BOLT.BA", "BPAT.BA", "CADO.BA", "CAPX.BA", "CARC.BA", "CECO2.BA", "CELU.BA", "CGPA2.BA", "CTIO.BA", "DGCU2.BA", "DOME.BA", "DYCA.BA", "FERR.BA", "FIPL.BA", "GAMI.BA", "GARO.BA", "GBAN.BA", "GCLA.BA", "GRIM.BA", "HAVA.BA", "INTR.BA", "INVJ.BA", "IRSA.BA", "LEDE.BA", "LONG.BA", "METR.BA", "MOLA.BA", "MOLI.BA", "MORI.BA", "OEST.BA", "PATA.BA", "PATR.BA", "PGR.BA", "RIGO.BA", "ROSE.BA", "SAMI.BA", "SEMI.BA", "VIST.BA", "RICH.BA"]

def analizar_activo(ticker):
    try:
        # Descarga de datos
        data = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if data.empty or len(data) < 25: return None
        
        # Precios y SMA20
        precio = float(data['Close'].iloc[-1])
        sma20 = float(data['Close'].rolling(20).mean().iloc[-1])
        
        # RSI 14 (Limpio)
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain.iloc[-1] / loss.iloc[-1]
        rsi_val = 100 - (100 / (1 + rs))
        
        # ATR y Stop Loss (Precio - ATR * 2)
        tr = pd.concat([data['High']-data['Low'], abs(data['High']-data['Close'].shift()), abs(data['Low']-data['Close'].shift())], axis=1).max(axis=1)
        atr = float(tr.rolling(14).mean().iloc[-1])
        sl = precio - (atr * 2)
        
        # Definición de Estado
        if precio > sma20 and 30 < rsi_val < 70:
            estado = "GOLDEN 💎"
        elif precio > sma20:
            estado = "BULL 🐂"
        else:
            estado = "BEAR 🐻"

        return {
            "Ticker": ticker,
            "Precio": f"{precio:.2f}",
            "RSI": f"{rsi_val:.2f}",
            "Stop Loss": f"{sl:.2f}",
            "Estado": estado
        }
    except:
        return None

if st.button('🚀 EJECUTAR ESCÁNER MAESTRO'):
    with st.spinner('Escaneando activos...'):
        with ThreadPoolExecutor(max_workers=10) as executor:
            resultados = list(executor.map(analizar_activo, TODOS))
        
        # Filtrar y mostrar resultados
        df_final = pd.DataFrame([r for r in resultados if r is not None])
        if not df_final.empty:
            st.success(f"Análisis completado para {len(df_final)} activos.")
            st.dataframe(df_final.sort_values("Estado", ascending=False), use_container_width=True)
        else:
            st.error("No se pudieron obtener datos en este momento.")
