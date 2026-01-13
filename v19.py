import yfinance as yf
import pandas as pd
import pandas_ta as ta
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

def ejecutar_analisis():
    # Listas de activos
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
        for ticker in tickers:
            try:
                # Descargamos datos históricos
                df = yf.download(ticker, period="2y", interval="1d", progress=False, auto_adjust=True)
                if df.empty or len(df) < 50: continue
                
                # Obtenemos info de la empresa (Nombre y Rubro)
                info = yf.Ticker(ticker).info
                nombre = info.get('longName', ticker)
                sector = info.get('sector', 'N/A')
                
                if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

                # --- INDICADORES ---
                df['RSI'] = ta.rsi(df['Close'], length=14)
                df['MA20'] = ta.sma(df['Close'], length=20)
                df['EMA200'] = ta.ema(df['Close'], length=200)
                df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)

                p_actual = df['Close'].iloc[-1]
                rsi_val = df['RSI'].iloc[-1]
                ma20 = df['MA20'].iloc[-1]
                ema200 = df['EMA200'].iloc[-1]
                atr_val = df['ATR'].iloc[-1]
                
                # --- CÁLCULOS DE TRADING ---
                take_profit = ma20  # Objetivo a la media móvil de 20
                stop_loss = p_actual - (2 * atr_val) # Stop Loss: 2 veces el ATR
                
                if rsi_val < 35 and p_actual > ema200: estado = "GOLDEN 💎"
                elif rsi_val < 35: estado = "ATENCION 🐻"
                elif rsi_val > 70: estado = "SOBRECOMPRA 🔥"
                else: estado = "NEUTRAL"

                resultados.append({
                    "Mercado": etiqueta_mercado,
                    "Ticker": ticker,
                    "Nombre": nombre,
                    "Sector": sector,
                    "Precio": round(float(p_actual), 2),
                    "RSI": round(float(rsi_val), 2) if not pd.isna(rsi_val) else "N/A",
                    "ATR": round(float(atr_val), 2),
                    "Take Profit": round(float(take_profit), 2),
                    "Stop Loss": round(float(stop_loss), 2),
                    "Tendencia": "BULL 🐂" if p_actual > ema200 else "BEAR 🐻",
                    "Estado": estado
                })
            except Exception as e:
                continue
        return resultados

    final = procesar_mercado(cedears_usa, "USA/CEDEAR") + procesar_mercado(activos_arg, "ARG_LOCAL")
    return pd.DataFrame(final)
