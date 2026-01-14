import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Radar Maestro Golden", layout="wide")
st.title("💎 Radar de Inversiones Maestro")

# Listado de activos con etiqueta de mercado
USA = ["MMM", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AMZN", "AAPL", "BA", "BABA", "BBD", "BCS", "BHP", "BIDU", "BIIB", "BP", "BRK-B", "BSBR", "C", "CAT", "CHTR", "CL", "COST", "CRM", "CSCO", "CVS", "CVX", "DD", "DE", "DIS", "EBAY", "FDX", "GE", "GFI", "GILD", "GLD", "GOOGL", "GS", "HAL", "HD", "HMC", "HON", "HPQ", "HSBC", "IBM", "INTC", "ITUB", "JD", "JNJ", "JPM", "KO", "LLY", "LMT", "MA", "MCD", "MDT", "MELI", "MO", "MRK", "MSFT", "MSI", "MU", "NEM", "NFLX", "NKE", "NVDA", "ORCL", "PBR", "PEP", "PFE", "PG", "PYPL", "QCOM", "RTX", "SBUX", "SCHW", "SLB", "SNAP", "SONY", "SPY", "T", "TGT", "TM", "TSLA", "TSM", "TXN", "UAL", "UNH", "UNP", "V", "VALE", "VZ", "WFC", "WMT", "XOM", "ZM", "QQQ", "DIA", "EEM", "IWM", "XLF", "XLE", "XLU", "XLK", "XLV", "XLP", "XLI", "XLB", "XLC", "GDX", "EWZ", "ARKK", "BITO", "IREN", "RIOT", "MARA", "COIN", "MSTR", "PLTR", "AI", "U", "SNOW", "PATH", "SE", "SHOP", "SPOT", "UBER", "ABNB"]
ARG = ["ALUA.BA", "BBAR.BA", "BMA.BA", "BYMA.BA", "CEPU.BA", "COME.BA", "CRES.BA", "EDN.BA", "GGAL.BA", "LOMA.BA", "MIRG.BA", "PAMP.BA", "SUPV.BA", "TECO2.BA", "TGNO4.BA", "TGSU2.BA", "TRAN.BA", "TXAR.BA", "VALO.BA", "YPFD.BA", "AGRO.BA", "AUSO.BA", "BHIP.BA", "BOLT.BA", "BPAT.BA", "CADO.BA", "CAPX.BA", "CARC.BA", "CECO2.BA", "CELU.BA", "CGPA2.BA", "CTIO.BA", "DGCU2.BA", "DOME.BA", "DYCA.BA", "FERR.BA", "FIPL.BA", "GAMI.BA", "GARO.BA", "GBAN.BA", "GCLA.BA", "GRIM.BA", "HAVA.BA", "INTR.BA", "INVJ.BA", "IRSA.BA", "LEDE.BA", "LONG.BA", "METR.BA", "MOLA.BA", "MOLI.BA", "MORI.BA", "OEST.BA", "PATA.BA", "PATR.BA", "PGR.BA", "RIGO.BA", "ROSE.BA", "SAMI.BA", "SEMI.BA", "VIST.BA", "RICH.BA"]

def analizar_activo(ticker):
    try:
        mercado = "ARGENTINA 🇦🇷" if ticker.endswith(".BA") else "USA 🇺🇸"
        t = yf.Ticker(ticker)
        # Bajamos info para Nombre y Sector
        info = t.info
        nombre = info.get('shortName', ticker)
        sector = info.get('sector', 'N/A')
        
        hist = t.history(period="6mo")
        if len(hist) < 25: return None
        
        # Cálculos numéricos
        cp = float(hist['Close'].iloc[-1])
        sma20 = float(hist['Close'].rolling(20).mean().iloc[-1])
        
        # RSI
        delta = hist['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
        
        # ATR y Gestión de Riesgo
        tr = pd.concat([hist['High']-hist['Low'], abs(hist['High']-hist['Close'].shift())], axis=1).max(axis=1)
        atr = float(tr.rolling(14).mean().iloc[-1])
        sl = cp - (atr * 2)
        tp = cp + (atr * 3)
        ratio = 3.0 # Definido por estrategia TP/SL
        
        # Tendencia y Recomendación
        tendencia = "BULL 🐂" if cp > sma20 else ("BEAR 🐻" if cp < sma20 else "NEUTRAL 😐")
        
        if cp > sma20 and 30 < rsi < 70:
            rec = "COMPRAR 💎"
        elif cp > sma20 and rsi > 70:
            rec = "MANTENER/SOBRECOMPRA ⚠️"
        else:
            rec = "ESPERAR ⏳"

        return {
            "Mercado": mercado,
            "Ticker": ticker,
            "Nombre": nombre,
            "Sector": sector,
            "Precio": round(cp, 2),
            "RSI": round(rsi, 2),
            "ATR": round(atr, 2),
            "Stop Loss": round(sl, 2),
            "Take Profit": round(tp, 2),
            "Ratio": ratio,
            "Tendencia": tendencia,
            "Recomendación": rec
        }
    except: return None

if st.button('🚀 EJECUTAR ANÁLISIS COMPLETO'):
    with st.spinner('Analizando datos de mercado, sectores y gestión de riesgo...'):
        todos = USA + ARG
        with ThreadPoolExecutor(max_workers=10) as executor:
            resultados = list(executor.map(analizar_activo, todos))
        
        df = pd.DataFrame([r for r in resultados if r is not None])
        st.success(f"Análisis finalizado para {len(df)} activos.")
        st.dataframe(df, use_container_width=True)
