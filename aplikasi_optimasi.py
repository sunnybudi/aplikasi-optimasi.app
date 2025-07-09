import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

st.set_page_config(layout="wide", page_title="Optimasi Produksi")

tab1, = st.tabs(["📦 Optimasi Produksi - Fungsi Z dan Tenaga Kerja"])

with tab1:
    st.title("📈 Optimasi Produksi - Fungsi Z dan Tenaga Kerja")
    st.markdown("""
    Aplikasi ini memaksimalkan keuntungan berdasarkan fungsi:
    \[
    Z = c_1X_1 + c_2X_2 + \dots + c_nX_n
    \]
    dengan kendala total tenaga kerja (operator).
    """)

    num_products = st.number_input("Jumlah Produk", min_value=2, value=2, step=1)

    product_names, laba_unit, harga_jual, tenaga_per_unit = [], [], [], []

    st.subheader("📋 Input Data Produk")
    for i in range(num_products):
        with st.expander(f"Produk {i+1}", expanded=True):
            name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"name_{i}")
            profit = st.number_input(f"Keuntungan per Unit {name}", key=f"laba_{i}", value=10.0)
            harga = st.number_input(f"Harga Jual per Unit {name}", key=f"harga_{i}", value=20.0)
            tenaga = st.number_input(f"Tenaga Kerja / unit {name}", key=f"tenaga_{i}", value=1.0)

        product_names.append(name)
        laba_unit.append(profit)
        harga_jual.append(harga)
        tenaga_per_unit.append(tenaga)

    st.subheader("⚙️ Total Tenaga Kerja (Operator) Tersedia")
    total_operator = st.number_input("Total Operator Tersedia", value=100.0)

    # ================= Optimasi ====================
    st.subheader("🧮 Perhitungan Optimasi Otomatis")

    # Fungsi objektif: Maks Z = c1X1 + c2X2 + ...
    st.latex(
        "Z = " + " + ".join([f"{laba_unit[i]}X_{{{i+1}}}" for i in range(num_products)])
    )
    st.markdown("### Kendala:")
    st.latex(
        " + ".join([f"{tenaga_per_unit[i]}X_{{{i+1}}}" for i in range(num_products)])
        + f" \\leq {total_operator}"
    )

    # Linear Programming
    c = [-p for p in laba_unit]
    A = [tenaga_per_unit]
    b = [total_operator]
    bounds = [(0, None) for _ in range(num_products)]

    result = linprog(c=c, A_ub=A, b_ub=b, bounds=bounds, method="highs")

    if result.success:
        x_opt = np.round(result.x, 2)
        z_total = -result.fun

        df_hasil = pd.DataFrame({
            "Produk": product_names,
            "Jumlah Produksi Optimal": x_opt,
            "Keuntungan/Unit": laba_unit,
            "Tenaga Kerja/Unit": tenaga_per_unit,
            "Total Keuntungan Produk": np.round(x_opt * laba_unit, 2)
        })

        st.success("✅ Solusi optimal ditemukan!")
        st.dataframe(df_hasil)

        st.subheader(f"💰 Total Keuntungan Maksimum: Rp {z_total:,.2f}")

        # ==============================================
        # Grafik batang
        # ==============================================
        st.subheader("📊 Visualisasi Jumlah Produksi Optimal & Keuntungan")
        fig, ax = plt.subplots(figsize=(10, 4))
        x_pos = np.arange(len(product_names))
        width = 0.35

        keuntungan_total = x_opt * laba_unit
        bars1 = ax.bar(x_pos - width/2, x_opt, width=width, label='Jumlah Produksi', color='lightgreen')
        bars2 = ax.bar(x_pos + width/2, keuntungan_total, width=width, label='Total Keuntungan', color='skyblue')

        max_val = max(np.max(x_opt), np.max(keuntungan_total))
        ax.set_ylim(0, max_val * 1.3)

        for bars in [bars1, bars2]:
            for bar in bars:
                val = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, val + (max_val * 0.05), f"{val:.2f}",
                        ha='center', va='bottom', fontsize=9)

        ax.set_xticks(x_pos)
        ax.set_xticklabels(product_names)
        ax.set_ylabel("Unit / Rupiah")
        ax.set_title("Produksi & Keuntungan Optimal per Produk")
        ax.legend()
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}".replace(",", ".")))
        st.pyplot(fig)

        # ==============================================
        # Prioritas Produksi (berdasarkan efisiensi)
        # ==============================================
        st.subheader("🧠 Produk Prioritas untuk Diproduksi Lebih Dahulu")
        df_eff = pd.DataFrame({
            "Produk": product_names,
            "Efisiensi (Keuntungan per Operator)": np.round(np.array(laba_unit) / np.array(tenaga_per_unit), 2)
        }).sort_values(by="Efisiensi (Keuntungan per Operator)", ascending=False)

        st.dataframe(df_eff)
        st.markdown(f"✅ **Produk yang sebaiknya diproduksi lebih dahulu:** `{df_eff.iloc[0]['Produk']}`")
    else:
        st.error("❌ Optimasi gagal. Periksa kembali input.")
