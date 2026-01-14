import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time

st.set_page_config(page_title="Radar Maestro Golden", layout="wide")
st.title("💰 Mis Oportunidades de Inversión")

# Lista de activos reducida para prueba inicial rápida (luego podés expandirla)
TODOS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "GGAL.BA", "YPFD.BA", "PAMP.BA", "ALUA.BA"]

def analizar_activo(ticker):
    try:
        # Añadimos una pequeña pausa para no saturar el servidor
        time.sleep(0.1) 
        data = yf.download(ticker, period="1mo", interval="1d", progress=False)
        
        if data.empty or len(data) < 10:
            return None
        
        # Usamos .iloc[-1] con .item() para extraer solo el valor numérico puro
        precio = float(data['Close'].iloc[-1].item())
        sma20 = float(data['Close'].rolling(20).mean().iloc[-1].item())
        
        # RSI 14 simplificado y limpio
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi_val = 100 - (100 / (1 + (gain.iloc[-1].item() / loss.iloc[-1].item())))
        
        # ATR y Stop Loss (ATR x 2)
        tr = pd.concat([data['High']-data['Low'], abs(data['High']-data['Close'].shift())], axis=1).max(axis=1)
        atr = float(tr.rolling(14).mean().iloc[-1].item())
        sl = precio - (atr * 2)
        
        estado = "GOLDEN 💎" if precio > sma20 and 30 < rsi_val < 70 else ("BULL 🐂" if precio > sma20 else "BEAR 🐻")

        return {
            "Ticker": ticker,
            "Precio": round(precio, 2),
            "RSI": round(rsi_val, 2),
            "Stop Loss": round(sl, 2),
            "Estado": estado
        }
    except Exception as e:
        return None

if st.button('🚀 EJECUTAR ESCÁNER MAESTRO'):
    with st.spinner('Obteniendo datos en tiempo real...'):
        resultados = []
        # Lo hacemos uno por uno para asegurar que no falle la conexión
        for ticker in TODOS:
            res = analizar_activo(ticker)
            if res:
                resultados.append(res)
        
        if resultados:
            df = pd.DataFrame(resultados)
            st.success(f"Escaneo completado.")
            st.dataframe(df.sort_values("Estado", ascending=False), use_container_width=True)
        else:
            st.error("Error de conexión con el mercado. Reintentá en unos segundos.")
