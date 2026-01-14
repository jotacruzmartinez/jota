import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Estrategia Golden - Radar Maestro", layout="wide")

# Listado de Tickers (Tus 188 activos)
cedears_usa = ["MMM", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AMZN", "AAPL", "BA", "BABA", "BBD", "BCS", "BHP", "BIDU", "BIIB", "BP", "BRK-B", "BSBR", "C", "CAT", "CHTR", "CL", "COST", "CRM", "CSCO", "CVS", "CVX", "DD", "DE", "DIS", "EBAY", "FDX", "GE", "GFI", "GILD", "GLD", "GOOGL", "GS", "HAL", "HD", "HMC", "HON", "HPQ", "HSBC", "IBM", "INTC", "ITUB", "JD", "JNJ", "JPM", "KO", "LLY", "LMT", "MA", "MCD", "MDT", "MELI", "MO", "MRK", "MSFT", "MSI", "MU", "NEM", "NFLX", "NKE", "NVDA", "ORCL", "PBR", "PEP", "PFE", "PG", "PYPL", "QCOM", "RTX", "SBUX", "SCHW", "SLB", "SNAP", "SONY", "SPY", "T", "TGT", "TM", "TSLA", "TSM", "TXN", "UAL", "UNH", "UNP", "V", "VALE", "VZ", "WFC", "WMT", "XOM", "ZM", "QQQ", "DIA", "EEM", "IWM", "XLF", "XLE", "XLU", "XLK", "XLV", "XLP", "XLI", "XLB", "XLC", "GDX", "EWZ", "ARKK", "BITO", "IREN", "RIOT", "MARA", "COIN", "MSTR", "PLTR", "AI", "U", "SNOW", "PATH", "SE", "SHOP", "SPOT", "UBER", "ABNB"]
activos_arg = ["ALUA.BA", "BBAR.BA", "BMA.BA", "BYMA.BA", "CEPU.BA", "COME.BA", "CRES.BA", "EDN.BA", "GGAL.BA", "LOMA.BA", "MIRG.BA", "PAMP.BA", "SUPV.BA", "TECO2.BA", "TGNO4.BA", "TGSU2.BA", "TRAN.BA", "TXAR.BA", "VALO.BA", "YPFD.BA", "AGRO.BA", "AUSO.BA", "BHIP.BA", "BOLT.BA", "BPAT.BA", "CADO.BA", "CAPX.BA", "CARC.BA", "CECO2.BA", "CELU.BA", "CGPA2.BA", "CTIO.BA", "DGCU2.BA", "DOME.BA", "DYCA.BA", "FERR.BA", "FIPL.BA", "GAMI.BA", "GARO.BA", "GBAN.BA", "GCLA.BA", "GRIM.BA", "HAVA.BA", "INTR.BA", "INVJ.BA", "IRSA.BA", "LEDE.BA", "LONG.BA", "METR.BA", "MOLA.BA", "MOLI.BA", "MORI.BA", "OEST.BA", "PATA.BA", "PATR.BA", "PGR.BA", "RIGO.BA", "ROSE.BA", "SAMI.BA", "SEMI.BA", "VIST.BA", "RICH.BA"]
TODOS_LOS_TICKERS = cedears_usa + activos_arg

# --- 2. CÁLCULOS TÉCNICOS ---
def calcular_indicadores(df, ticker):
    # Necesitamos al menos 20 días para la Media y 14 para RSI
    close = df['Close']
    
    # 1. Media Móvil (20 períodos)
    sma = close.rolling(window=20).mean().iloc[-1]
    
    # 2. RSI (14 períodos)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs.iloc[-1]))
    
    # 3. ATR (14 períodos)
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    atr = true_range.rolling(14).mean().iloc[-1]
    
    # 4. Lógica de Salidas
    precio_actual = close.iloc[-1]
    stop_loss = precio_actual - (atr * 2)
    take_profit = precio_actual + (atr * 3) # Ajustar según tu ratio R/B
    
    # 5. Tendencia y Estrategia
    tendencia = "BULL 🐂" if precio_actual > sma else "BEAR 🐻"
    estrategia = "GOLDEN 💎" if (tendencia == "BULL 🐂" and rsi < 70 and rsi > 30) else "ESPERAR"

    return {
        "Mercado": "ARG" if ".BA" in ticker else "USA",
        "Ticker": ticker,
        "Precio": round(float(precio_actual), 2),
        "Media Móvil": round(float(sma), 2),
        "RSI": round(float(rsi), 2),
        "ATR": round(float(atr), 2),
        "Stop Loss": round(float(stop_loss), 2),
        "Take Profit": round(float(take_profit), 2),
        "Tendencia": tendencia,
        "Estrategia": estrategia
    }

def procesar_activo(ticker):
    try:
        data = yf.download(ticker, period="3mo", interval="1d", progress=False)
        if len(data) < 20: return None
        return calcular_indicadores(data, ticker)
    except:
        return None

@st.cache_data(ttl=600)
def ejecutar_radar_completo(lista):
    with ThreadPoolExecutor(max_workers=20) as executor:
        resultados = list(executor.map(procesar_activo, lista))
    return [r for r in resultados if r is not None]

# --- 3. INTERFAZ ---
st.title("🚀 Panel Maestro de Oportunidades")

if st.button('Iniciar Escaneo de 188 Activos'):
    with st.spinner('Calculando métricas avanzadas...'):
        datos = ejecutar_radar_completo(TODOS_LOS_TICKERS)
        if datos:
            df_final = pd.DataFrame(datos)
            st.success(f"Análisis completado para {len(df_final)} activos.")
            # Ordenamos para que las GOLDEN aparezcan arriba
            df_final = df_final.sort_values(by="Estrategia", ascending=False)
            st.dataframe(df_final, use_container_width=True)
        else:
            st.error("Error al conectar con el mercado.")
