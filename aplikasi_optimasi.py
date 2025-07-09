import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt

st.set_page_config(page_title="Optimasi Produksi", layout="wide")
st.title("👷‍♂️ Optimasi Produksi Berdasarkan Operator & Mesin")

st.markdown("Aplikasi ini menghitung kombinasi produksi produk untuk memaksimalkan keuntungan berdasarkan jumlah **operator** dan **mesin** yang tersedia.")

# -------------------------
# Input Produk & Keuntungan
# -------------------------
st.header("1️⃣ Input Parameter Produksi")

num_products = st.number_input("Jumlah Produk", min_value=2, value=2, step=1)

product_names = []
profits = []
operator_per_unit = []
machine_per_unit = []

for i in range(num_products):
    st.subheader(f"📦 Produk {i+1}")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"name_{i}")
    with col2:
        profit = col2.number_input(f"Keuntungan/unit {name}", value=10.0, step=1.0, key=f"profit_{i}")
    with col3:
        op = col3.number_input(f"Operator/unit {name}", value=1.0, step=1.0, key=f"op_{i}")
    with col4:
        machine = col4.number_input(f"Mesin/unit {name}", value=1.0, step=1.0, key=f"machine_{i}")

    product_names.append(name)
    profits.append(profit)
    operator_per_unit.append(op)
    machine_per_unit.append(machine)

# -------------------------
# Input Ketersediaan Sumber Daya
# -------------------------
st.header("2️⃣ Ketersediaan Sumber Daya")

col_op, col_mc = st.columns(2)
total_operator = col_op.number_input("Jumlah Total Operator Tersedia", value=100.0, step=1.0)
total_machine = col_mc.number_input("Jumlah Total Mesin Tersedia", value=80.0, step=1.0)

# -------------------------
# Optimisasi
# -------------------------
st.header("3️⃣ Hasil Optimasi")

if st.button("🚀 Jalankan Optimasi"):
    # Fungsi objektif
    c = [-p for p in profits]

    # Kendala matriks: operator dan mesin
    A = [
        operator_per_unit,  # Operator constraint
        machine_per_unit    # Mesin constraint
    ]
    b = [total_operator, total_machine]
    bounds = [(0, None) for _ in range(num_products)]

    result = linprog(c=c, A_ub=A, b_ub=b, bounds=bounds, method="highs")

    if result.success:
        st.success("✅ Solusi optimal ditemukan!")
        produk_optimal = np.round(result.x, 2)
        keuntungan_total = -result.fun

        df_hasil = pd.DataFrame({
            "Produk": product_names,
            "Jumlah Optimal": produk_optimal,
            "Keuntungan per Unit": profits,
