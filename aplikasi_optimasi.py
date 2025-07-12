import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpStatus

st.set_page_config(page_title="Optimasi Produksi - Mesin & Operator", layout="wide")
st.title("🔧 Optimasi Produksi - Jumlah Mesin & Operator Produksi")

# ---------- Penjelasan Rumus ----------
st.subheader(r"""
📘 Rumus Optimasi Produksi

$$
\begin{array}{ll}
\text{Total Penjualan} &= \text{Harga Jual per Unit} \times \text{Jumlah Produksi} \\
\text{Total Keuntungan} &= \text{Laba per Unit} \times \text{Jumlah Produksi} \\
\text{Total Biaya Produksi} &= (\text{Harga Jual per Unit} - \text{Laba per Unit}) \times \text{Jumlah Produksi} \\
\text{Total Operator} &= \text{Jumlah Mesin} \times \text{Operator per Mesin} \\
\text{Efisiensi} &= \dfrac{\text{Total Keuntungan}}{\text{Total Operator}}
\end{array}
$$
""")

st.markdown(r"""
## 📈 Rumus Optimasi Produksi (Linear Programming)
Misalkan:
- \( X_1, X_2, \dots, X_n \): jumlah unit masing-masing produk
- \( c_1, c_2, \dots, c_n \): keuntungan per unit masing-masing produk
- \( o_1, o_2, \dots, o_n \): operator per unit produk (mesin × operator per mesin)
- \( m_1, m_2, \dots, m_n \): mesin per unit produk
- \( O \): total operator tersedia
- \( M \): total mesin tersedia

### Fungsi Objektif:
$$
\text{Maksimalkan } Z = c_1X_1 + c_2X_2 + \dots + c_nX_n
$$

### Kendala:
$$
o_1X_1 + o_2X_2 + \dots + o_nX_n \leq O \\
m_1X_1 + m_2X_2 + \dots + m_nX_n \leq M \\
X_1, X_2, \dots, X_n \geq 0
$$
""")

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

    st.header("⚙️ Input untuk Optimasi")
    total_operator_avail = st.number_input("Total Operator Tersedia", min_value=1, value=100)
    total_mesin_avail = st.number_input("Total Mesin Tersedia", min_value=1, value=50)

# ---------- Fungsi Tambahan ----------
def format_rupiah(nilai):
    return f"Rp {nilai:,.0f}".replace(",", ".")

# ---------- Perhitungan ----------
total_penjualan = [harga_jual[i] * jumlah_produksi[i] for i in range(num_products)]
total_keuntungan = [laba_per_unit[i] * jumlah_produksi[i] for i in range(num_products)]
biaya_unit = [harga_jual[i] - laba_per_unit[i] for i in range(num_products)]
total_biaya = [biaya_unit[i] * jumlah_produksi[i] for i in range(num_products)]
total_operator_per_produk = [mesin_digunakan[i] * operator_per_mesin[i] for i in range(num_products)]
efisiensi_per_produk = [
    total_keuntungan[i] / total_operator_per_produk[i] if total_operator_per_produk[i] > 0 else 0
    for i in range(num_products)
]

# ---------- Optimasi Produksi Otomatis ----------
st.subheader("📌 Hasil Optimasi Produksi Maksimum")
model = LpProblem("Optimasi_Produksi", LpMaximize)
X = [LpVariable(f"X{i+1}", lowBound=0, cat='Integer') for i in range(num_products)]
model += lpSum([laba_per_unit[i] * X[i] for i in range(num_products)])
model += lpSum([mesin_digunakan[i] * operator_per_mesin[i] * X[i] for i in range(num_products)]) <= total_operator_avail
model += lpSum([mesin_digunakan[i] * X[i] for i in range(num_products)]) <= total_mesin_avail

status = model.solve()

if LpStatus[model.status] == "Optimal":
    for i, var in enumerate(X):
        st.write(f"🔹 {product_names[i]} ➜ Jumlah Optimal: **{int(var.value())} unit**")
    st.success(f"🎯 Total Keuntungan Maksimum: **{format_rupiah(int(model.objective.value()))}**")
else:
    st.warning("⚠️ Optimasi gagal: Model tidak memiliki solusi feasible. Periksa kembali input jumlah operator, mesin, atau keuntungan.")

# ---------- Ringkasan dan Visualisasi ----------
# (bagian lainnya tetap seperti sebelumnya, tidak diubah)
