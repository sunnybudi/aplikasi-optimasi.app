import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt

st.set_page_config(page_title="Optimasi Produksi", layout="wide")
st.title("📊 Optimasi Produksi: Kendala Waktu & Operator")

st.markdown("""
Aplikasi ini membantu menentukan kombinasi produksi optimal untuk **memaksimalkan keuntungan** berdasarkan kendala:
- ⏱️ Waktu (jam kerja total)
- 👷 Jumlah operator yang tersedia
""")

# -------------------------------
# Input jumlah produk
# -------------------------------
num_products = st.number_input("🔢 Jumlah Produk", min_value=2, value=2, step=1, key="num_products")

# Reset semua variabel input terkait jumlah produk
if 'data_inputs' not in st.session_state or len(st.session_state.data_inputs) != num_products:
    st.session_state.data_inputs = [
        {
            "name": f"Produk {i+1}",
            "profit": 10.0,
            "time_per_unit": 1.0,
            "operator_per_unit": 1.0
        }
        for i in range(num_products)
    ]

# -------------------------------
# Input data produk
# -------------------------------
st.header("📦 Input Parameter Setiap Produk")

for i in range(num_products):
    with st.expander(f"Produk {i+1}", expanded=True):
        st.session_state.data_inputs[i]["name"] = st.text_input("Nama Produk", st.session_state.data_inputs[i]["name"], key=f"name_{i}")
        st.session_state.data_inputs[i]["profit"] = st.number_input("Keuntungan per Unit (Rp)", min_value=0.0, value=st.session_state.data_inputs[i]["profit"], key=f"profit_{i}")
        st.session_state.data_inputs[i]["time_per_unit"] = st.number_input("Jam Kerja per Unit", min_value=0.0, value=st.session_state.data_inputs[i]["time_per_unit"], key=f"time_{i}")
        st.session_state.data_inputs[i]["operator_per_unit"] = st.number_input("Operator per Unit", min_value=0.0, value=st.session_state.data_inputs[i]["operator_per_unit"], key=f"op_{i}")

# -------------------------------
# Input batas sumber daya
# -------------------------------
st.header("⚙️ Batasan Sumber Daya")
col1, col2 = st.columns(2)
with col1:
    total_time = st.number_input("Total Jam Kerja Tersedia", value=100.0, step=1.0)
with col2:
    total_operator = st.number_input("Total Operator Tersedia", value=80.0, step=1.0)

# -------------------------------
# Hitung optimasi
# -------------------------------
st.header("🚀 Hasil Optimasi")

product_names = [p["name"] for p in st.session_state.data_inputs]
profits = [p["profit"] for p in st.session_state.data_inputs]
times = [p["time_per_unit"] for p in st.session_state.data_inputs]
operators = [p["operator_per_unit"] for p in st.session_state.data_inputs]

# Fungsi objektif (dikalikan -1 karena linprog meminimalkan)
c = [-p for p in profits]
A = [times, operators]
b = [total_time, total_operator]
bounds = [(0, None)] * num_products

# Optimasi
result = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')

if result.success:
    x_opt = np.round(result.x, 2)
    total_profit = -result.fun

    df = pd.DataFrame({
        "Produk": product_names,
        "Jumlah Produksi Optimal": x_opt,
        "Keuntungan per Unit": profits,
        "Total Keuntungan": np.round(np.multiply(x_opt, profits), 2)
    })

    st.success("✅ Solusi Optimal Ditemukan!")
    st.dataframe(df)
    st.subheader(f"💰 Total Keuntungan Maksimum: Rp {total_profit:,.2f}")

    # -------------------------------
    # Visualisasi Grafik
    # -------------------------------
    st.subheader("📊 Visualisasi Kombinasi Produksi")
    fig, ax = plt.subplots(figsize=(10, 4))
    bars = ax.bar(product_names, x_opt, color='lightblue')
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f"{yval:.2f}", ha='center', fontsize=10)
    ax.set_ylabel("Jumlah Produksi")
    ax.set_title("Jumlah Produksi Optimal per Produk")
    st.pyplot(fig)
else:
    st.error("❌ Optimasi gagal. Periksa input dan batasan.")
