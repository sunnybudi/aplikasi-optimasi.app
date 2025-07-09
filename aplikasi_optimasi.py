import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

st.set_page_config(page_title="Multi-Model Optimasi Produksi", layout="wide")
st.title("📊 Aplikasi Multi-Model Optimasi Produksi")

model_tabs = st.tabs([
    "Model 1 - Maksimalkan Keuntungan",
    "Model 2 - Minimalkan Biaya",
    "Model 3 - Penuhi Permintaan & Kapasitas",
    "Model 4 - Profit per Jam",
    "Model 5 - Optimasi Operator & Mesin"
])

# Utility function to solve LP and display results
def solve_lp(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None, bounds=None, product_names=None):
    result = linprog(c=c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    if result.success:
        x_opt = np.round(result.x, 2)
        z_val = -result.fun if any(i < 0 for i in c) else result.fun
        st.success("✅ Solusi optimal ditemukan!")
        df = pd.DataFrame({
            "Produk": product_names,
            "Jumlah Optimal": x_opt,
            "Nilai Tujuan per Unit": [abs(ci) for ci in c[:len(product_names)]],
            "Total Nilai": np.round(x_opt * np.abs(c[:len(product_names)]), 2)
        })
        st.dataframe(df)
        st.subheader(f"🎯 Nilai Optimal: Rp {z_val:,.2f}")

        # Bar chart
        fig, ax = plt.subplots(figsize=(8, 4))
        bar1 = ax.bar(product_names, x_opt, color='teal', label="Jumlah Optimal")
        for bar in bar1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f"{height:.2f}", ha='center')
        ax.set_title("Jumlah Produksi Optimal per Produk")
        st.pyplot(fig)
    else:
        st.error("❌ Solusi tidak ditemukan. Periksa input.")

# ---- Tab 1: Maksimalkan Keuntungan ----
with model_tabs[0]:
    st.header("Model 1 - Maksimalkan Keuntungan")
    n = st.number_input("Jumlah Produk", min_value=2, value=2, step=1, key="m1_n")
    names, profits, times = [], [], []
    for i in range(n):
        st.subheader(f"Produk {i+1}")
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"m1_name_{i}")
        with col2:
            profit = st.number_input(f"Keuntungan/unit", value=10.0, key=f"m1_profit_{i}")
        with col3:
            time = st.number_input(f"Waktu kerja/unit (jam)", value=1.0, key=f"m1_time_{i}")
        names.append(name)
        profits.append(profit)
        times.append(time)

    total_time = st.number_input("Total Waktu Tersedia (jam)", value=100.0, key="m1_total_time")

    c = [-p for p in profits]
    A = [times]
    b = [total_time]
    bounds = [(0, None)] * n
    solve_lp(c=c, A_ub=A, b_ub=b, bounds=bounds, product_names=names)

# Tab 2 - Minimalkan Biaya
with model_tabs[1]:
    st.header("Model 2 - Minimalkan Biaya")
    n = st.number_input("Jumlah Produk", min_value=2, value=2, key="m2_n")
    names, costs, demands = [], [], []
    for i in range(n):
        st.subheader(f"Produk {i+1}")
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"m2_name_{i}")
        with col2:
            cost = st.number_input(f"Biaya/unit", value=10.0, key=f"m2_cost_{i}")
        with col3:
            demand = st.number_input(f"Permintaan minimum", value=50.0, key=f"m2_demand_{i}")
        names.append(name)
        costs.append(cost)
        demands.append(demand)

    c = costs
    A = [[-1]*n]  # dummy (no real constraint)
    b = [-1]
    bounds = [(d, None) for d in demands]
    solve_lp(c=c, A_ub=A, b_ub=b, bounds=bounds, product_names=names)

# Tab 3 - Penuhi Permintaan & Kapasitas
with model_tabs[2]:
    st.header("Model 3 - Permintaan & Kapasitas")
    n = st.number_input("Jumlah Produk", min_value=2, value=2, key="m3_n")
    names, profits, demands, times = [], [], [], []
    for i in range(n):
        st.subheader(f"Produk {i+1}")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"m3_name_{i}")
        with col2:
            profit = st.number_input(f"Keuntungan/unit", value=10.0, key=f"m3_profit_{i}")
        with col3:
            demand = st.number_input(f"Permintaan minimum", value=20.0, key=f"m3_demand_{i}")
        with col4:
            time = st.number_input(f"Waktu/unit", value=1.0, key=f"m3_time_{i}")
        names.append(name)
        profits.append(profit)
        demands.append(demand)
        times.append(time)

    capacity = st.number_input("Total Kapasitas Waktu", value=100.0, key="m3_capacity")
    c = [-p for p in profits]
    A = [times]
    b = [capacity]
    bounds = [(d, None) for d in demands]
    solve_lp(c=c, A_ub=A, b_ub=b, bounds=bounds, product_names=names)

# Tab 4 - Profit per Jam
with model_tabs[3]:
    st.header("Model 4 - Efisiensi Profit per Jam")
    n = st.number_input("Jumlah Produk", min_value=2, value=2, key="m4_n")
    names, profits, times = [], [], []
    for i in range(n):
        st.subheader(f"Produk {i+1}")
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"m4_name_{i}")
        with col2:
            profit = st.number_input(f"Keuntungan/unit", value=10.0, key=f"m4_profit_{i}")
        with col3:
            time = st.number_input(f"Waktu kerja/unit", value=1.0, key=f"m4_time_{i}")
        names.append(name)
        profits.append(profit / time)
        times.append(time)

    total_time = st.number_input("Total Waktu Tersedia", value=100.0, key="m4_total_time")
    c = [-p for p in profits]
    A = [times]
    b = [total_time]
    bounds = [(0, None)] * n
    solve_lp(c=c, A_ub=A, b_ub=b, bounds=bounds, product_names=names)

# Tab 5 - Optimasi Operator & Mesin
with model_tabs[4]:
    st.header("Model 5 - Optimasi Operator & Mesin")
    n = st.number_input("Jumlah Produk", min_value=2, value=2, key="m5_n")
    names, profits, op_unit, mc_unit = [], [], [], []
    for i in range(n):
        st.subheader(f"Produk {i+1}")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"m5_name_{i}")
        with col2:
            profit = st.number_input(f"Keuntungan/unit", value=10.0, key=f"m5_profit_{i}")
        with col3:
            op = st.number_input(f"Operator/unit", value=1.0, key=f"m5_op_{i}")
        with col4:
            mc = st.number_input(f"Mesin/unit", value=1.0, key=f"m5_mc_{i}")
        names.append(name)
        profits.append(profit)
        op_unit.append(op)
        mc_unit.append(mc)

    total_op = st.number_input("Total Operator Tersedia", value=100.0, key="m5_total_op")
    total_mc = st.number_input("Total Mesin Tersedia", value=80.0, key="m5_total_mc")
    c = [-p for p in profits]
    A = [op_unit, mc_unit]
    b = [total_op, total_mc]
    bounds = [(0, None)] * n
    solve_lp(c=c, A_ub=A, b_ub=b, bounds=bounds, product_names=names)
