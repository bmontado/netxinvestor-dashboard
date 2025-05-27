
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📈 NetXInvestor Trading Dashboard")

uploaded_file = st.file_uploader("Subí tu archivo de trading (.xlsx) desde NetXInvestor", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    df = pd.read_excel(xls, sheet_name='history')

    for i in range(len(df)):
        if "Action" in df.iloc[i].values:
            header_row_index = i
            break

    df_data = pd.DataFrame(df.values[7:], columns=[
        "Empty", "Date", "Type", "Security ID", "Activity Description", "Net Amount", "Details",
        "Trade Date", "Quantity", "Price", "Principal In Local Currency", "Commission / Fees",
        "Settlement Date", "Principal (Local)", "Commission (Local)", "Net Amount (Local)",
        "Price (Local)", "Cusip", "Payee", "Paid For", "Request Reason"
    ])

    df_data['Trade Date'] = pd.to_datetime(df_data['Trade Date'], errors='coerce')
    df_data['Net Amount'] = pd.to_numeric(df_data['Net Amount'], errors='coerce')

    df_data_valid = df_data.dropna(subset=['Trade Date', 'Net Amount'])

    daily_pnl = df_data_valid.groupby('Trade Date')['Net Amount'].sum().cumsum()

    st.subheader("📊 Evolución del Balance (Equity)")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(daily_pnl.index, daily_pnl.values, marker='o')
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Balance acumulado ($)")
    ax.set_title("Evolución del Equity")
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("📝 Journal de Trading")
    st.dataframe(df_data_valid[['Trade Date', 'Activity Description', 'Net Amount', 'Details']])
else:
    st.info("Por favor, subí un archivo .xlsx para ver tu dashboard.")
