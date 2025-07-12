import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpStatus

st.set_page_config(page_title="Optimasi Produksi - Mesin & Operator", layout="wide")
st.title("🔧 Aplikasi Produksi - Mesin & Operator")

# Tabs
tab1, tab2 = st.tabs(["📈 Optimasi Produksi", "📊 Perhitungan Produksi"])

# ---------- Input: SEMUA di SIDEBAR ----------
with st.sidebar:
    st.header("📦 Input Jumlah Produk")
    num_products = st.number_input("Jumlah Produk", min_value=2, value=2, step=1)

    st.header("📥 Input Data Produk")

    product_names = []
    jumlah_produksi = []
    harga_jual = []
    laba_per_unit = []
    mesin_digunakan = []
    operator_per_mesin = []

    for i in range(num_products):
        st.markdown(f"### 🔹 Produk {i+1}")
        name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"name_{i}")
        qty = st.number_input(f"Jumlah Produksi Produk {i+1}", min_value=0, value=0, key=f"qty_{i}")
        harga = st.number_input(f"Harga Jual/unit Produk {i+1}", min_value=0, value=0, key=f"harga_{i}")
        laba = st.number_input(f"Keuntungan/unit Produk {i+1}", min_value=0, value=0, key=f"laba_{i}")
        mesin = st.number_input(f"Jumlah Mesin Produk {i+1}", min_value=0, value=0, key=f"mesin_{i}")
        op_mesin = st.number_input(f"Operator per Mesin Produk {i+1}", min_value=1, value=1, key=f"opmesin_{i}")

        product_names.append(name)
        jumlah_produksi.append(qty)
        harga_jual.append(harga)
        laba_per_unit.append(laba)
        mesin_digunakan.append(mesin)
        operator_per_mesin.append(op_mesin)

# ---------- Perhitungan ----------
def format_rupiah(nilai):
    return f"Rp {nilai:,.0f}".replace(",", ".")

total_penjualan = [harga_jual[i] * jumlah_produksi[i] for i in range(num_products)]
total_keuntungan = [laba_per_unit[i] * jumlah_produksi[i] for i in range(num_products)]
biaya_unit = [harga_jual[i] - laba_per_unit[i] for i in range(num_products)]
total_biaya = [biaya_unit[i] * jumlah_produksi[i] for i in range(num_products)]
total_operator_per_produk = [mesin_digunakan[i] * operator_per_mesin[i] for i in range(num_products)]
efisiensi_per_produk = [
    total_keuntungan[i] / total_operator_per_produk[i] if total_operator_per_produk[i] > 0 else 0
    for i in range(num_products)
]

total_all_penjualan = sum(total_penjualan)
total_all_keuntungan = sum(total_keuntungan)
total_all_biaya = sum(total_biaya)
total_mesin = sum(mesin_digunakan)
total_operator = sum(total_operator_per_produk)
total_all_produksi = sum(jumlah_produksi)

# ---------- Tab 1: Optimasi Produksi ----------
with tab1:
    st.subheader("📈 Optimasi Produksi Berdasarkan Keuntungan Maksimum")
    st.markdown(r"""
    $$
    \text{Maksimalkan } Z = \sum (\text{Laba per unit}_i \times X_i) \\
    \text{dengan kendala:} \\
    \sum (\text{Mesin}_i \times \text{Operator/Mesin}_i \times X_i) \leq \text{Total Operator} \\
    \sum (\text{Mesin}_i \times X_i) \leq \text{Total Mesin}
    $$
    """)

    total_operator_tersedia = st.number_input("Masukkan Total Operator yang Tersedia", min_value=1, value=10)
    total_mesin_tersedia = st.number_input("Masukkan Total Mesin yang Tersedia", min_value=1, value=5)

    if all(laba > 0 for laba in laba_per_unit) and total_operator_tersedia > 0 and total_mesin_tersedia > 0:
        x = [LpVariable(f"x{i+1}", lowBound=0, cat='Integer') for i in range(num_products)]
        model = LpProblem("Optimasi_Produksi", LpMaximize)
        model += lpSum([laba_per_unit[i] * x[i] for i in range(num_products)]), "Total_Keuntungan"
        model += lpSum([mesin_digunakan[i] * operator_per_mesin[i] * x[i] for i in range(num_products)]) <= total_operator_tersedia, "Batas_Operator"
        model += lpSum([mesin_digunakan[i] * x[i] for i in range(num_products)]) <= total_mesin_tersedia, "Batas_Mesin"

        model.solve()

        if LpStatus[model.status] == "Optimal":
            st.success("✅ Solusi optimal ditemukan:")
            for i in range(num_products):
                st.write(f"🔹 {product_names[i]} ➜ Jumlah Optimal: **{int(x[i].value())} unit**")
            st.write(f"💰 Total Keuntungan Maksimal: **{format_rupiah(model.objective.value())}**")
        else:
            st.error("❌ Tidak ada solusi optimal ditemukan. Periksa kembali input dan batasan operator/mesin.")
    else:
        st.info("ℹ️ Masukkan data produk, total operator dan mesin yang tersedia untuk melihat hasil optimasi.")
