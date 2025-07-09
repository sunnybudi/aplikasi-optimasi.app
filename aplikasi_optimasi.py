import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# Konfigurasi halaman
st.set_page_config(page_title="Optimasi Produksi", layout="wide")
st.title("📦 Optimasi Produksi Maksimal (Linear Programming)")

# Penjelasan model
st.markdown(r"""
### 🧠 Model Linear Programming

Tujuan: Memaksimalkan keuntungan total dari produksi beberapa produk.

#### Fungsi Objektif:
$$
\text{Maksimalkan } Z = p_1x_1 + p_2x_2 + \dots + p_nx_n
$$

#### Dengan Kendala:
$$
a_{1}x_1 + a_{2}x_2 + \dots + a_{n}x_n \leq B
$$

- \(x_i\): jumlah unit produk ke-\(i\) yang diproduksi  
- \(p_i\): keuntungan per unit produk ke-\(i\)  
- \(a_i\): konsumsi sumber daya untuk satu unit produk ke-\(i\)  
- \(B\): total sumber daya tersedia
""")

# ------------------------
# Input
# ------------------------
st.header("1️⃣ Input Parameter")

n_produk = st.number_input("Jumlah Produk", min_value=2, value=2, step=1)

produk_names = []
profit_per_unit = []
resource_per_unit = []

for i in range(n_produk):
    st.subheader(f"🛠️ Produk {i+1}")
    col1, col2, col3 = st.columns(3)
    with col1:
        nama = col1.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}", key=f"nama_{i}")
    with col2:
        profit = col2.number_input(f"Keuntungan/unit {nama}", value=10.0, step=1.0, key=f"profit_{i}")
    with col3:
        resource = col3.number_input(f"Sumber Daya/unit {nama}", value=1.0, step=1.0, key=f"res_{i}")
    
    produk_names.append(nama)
    profit_per_unit.append(profit)
    resource_per_unit.append(resource)

# Total sumber daya tersedia
total_resource = st.number_input("📦 Total Sumber Daya Tersedia", value=100.0, step=1.0)

# ------------------------
# Optimasi
# ------------------------
st.header("2️⃣ Hasil Optimasi")

if st.button("🚀 Jalankan Optimasi"):
    c = [-x for x in profit_per_unit]
    A = [resource_per_unit]
    b = [total_resource]
    bounds = [(0, None) for _ in range(n_produk)]

    result = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method="highs")

    if result.success:
        x_opt = np.round(result.x, 2)
        z_opt = -result.fun
        total_profit = np.multiply(x_opt, profit_per_unit)

        st.success("✅ Solusi optimal ditemukan!")
        st.markdown("### 📊 Hasil Optimasi")
        df = pd.DataFrame({
            "Produk": produk_names,
            "Jumlah Produksi Optimal": x_opt,
            "Keuntungan/unit": profit_per_unit,
            "Total Keuntungan": np.round(total_profit, 2)
        })

        st.dataframe(df)
        st.subheader(f"💰 Total Keuntungan Maksimum: Rp {z_opt:,.2f}")

        # -------------------------
        # Diagram Batang
        # -------------------------
        st.markdown("### 📈 Visualisasi Total Keuntungan per Produk")

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(produk_names, total_profit, color='skyblue')

        for bar, val in zip(bars, total_profit):
            ax.text(bar.get_x() + bar.get_width() / 2, val + 2, f"{val:,.2f}",
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

        ax.set_ylabel("Total Keuntungan")
        ax.set_title("Total Keuntungan per Produk")
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'.replace(",", ".")))
        ax.grid(True, axis='y', linestyle='--', alpha=0.5)

        st.pyplot(fig)
    else:
        st.error("❌ Optimasi gagal. Periksa input Anda.")
