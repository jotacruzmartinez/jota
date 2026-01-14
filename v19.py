import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# --- 1. CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="Estrategia Golden - Radar Oficial", layout="wide")
st.title("💎 Radar de Inversiones: Estrategia Golden")
st.write("Versión Beta - Sistema de Análisis en Tiempo Real")

# --- 2. LISTADO COMPLETO (188 ACTIVOS) ---
cedears_usa = ["MMM", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AMZN", "AAPL", "BA", "BABA", "BBD", "BCS", "BHP", "BIDU", "BIIB", "BP", "BRK-B", "BSBR", "C", "CAT", "CHTR", "CL", "COST", "CRM", "CSCO", "CVS", "CVX", "DD", "DE", "DIS", "EBAY", "FDX", "GE", "GFI", "GILD", "GLD", "GOOGL", "GS", "HAL", "HD", "HMC", "HON", "HPQ", "HSBC", "IBM", "INTC", "ITUB", "JD", "JNJ", "JPM", "KO", "LLY", "LMT", "MA", "MCD", "MDT", "MELI", "MO", "MRK", "MSFT", "MSI", "MU", "NEM", "NFLX", "NKE", "NVDA", "ORCL", "PBR", "PEP", "PFE", "PG", "PYPL", "QCOM", "RTX", "SBUX", "SCHW", "SLB", "SNAP", "SONY", "SPY", "T", "TGT", "TM", "TSLA", "TSM", "TXN", "UAL", "UNH", "UNP", "V", "VALE", "VZ", "WFC", "WMT", "XOM", "ZM", "QQQ", "DIA", "EEM", "IWM", "XLF", "XLE", "XLU", "XLK", "XLV", "XLP", "XLI", "XLB", "XLC", "GDX", "EWZ", "ARKK", "BITO", "IREN", "RIOT", "MARA", "COIN", "MSTR", "PLTR", "AI", "U", "SNOW", "PATH", "SE", "SHOP", "SPOT", "UBER", "ABNB"]
activos_arg = ["ALUA.BA", "BBAR.BA", "BMA.BA", "BYMA.BA", "CEPU.BA", "COME.BA", "CRES.BA", "EDN.BA", "GGAL.BA", "LOMA.BA", "MIRG.BA", "PAMP.BA", "SUPV.BA", "TECO2.BA", "TGNO4.BA", "TGSU2.BA", "TRAN.BA", "TXAR.BA", "VALO.BA", "YPFD.BA", "AGRO.BA", "AUSO.BA", "BHIP.BA", "BOLT.BA", "BPAT.BA", "CADO.BA", "CAPX.BA", "CARC.BA", "CECO2.BA", "CELU.BA", "CGPA2.BA", "CTIO.BA", "DGCU2.BA", "DOME.BA", "DYCA.BA", "FERR.BA", "FIPL.BA", "GAMI.BA", "GARO.BA", "GBAN.BA", "GCLA.BA", "GRIM.BA", "HAVA.BA", "INTR.BA", "INVJ.BA", "IRSA.BA", "LEDE.BA", "LONG.BA", "METR.BA", "MOLA.BA", "MOLI.BA", "MORI.BA", "OEST.BA", "PATA.BA", "PATR.BA", "PGR.BA", "RIGO.BA", "ROSE.BA", "SAMI.BA", "SEMI.BA", "VIST.BA", "RICH.BA"]
TODOS_LOS_TICKERS = cedears_usa + activos_arg

# --- 3. EL MOTOR TÉCNICO ---
def analizar_activo(ticker):
    try:
        # Descargamos datos (3 meses para tener historia suficiente)
        data = yf.download(ticker, period="3mo", interval="1d", progress=False)
        if len(data) < 25: return None
        
        # Información Básica
        info = yf.Ticker(ticker)
        nombre = info.info.get('longName', 'N/A')
        industria = info.info.get('industry', 'N/A')
        
        close = data['Close']
        precio_actual = float(close.iloc[-1])
        
        # 1. Media Móvil (20 períodos)
        sma = float(close.rolling(window=20).mean().iloc[-1])
        
        # 2. RSI (14 períodos)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = float(100 - (100 / (1 + (gain / loss).iloc[-1])))
        
        # 3. ATR (14 períodos)
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = float(true_range.rolling(14).mean().iloc[-1])
        
        # 4. Gestión de Riesgo
        stop_loss = precio_actual - (atr * 2)
        take_profit = precio_actual + (atr * 3)
        
        # 5. Tendencia y Estrategia
        tendencia = "BULL 🐂" if precio_actual > sma else "BEAR 🐻"
        # Estrategia según tus manuales (Página 13)
        estrategia = "GOLDEN 💎" if (tendencia == "BULL 🐂" and 30 < rsi < 70) else tendencia

        return {
            "Mercado": "ARG" if ".BA" in ticker else "USA",
            "Ticker": ticker,
            "Empresa": nombre,
            "Industria": industria,
            "Precio": round(precio_actual, 2),
            "SMA 20": round(sma, 2),
            "RSI": round(rsi, 2),
            "ATR": round(atr, 2),
            "Stop Loss": round(stop_loss, 2),
            "Take Profit": round(take_profit, 2),
            "Tendencia": tendencia,
            "Estrategia": estrategia
        }
    except:
        return None

@st.cache_data(ttl=600)
def ejecutar_analisis_paralelo(lista):
    # 20 trabajadores para procesar los 188 activos en segundos
    with ThreadPoolExecutor(max_workers=20) as executor:
        resultados = list(executor.map(analizar_activo, lista))
    return [r for r in resultados if r is not None]

# --- 4. ACCIÓN ---
if st.button('🚀 EJECUTAR ESCÁNER MAESTRO'):
    with st.spinner('Procesando datos del mercado global...'):
        lista_final = ejecutar_analisis_paralelo(TODOS_LOS_TICKERS)
        
        if lista_final:
            df = pd.DataFrame(lista_final)
            st.success(f"Análisis exitoso: {len(df)} activos validados.")
            
            # Reordenar para que las GOLDEN aparezcan primero
            df = df.sort_values(by="Estrategia", ascending=False)
            
            # Mostrar tabla con todas tus columnas requeridas
            st.dataframe(df, use_container_width=True)
        else:
            st.error("No se pudieron recuperar datos. Verificá tu conexión.")
