import streamlit as st
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Estrategia Golden - Radar", layout="wide")

# --- TUS LISTADOS ACTUALIZADOS ---
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

# --- MOTOR DE DESCARGA RÁPIDA (CONCURRENTE) ---
@st.cache_data(ttl=600)  # Mantiene los datos frescos cada 10 minutos
def escanear_mercado(lista_tickers):
    def procesar_activo(ticker):
        try:
            # Bajamos solo 2 meses de historia para que sea liviano
            data = yf.download(ticker, period="2mo", interval="1d", progress=False)
            if data.empty:
                return None
            
            ultimo_precio = data['Close'].iloc[-1]
            
            # --- AQUÍ PODÉS AGREGAR TUS LÓGICAS DE RSI / ATR ---
            # Ejemplo simple:
            return {
                "Ticker": ticker,
                "Precio": round(float(ultimo_precio), 2),
                "Mercado": "ARG" if ".BA" in ticker else "USA",
                "Estado": "Análizado ✅"
            }
        except Exception:
            return None

    # Usamos 20 "trabajadores" en simultáneo para no perder tiempo
    with ThreadPoolExecutor(max_workers=20) as executor:
        resultados = list(executor.map(procesar_activo, lista_tickers))
    
    # Filtramos los que dieron error y armamos la tabla
    exitosos = [r for r in resultados if r is not None]
    return pd.DataFrame(exitosos)

# --- INTERFAZ ---
st.title("💎 Estrategia Golden - Radar de Mercado")
st.write(f"Total de activos a monitorear: **{len(TODOS_LOS_TICKERS)}**")

if st.button('🚀 EJECUTAR ESCÁNER'):
    with st.spinner('Analizando el tablero de juego...'):
        df_final = escanear_mercado(TODOS_LOS_TICKERS)
        
        if not df_final.empty:
            st.success(f"Escaneo completado. Se detectaron {len(df_final)} activos activos.")
            
            # Buscador simple
            busqueda = st.text_input("Buscar Ticker específico:")
            if busqueda:
                df_final = df_final[df_final['Ticker'].str.contains(busqueda.upper())]
            
            st.table(df_final) # st.table es más estable para ver muchos datos
        else:
            st.error("No se pudieron obtener datos. Reintentá en unos segundos.")
else:
    st.info("Presioná el botón para obtener la validación de precios actual.")
