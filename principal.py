import streamlit as st
import v19
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Inversiones Jota", layout="wide")

st.title("💰 Mis Oportunidades de Inversión")
st.write("Presioná el botón para escanear el mercado en tiempo real.")

# Botón para iniciar
if st.button("🚀 Iniciar Escaneo Maestro"):
    with st.spinner("Buscando diamantes en el mercado... esto puede tardar un minuto..."):
        try:
            # Llamamos a la función que está en v19.py
            df_resultados = v19.ejecutar_analisis()
            
            if not df_resultados.empty:
                st.success("¡Escaneo completado!")
                # Mostramos la tabla en la web
                st.dataframe(df_resultados, use_container_width=True)
            else:
                st.warning("No se encontraron datos en este momento.")
        except Exception as e:
            st.error(f"Hubo un error al procesar: {e}")
