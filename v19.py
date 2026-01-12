import yfinance as yf
import pandas as pd
import pandas_ta as ta
import warnings
import os
import time
from datetime import datetime

warnings.filterwarnings("ignore")

# --- LISTADOS ACTUALIZADOS (Limpiamos los que tiraron error de delistado) ---
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

def procesar_mercado(tickers, etiqueta_mercado):
    resultados = []
    print(f"\nProcesando mercado: {etiqueta_mercado}...")
    for ticker in tickers:
        try:
            df = yf.download(ticker, period="2y", interval="1d", progress=False, auto_adjust=True)
            if df.empty or len(df) < 50: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

            # --- INDICADORES ---
            df['RSI'] = ta.rsi(df['Close'], length=14)
            df['MA20'] = ta.sma(df['Close'], length=20)
            df['EMA200'] = ta.ema(df['Close'], length=200)
            df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)

            p_actual = df['Close'].iloc[-1]
            rsi_val = df['RSI'].iloc[-1]
            ma20 = df['MA20'].iloc[-1]
            atr = df['ATR'].iloc[-1]
            ema200 = df['EMA200'].iloc[-1]
            
            tp = ma20
            sl = p_actual - (2 * atr)
            beneficio = tp - p_actual
            riesgo = p_actual - sl
            ratio = beneficio / riesgo if riesgo > 0 else 0
            
            if rsi_val < 35 and p_actual > ema200: estado = "GOLDEN 💎"
            elif rsi_val < 35: estado = "ATENCION 🐻"
            elif rsi_val > 70: estado = "SOBRECOMPRA 🔥"
            else: estado = "NEUTRAL"

            resultados.append({
                "Fecha": datetime.now().strftime('%Y-%m-%d'),
                "Mercado": etiqueta_mercado,
                "Ticker": ticker,
                "Precio": round(float(p_actual), 2),
                "RSI": round(float(rsi_val), 2),
                "ATR": round(float(atr), 2),
                "MA20_TP": round(float(tp), 2),
                "SL_2ATR": round(float(sl), 2),
                "Ratio_BR": round(float(ratio), 2),
                "Tendencia": "BULL 🐂" if p_actual > ema200 else "BEAR 🐻",
                "Estado": estado
            })
            
            if estado == "GOLDEN 💎":
                print(f"⭐ {ticker:<8} | RSI: {rsi_val:>4.1f} | Ratio: {ratio:>4.2f}")

        except Exception:
            continue
    return resultados

# --- EJECUCIÓN ---
ahora = datetime.now().strftime('%Y-%m-%d_%H-%M')
print("="*80)
print(f"🚀 INICIANDO ESCANEO MAESTRO UNIFICADO - {ahora}")
print("="*80)

# Asegurar que la carpeta existe ANTES de procesar
if not os.path.exists("DATA_MASTER"):
    os.makedirs("DATA_MASTER")

todo_junto = procesar_mercado(cedears_usa, "USA/CEDEAR") + procesar_mercado(activos_arg, "ARG_LOCAL")

if todo_junto:
    df_final = pd.DataFrame(todo_junto)
    ruta = f"DATA_MASTER/Master_Analisis_{ahora}.xlsx"
    df_final.to_excel(ruta, index=False)
    print("\n" + "="*80)
    print(f"✅ EXITO: {len(todo_junto)} activos guardados en {ruta}")
    print("="*80)
else:
    print("❌ No se recolectaron datos.")
