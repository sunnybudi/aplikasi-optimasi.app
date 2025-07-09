import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Optimasi Produksi", layout="wide")
st.title("🔧 Optimasi Keuntungan Produksi (Linear Programming)")

st.markdown("Aplikasi ini membantu menentukan jumlah produksi optimal untuk memaksimalkan keuntungan berdasarkan batasan sumber daya.")

# -------------------------
# Input: Jumlah Produk dan Kendala
# -------------------------
st.header("1️⃣ Input Parameter Produksi")

num_products = st.number_input("Jumlah Produk", min_value=2, value=2, step=1)
num_constraints = st.number_input("Jumlah Kendala (misalnya waktu, bahan baku, tenaga kerja)", min_value=1, value=2, step=1)

st.subheader("🧮 Nama Produk dan Keuntungan per Unit")
product_names = []
profits = []

for i in range(num_products):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(f"Nama Produk {i+1}", value=f"Produk {i+1}")
    with col2:
        profit = st.number_input(f"Keuntungan per unit {name}", value=10.0, step=1.0, key=f"profit_{i}")
    product_names.append(name)
    profits.append(profit)

st.subheader("📊 Matriks Koefisien Kendala & RHS (<=)")
A = []
b = []
constraint_labels = []

for i in range(num_constraints):
    cols = st.columns(num_products + 2)
    constraint_row = []
    for j in range(num_products):
        coef = cols[j].number_input(f"Koefisien {product_names[j]} di Kendala {i+1}", value=1.0, step=0.5, key=f"a_{i}_{j}")
        constraint_row.append(coef)
    rhs = cols[-2].number_input(f"RHS Kendala {i+1} (batas maksimum)", value=100.0, step=1.0, key=f"b_{i}")
    label = cols[-1].text_input(f"Nama Kendala {i+1}", value=f"Kendala {i+1}", key=f"label_{i}")
    A.append(constraint_row)
    b.append(rhs)
    constraint_labels.append(label)

# -------------------------
# Optimisasi Linear Programming
# -------------------------
st.header("2️⃣ Hasil Optimasi")

if st.button("🚀 Jalankan Optimasi"):
    c = [-p for p in profits]  # Karena linprog melakukan minimisasi
    A_ub = np.array(A)
    b_ub = np.array(b)
    bounds = [(0, None) for _ in range(num_products)]

    result = linprog(c=c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

    if result.success:
        st.success("✅ Optimasi berhasil ditemukan!")
        produk_optimal = np.round(result.x, 2)
        keuntungan_total = -result.fun

        df_hasil = pd.DataFrame({
            "Produk": product_names,
            "Jumlah Optimal": produk_optimal,
            "Keuntungan per Unit": profits,
            "Total Keuntungan Produk": np.round(np.multiply(produk_optimal, profits), 2)
        })

        st.dataframe(df_hasil)
        st.subheader("💰 Total Keuntungan Maksimum: Rp {:,.2f}".format(keuntungan_total))

        # Simpan hasil ke CSV
        csv = df_hasil.to_csv(index=False).encode()
        st.download_button("⬇️ Unduh Hasil sebagai CSV", csv, file_name="hasil_optimasi.csv", mime="text/csv")

        # Visualisasi jika hanya 2 produk
        if num_products == 2:
            st.subheader("📈 Visualisasi Area Feasible (2 Produk)")
            fig, ax = plt.subplots()
            x = np.linspace(0, max(b) * 1.2, 400)

            for i in range(num_constraints):
                a1, a2 = A[i]
                if a2 != 0:
                    y = (b[i] - a1 * x) / a2
                else:
                    y = np.full_like(x, b[i] / a1)
                ax.plot(x, y, label=constraint_labels[i])

            ax.fill_between(x, 0, np.minimum.reduce([
                np.maximum(0, (b[i] - A[i][0] * x) / A[i][1] if A[i][1] != 0 else np.inf)
                for i in range(num_constraints)
            ]), color='gray', alpha=0.3)

            ax.plot(produk_optimal[0], produk_optimal[1], 'ro', label='Solusi Optimal')
            ax.set_xlabel(product_names[0])
            ax.set_ylabel(product_names[1])
            ax.set_title("Area Feasible dan Titik Optimal")
            ax.legend()
            st.pyplot(fig)
    else:
        st.error("❌ Optimasi gagal ditemukan. Coba ubah parameter.")
