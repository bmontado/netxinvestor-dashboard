# trading_dashboard_app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📘 NetXInvestor Trading Dashboard")

view_option = st.sidebar.radio("Seleccioná vista", ["Realized PnL", "Resumen Detallado"])

uploaded_file = st.file_uploader("Subí tu archivo de ganancias y pérdidas realizadas (.xlsx)", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    df_preview = pd.read_excel(xls, sheet_name='RGL')

    # Forzar el encabezado correcto según formato conocido
    header_row_index = 19
    df_data = pd.read_excel(uploaded_file, sheet_name='RGL', header=header_row_index)
    df_data.columns = df_data.columns.str.strip()

    # Mostrar columnas disponibles para debug si falla
    st.write("Columnas detectadas:", df_data.columns.tolist())

    # Renombrar columnas manualmente para que encajen con lo que se espera
    df_data = df_data.rename(columns={
        df_data.columns[1]: 'Symbol',
        df_data.columns[4]: 'Gain/Loss',
        df_data.columns[6]: 'Open Date',
        df_data.columns[8]: 'Close Date'
    })

    if 'Symbol' in df_data.columns and 'Gain/Loss' in df_data.columns:
        df_data = df_data.dropna(subset=['Symbol', 'Gain/Loss'], how='any')

        for col in ['Gain/Loss', 'Proceeds', 'Cost']:
            if col in df_data.columns:
                df_data[col] = df_data[col].replace({'\\$': '', ',': ''}, regex=True).astype(float)

        df_data['Open Date'] = pd.to_datetime(df_data.get('Open Date'), errors='coerce')
        df_data['Close Date'] = pd.to_datetime(df_data.get('Close Date'), errors='coerce')
        df_data['Duration (days)'] = (df_data['Close Date'] - df_data['Open Date']).dt.days

        if view_option == "Realized PnL":
            st.subheader("📊 PnL por Activo")
            pnl_by_symbol = df_data.groupby("Symbol")['Gain/Loss'].sum().sort_values(ascending=False)
            st.bar_chart(pnl_by_symbol)

            st.subheader("📈 PnL Acumulado por Fecha")
            pnl_by_date = df_data.groupby("Close Date")['Gain/Loss'].sum().cumsum()
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(pnl_by_date.index, pnl_by_date.values, marker='o')
            ax.set_title("PnL Acumulado")
            ax.set_xlabel("Fecha")
            ax.set_ylabel("PnL ($)")
            ax.grid(True)
            st.pyplot(fig)

            st.subheader("📋 Resumen de Trades")
            st.dataframe(df_data[['Symbol', 'Gain/Loss', 'Open Date', 'Close Date', 'Duration (days)', 'Term']])

        elif view_option == "Resumen Detallado":
            st.subheader("🔍 Análisis Detallado del Rendimiento")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Ganancia Total", f"${df_data['Gain/Loss'].sum():,.2f}")
            col2.metric("# Trades Ganadores", (df_data['Gain/Loss'] > 0).sum())
            col3.metric("# Trades Perdidos", (df_data['Gain/Loss'] < 0).sum())
            col4.metric("Duración Promedio", f"{df_data['Duration (days)'].mean():.1f} días")

            st.subheader("🏆 Top 10 Activos con Mayor Ganancia")
            top_gainers = df_data.groupby('Symbol')['Gain/Loss'].sum().sort_values(ascending=False).head(10)
            st.bar_chart(top_gainers)

            st.subheader("⚠️ Top 10 Activos con Mayor Pérdida")
            top_losers = df_data.groupby('Symbol')['Gain/Loss'].sum().sort_values().head(10)
            st.bar_chart(top_losers)

            st.subheader("📆 Duración Promedio por Activo")
            avg_duration = df_data.groupby('Symbol')['Duration (days)'].mean().sort_values(ascending=False)
            st.dataframe(avg_duration.reset_index().rename(columns={'Duration (days)': 'Duración Promedio'}))
    else:
        st.error("No se encontraron las columnas necesarias: 'Symbol' y 'Gain/Loss'. Verificá el formato del archivo.")
else:
    st.info("Subí un archivo exportado de NetXInvestor para comenzar.")
