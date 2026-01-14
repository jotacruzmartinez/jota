import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Radar Maestro Golden", layout="wide")
st.title("💎 Radar de Inversiones: El Imán de la Media")

# Listas de activos (USA + ARG)
USA = ["MMM", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AMZN", "AAPL", "BA", "BABA", "BBD", "BCS", "BHP", "BIDU", "BIIB", "BP", "BRK-B", "BSBR", "C", "CAT", "CHTR", "CL", "COST", "CRM", "CSCO", "CVS", "CVX", "DD", "DE", "DIS", "EBAY", "FDX", "GE", "GFI", "GILD", "GLD", "GOOGL", "GS", "HAL", "HD", "HMC", "HON", "HPQ", "HSBC", "IBM", "INTC", "ITUB", "JD", "JNJ", "JPM", "KO", "LLY", "LMT", "MA", "MCD", "MDT", "MELI", "MO", "MRK", "MSFT", "MSI", "MU", "NEM", "NFLX", "NKE", "NVDA", "ORCL", "PBR", "PEP", "PFE", "PG", "PYPL", "QCOM", "RTX", "SBUX", "SCHW", "SLB", "SNAP", "SONY", "SPY", "T", "TGT", "TM", "TSLA", "TSM", "TXN", "UAL", "UNH", "UNP", "V", "VALE", "VZ", "WFC", "WMT", "XOM", "ZM", "QQQ", "DIA", "EEM", "IWM", "XLF", "XLE", "XLU", "XLK", "XLV", "XLP", "XLI", "XLB", "XLC", "GDX", "EWZ", "ARKK", "BITO", "IREN", "RIOT", "MARA", "COIN", "MSTR", "PLTR", "AI", "U", "SNOW", "PATH", "SE", "SHOP", "SPOT", "UBER", "ABNB"]
ARG = ["ALUA.BA", "BBAR.BA", "BMA.BA", "BYMA.BA", "CEPU.BA", "COME.BA", "CRES.BA", "EDN.BA", "GGAL.BA", "LOMA.BA", "MIRG.BA", "PAMP.BA", "SUPV.BA", "TECO2.BA", "TGNO4.BA", "TGSU2.BA", "TRAN.BA", "TXAR.BA", "VALO.BA", "YPFD.BA", "AGRO.BA", "AUSO.BA", "BHIP.BA", "BOLT.BA", "BPAT.BA", "CADO.BA", "CAPX.BA", "CARC.BA", "CECO2.BA", "CELU.BA", "CGPA2.BA", "CTIO.BA", "DGCU2.BA", "DOME.BA", "DYCA.BA", "FERR.BA", "FIPL.BA", "GAMI.BA", "GARO.BA", "GBAN.BA", "GCLA.BA", "GRIM.BA", "HAVA.BA", "INTR.BA", "INVJ.BA", "IRSA.BA", "LEDE.BA", "LONG.BA", "METR.BA", "MOLA.BA", "MOLI.BA", "MORI.BA", "OEST.BA", "PATA.BA", "PATR.BA", "PGR.BA", "RIGO.BA", "ROSE.BA", "SAMI.BA", "SEMI.BA", "VIST.BA", "RICH.BA"]

def analizar_activo(ticker):
    try:
        mercado = "USA 🇺🇸" if not ticker.endswith(".BA") else "ARGENTINA 🇦🇷"
        t = yf.Ticker(ticker)
        hist = t.history(period="6mo")
        if len(hist) < 30: return None
        
        # PRECIO E IMÁN (SMA20)
        cp = float(hist['Close'].iloc[-1])
        sma20 = float(hist['Close'].rolling(20).mean().iloc[-1])
        distancia_a_media = ((cp - sma20) / sma20) * 100
        
        # RSI 14
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
        
        # GESTIÓN DINÁMICA DE RATIO
        tr = pd.concat([hist['High']-hist['Low'], abs(hist['High']-hist['Close'].shift())], axis=1).max(axis=1)
        atr = float(tr.rolling(14).mean().iloc[-1])
        
        # El Stop siempre es Precio - 2 ATR
        stop_loss = cp - (atr * 2)
        # El Take Profit busca el máximo de los últimos 20 días (resistencia real)
        take_profit = float(hist['High'].rolling(20).max().iloc[-1])
        
        # CÁLCULO DEL RATIO REAL (Beneficio / Riesgo)
        riesgo = cp - stop_loss
        beneficio = take_profit - cp
        ratio_final = beneficio / riesgo if riesgo > 0 else 0
        
        tendencia = "ALCISTA 🟢" if cp > sma20 else "BAJISTA 🔴"
        
        # Recomendación basada en el Ratio y el Imán
        if cp > sma20 and 30 < rsi < 60 and ratio_final > 1.2:
            rec = "COMPRAR 💎"
        elif cp < sma20 and rsi < 30:
            rec = "REBOTE PROXIMO ⚡"
        else:
            rec = "ESPERAR ⏳"

        return {
            "Mercado": mercado, "Ticker": ticker, "Precio": round(cp, 2),
            "Media 20": round(sma20, 2), "Dist. Media %": f"{distancia_a_media:.2f}%",
            "RSI": round(rsi, 2), "ATR": round(atr, 2), "Stop Loss": round(stop_loss, 2),
            "Take Profit": round(take_profit, 2), "Ratio": round(ratio_final, 2),
            "Tendencia": tendencia, "Recomendación": rec
        }
    except: return None

if st.button('🚀 EJECUTAR ESCÁNER DINÁMICO'):
    with st.spinner('Midiendo distancias y calculando ratios reales...'):
        todos = USA + ARG
        with ThreadPoolExecutor(max_workers=10) as executor:
            resultados = list(executor.map(analizar_activo, todos))
        
        df = pd.DataFrame([r for r in resultados if r is not None])
        if not df.empty:
            st.success(f"Radar activado sobre {len(df)} activos.")
            # Ordenamos por Ratio para ver las mejores oportunidades arriba
            st.dataframe(df.sort_values("Ratio", ascending=False), use_container_width=True)
