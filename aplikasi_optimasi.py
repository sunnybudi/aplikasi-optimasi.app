import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

st.set_page_config(page_title="Optimasi Produksi dengan Batas Waktu", layout="wide")
st.title("🕒 Optimasi Produksi dengan Kendala Waktu Kerja")

st.markdown(r"""
### 🧠 Fungsi Objektif:
$$
\text{Maksimalkan: } Z = \sum_{i=1}^{n} p_i x_i
$$

### 🔒 Kendala:
$$
\sum_{i=1}^{n} t_i x_i \leq T
$$

Dimana:
- \(p_i\) = keuntungan per unit
- \(t_i\) = waktu kerja per unit
- \(T\) = total waktu tersedia
""")

# -------------------------
# Input Produk
# -------------------------
st.header("1️⃣ Input Data Produk")

num_products = st.number_input("Jumlah Produk", min_value=2, value=2, step=1)

product_names = []
profits = []
time_per_unit = []

for i in range(num_products):
    st.subheader(f"📦 Produk {i+1}")
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"name_{i}")
    with col2:
        profit = st.number_input(f"Keuntungan/unit ({name})", value=10.0, step=1.0, key=f"profit_{i}")
    with col3:
        time = st.number_input(f"Waktu kerja/unit ({name}) (jam)", value=2.0, step=0.5, key=f"time_{i}")

    product_names.append(name)
    profits.append(profit)
    time_per_unit.append(time)

# -------------------------
# Input Total Waktu
# -------------------------
st.header("2️⃣ Total Waktu Kerja yang Tersedia")

total_time = st.number_input("Total Waktu Kerja (jam)", value=100.0, step=1.0)

# -------------------------
# Optimisasi
# -------------------------
st.header("3️⃣ Hasil Optimasi")

if all(p > 0 for p in profits) and total_time > 0:
    c = [-p for p in profits]
    A = [time_per_unit]
    b = [total_time]
    bounds = [(0, None) for _ in range(num_products)]

    result = linprog(c=c, A_ub=A, b_ub=b, bounds=bounds, method="highs")

    if result.success:
        x_opt = np.round(result.x, 2)
        z_max = -result.fun
        total_profit = np.round(np.multiply(x_opt, profits), 2)

        df_result = pd.DataFrame({
            "Produk": product_names,
            "Jumlah Optimal": x_opt,
            "Keuntungan/unit": profits,
            "Waktu/unit (jam)": time_per_unit,
            "Total Keuntungan": total_profit
        })

        st.dataframe(df_result)
        st.subheader(f"💰 Total Keuntungan Maksimum: Rp {z_max:,.2f}")

        # Grafik batang
        st.subheader("📊 Grafik Produksi & Keuntungan")
        x_pos = np.arange(len(product_names))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, 5))
        bar1 = ax.bar(x_pos - width/2, total_profit, width=width, color='steelblue', label='Total Keuntungan')
        bar2 = ax.bar(x_pos + width/2, x_opt, width=width, color='seagreen', label='Jumlah Produksi')

        max_val = max(np.max(total_profit), np.max(x_opt)) * 1.3
        ax.set_ylim(0, max_val)

        for bars in [bar1, bar2]:
            for bar in bars:
                val = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, val + 0.5, f'{val:,.2f}',
                        ha='center', va='bottom', fontsize=9)

        ax.set_xticks(x_pos)
        ax.set_xticklabels(product_names)
        ax.set_ylabel("Nilai")
        ax.set_title("Produksi & Keuntungan Optimal")
        ax.legend()
        ax.grid(True, axis='y', linestyle='--', alpha=0.4)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", ".")))

        st.pyplot(fig)

    else:
        st.error("❌ Optimasi gagal. Periksa input datanya.")
else:
    st.info("🔄 Masukkan semua data produk dan total waktu kerja untuk menampilkan hasil optimasi.")
