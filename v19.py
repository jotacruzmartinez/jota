import streamlit as st
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Mis Oportunidades de Inversión", layout="wide")
st.title("💰 Mis Oportunidades de Inversión")
st.write("Presioná el botón para escanear el mercado en tiempo real.")

# --- 2. TUS LISTADOS (188 ACCIONES) ---
cedears_usa = [
    "MMM", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AMZN", "AAPL", "BA", "BABA", "BBD", "BCS", "BHP", "BIDU",
    "BIIB", "BP", "BRK-B", "BSBR", "C", "CAT", "CHTR", "CL", "COST", "CRM", "CSCO", "CVS", "CVX", "DD", "DE",
    "DIS", "EBAY", "FDX", "GE", "GFI", "GILD", "GLD", "GOOGL", "GS", "HAL", "HD", "HMC", "HON",
    "HPQ", "HSBC", "IBM", "INTC", "ITUB", "JD", "JNJ", "JPM", "KO", "LLY", "LMT", "MA", "MCD", "MDT", "MELI",
    "MO", "MRK", "MSFT", "MSI", "MU", "NEM", "NFLX", "NKE", "NVDA", "ORCL", "PBR", "PEP", "PFE", "PG",
    "PYPL", "QCOM", "RTX", "SBUX", "SCHW", "SLB", "SNAP", "SONY", "SPY", "T", "TGT", "TM", "TSLA", "TSM",
    "TXN", "UAL", "UNH", "UNP", "V", "VALE", "VZ", "WFC", "WMT", "XOM", "ZM", "QQQ", "DIA", "EEM", "IWM",
    "XLF", "XLE", "XLU", "XLK", "XLV", "XLP", "XLI", "XLB", "XLC", "GDX", "EWZ", "ARKK", "BITO", "IREN",
    "RIOT", "MARA", "COIN", "MSTR", "PLTR", "AI", "U", "SNOW", "PATH", "SE", "SHOP", "SPOT", "UBER", "ABNB"
]

activos_arg = [
    "ALUA.BA", "BBAR.BA", "BMA.BA", "BYMA.BA", "CEPU.BA", "COME.BA", "CRES.BA", "EDN.BA",
    "GGAL.BA", "LOMA.BA", "MIRG.BA", "PAMP.BA", "SUPV.BA", "TECO2.BA", "TGNO4.BA", "TGSU2.BA",
    "TRAN.BA", "TXAR.BA", "VALO.BA", "YPFD.BA", "AGRO.BA", "AUSO.BA", "BHIP.BA", "BOLT.BA",
    "BPAT.BA", "CADO.BA", "CAPX.BA", "CARC.BA", "CECO2.BA", "CELU.BA", "CGPA2.BA",
    "CTIO.BA", "DGCU2.BA", "DOME.BA", "DYCA.BA", "FERR.BA", "FIPL.BA", "GAMI.BA", "GARO.BA",
    "GBAN.BA", "GCLA.BA", "GRIM.BA", "HAVA.BA", "INTR.BA", "INVJ.BA", "IRSA.BA",
    "LEDE.BA", "LONG.BA", "METR.BA", "MOLA.BA", "MOLI.BA", "MORI.BA", "OEST.BA", "PATA.BA",
    "PATR.BA", "PGR.BA", "RIGO.BA", "ROSE.BA", "SAMI.BA", "SEMI.BA", "VIST.BA", "RICH.BA"
]

TODOS_LOS_TICKERS = cedears_usa + activos_arg

# --- 3. EL MOTOR (Aquí se procesan los datos) ---
def procesar_un_solo_activo(ticker):
    try:
        # Descarga rápida de 2 meses
        data = yf.download(ticker, period="2mo", interval="1d", progress=False)
        if data.empty: return None
        
        precio = data['Close'].iloc[-1]
        
        # ACA PODES SUMAR TUS CALCULOS MAS ADELANTE
        return {
            "Ticker": ticker,
            "Precio": round(float(precio), 2),
            "Estado": "Validado ✅"
        }
    except:
        return None

@st.cache_data(ttl=600)
def ejecutar_analisis_maestro(lista):
    # Esto usa 20 "trabajadores" a la vez para que no se trabe
    with ThreadPoolExecutor(max_workers=20) as executor:
        resultados = list(executor.map(procesar_un_solo_activo, lista))
    return [r for r in resultados if r is not None]

# --- 4. LA ACCIÓN ---
if st.button('🚀 Iniciar Escaneo Maestro'):
    with st.spinner('Analizando los 188 activos...'):
        datos_finales = ejecutar_analisis_maestro(TODOS_LOS_TICKERS)
        
        if datos_finales:
            df = pd.DataFrame(datos_finales)
            st.success(f"Se encontraron {len(df)} activos disponibles.")
            st.dataframe(df, use_container_width=True)
        else:
            st.error("No se pudo obtener información. Probá de nuevo.")
