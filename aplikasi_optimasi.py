import streamlit as st
from scipy.optimize import linprog
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Optimasi Produksi Sederhana", layout="centered")
st.title("🧮 Optimasi Produksi Sederhana (2 Produk)")

st.markdown("""
Aplikasi ini memaksimalkan keuntungan produksi 2 produk dengan rumus:

\[
\\text{Maximize } Z = c_1X + c_2Y
\]

dengan kendala:

\[
a_1X + a_2Y \\leq R
\]
""")

# Input pengguna
st.subheader("📦 Input Parameter")

c1 = st.number_input("Keuntungan/unit Produk X (c₁)", value=20.0)
c2 = st.number_input("Keuntungan/unit Produk Y (c₂)", value=30.0)

a1 = st.number_input("Sumber daya/unit Produk X (a₁)", value=4.0)
a2 = st.number_input("Sumber daya/unit Produk Y (a₂)", value=3.0)

R = st.number_input("Total Sumber Daya Tersedia (R)", value=120.0)

# Tampilkan fungsi objektif dan kendala
st.markdown("### 🔢 Rumus Dihitung")
st.latex(f"Z = {c1}X + {c2}Y")
st.latex(f"{a1}X + {a2}Y \\leq {R}")

# Hitung optimasi
c = [-c1, -c2]
A = [[a1, a2]]
b = [R]
bounds = [(0, None), (0, None)]

result = linprog(c=c, A_ub=A, b_ub=b, bounds=bounds, method="highs")

# Tampilkan hasil
if result.success:
    x_opt, y_opt = np.round(result.x, 2)
    z_max = round(-result.fun, 2)

    st.success("✅ Solusi Optimal Ditemukan:")
    st.write(f"📦 Jumlah Produksi X = {x_opt}")
    st.write(f"📦 Jumlah Produksi Y = {y_opt}")
    st.write(f"💰 Total Keuntungan Maksimum Z = Rp {z_max:,.2f}")

    # Visualisasi solusi
    st.subheader("📊 Visualisasi Area Feasible dan Solusi Optimal")
    x_vals = np.linspace(0, R / a1, 200)
    y_vals = (R - a1 * x_vals) / a2

    fig, ax = plt.subplots()
    ax.plot(x_vals, y_vals, label="Kendala", color='blue')
    ax.fill_between(x_vals, 0, y_vals, where=(y_vals >= 0), color='gray', alpha=0.3)
    ax.plot(x_opt, y_opt, 'ro', label="Solusi Optimal")

    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Jumlah Produk X")
    ax.set_ylabel("Jumlah Produk Y")
    ax.set_title("Area Feasible & Solusi Optimal")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)
else:
    st.error("❌ Optimasi gagal. Silakan cek kembali input Anda.")
