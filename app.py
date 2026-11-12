import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# ---------------------------------------------------------------
# Konfigurasi halaman
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Prediksi Penjualan UMKM",
    page_icon="🎀",
    layout="wide",
)

# ---------------------------------------------------------------
# Pilihan tema warna
# ---------------------------------------------------------------
THEMES = {
    "🍬 Pink Permen": dict(
        p1="#ec4899", p2="#f472b6", p3="#a855f7", p4="#fb7185", soft="#fce7f3",
        border="#fbcfe8", deep="#be185d", dark="#3b1d2e", muted="#9d6b85",
        muted2="#8a6477", bg1="#fff5f9", bg2="#fdf2ff", bg3="#fff0f5",
        side2="#f3e8ff", maskot="🐰",
        ikon=["🌸", "💖", "✨", "🎀", "🍓", "⭐", "🦋", "🌷", "🫧", "💗", "🍰", "🌈"],
    ),
    "💜 Lavender": dict(
        p1="#8b5cf6", p2="#a78bfa", p3="#ec4899", p4="#60a5fa", soft="#ede9fe",
        border="#ddd6fe", deep="#6d28d9", dark="#2e1b4e", muted="#7c6a9d",
        muted2="#8b7ca8", bg1="#f8f5ff", bg2="#f0f4ff", bg3="#faf5ff",
        side2="#e0e7ff", maskot="🦄",
        ikon=["🔮", "💜", "✨", "🦄", "🌙", "⭐", "🫧", "🪻", "🎀", "💫", "☁️", "🌈"],
    ),
    "🍃 Mint Segar": dict(
        p1="#10b981", p2="#34d399", p3="#06b6d4", p4="#84cc16", soft="#d1fae5",
        border="#a7f3d0", deep="#047857", dark="#0f3a2c", muted="#5f8a78",
        muted2="#6f9a86", bg1="#f3fff9", bg2="#effcff", bg3="#f7fee7",
        side2="#cffafe", maskot="🐸",
        ikon=["🍃", "🌿", "✨", "🍀", "🥝", "⭐", "🦋", "🌱", "🫧", "💚", "🍵", "🌈"],
    ),
    "🍑 Peach Hangat": dict(
        p1="#fb923c", p2="#fdba74", p3="#f472b6", p4="#fbbf24", soft="#ffedd5",
        border="#fed7aa", deep="#c2410c", dark="#4a2511", muted="#a3785a",
        muted2="#a8836a", bg1="#fff8f1", bg2="#fffbeb", bg3="#fff1f2",
        side2="#fef3c7", maskot="🐥",
        ikon=["🍑", "🍊", "✨", "🧁", "🍯", "⭐", "🦋", "🌼", "🫧", "🧡", "🍰", "🌈"],
    ),
}

NAMA_BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

DATA_CONTOH = pd.DataFrame(
    {
        "Bulan_Ke": [1, 2, 3, 4, 5, 6],
        "Total_Penjualan": [15000000, 16500000, 16000000, 18000000, 19500000, 21000000],
    }
)

# ---------------------------------------------------------------
# Sidebar (dibuat paling awal supaya tema bisa dipakai di CSS)
# ---------------------------------------------------------------
with st.sidebar:
    st.header("🎀 Pengaturan")
    nama_tema = st.selectbox("Tema warna 🎨", list(THEMES.keys()))
    gerak = st.toggle("Efek gerak ✨", value=True)
    st.divider()
    sumber = st.radio("Sumber data", ["Data contoh", "Ketik manual", "Unggah CSV sendiri"])
    file = None
    if sumber == "Unggah CSV sendiri":
        file = st.file_uploader("Kolom wajib: Bulan_Ke, Total_Penjualan", type=["csv"])
    awal_nama = st.selectbox("Bulan pertama pada data 🗓️", ["Tidak dipakai"] + NAMA_BULAN)
    n_bulan = st.slider("Prediksi berapa bulan ke depan? 🔮", 1, 24, 3)
    st.caption("Metode utama: Regresi Linear (scikit-learn) 💕")

T = THEMES[nama_tema]


def hex_rgb(h):
    return f"{int(h[1:3], 16)}, {int(h[3:5], 16)}, {int(h[5:7], 16)}"


# ---------------------------------------------------------------
# CSS
# ---------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&display=swap');

@property --sudut {syntax: '<angle>'; initial-value: 0deg; inherits: false;}
@property --a {syntax: '<integer>'; initial-value: 0; inherits: false;}
@property --b {syntax: '<integer>'; initial-value: 0; inherits: false;}

html, body, .stApp, .stMarkdown, button, label, h1, h2, h3, p {
    font-family: 'Baloo 2', 'Segoe UI', 'Trebuchet MS', sans-serif;
}
.stApp {background: linear-gradient(160deg, @@BG1@@ 0%, @@BG2@@ 50%, @@BG3@@ 100%);}
.block-container {padding-top: 2rem; max-width: 1150px; position: relative; z-index: 1;}
footer {visibility: hidden;}

/* ---------- hiasan melayang ---------- */
.fl {position: fixed; bottom: -50px; z-index: 0; pointer-events: none; opacity: 0;
     animation: naik linear infinite;}
@keyframes naik {
    0% {transform: translateY(0) rotate(0deg); opacity: 0;}
    10% {opacity: .65;}
    90% {opacity: .55;}
    100% {transform: translateY(-115vh) rotate(360deg); opacity: 0;}
}

/* ---------- header ---------- */
.hero {
    background: linear-gradient(120deg, @@P1@@, @@P2@@, @@P3@@, @@P4@@, @@P1@@);
    background-size: 300% 300%; animation: geser 9s ease infinite;
    padding: 30px 34px 54px; border-radius: 28px; margin-bottom: 18px;
    box-shadow: 0 12px 32px rgba(@@RGB1@@, .35); position: relative; overflow: hidden;
}
@keyframes geser {0% {background-position: 0% 50%;} 50% {background-position: 100% 50%;} 100% {background-position: 0% 50%;}}
.hero h1 {margin: 0; font-size: 2.3rem; color: #fff; padding: 0; font-weight: 800;}
.hero p {margin: 8px 0 0; color: #fff; opacity: .92; font-size: 1.05rem;}
.maskot {display: inline-block; font-size: 2.5rem; margin-right: 10px;
         animation: lompat 1.6s ease-in-out infinite; transform-origin: bottom center;}
@keyframes lompat {0%, 100% {transform: translateY(0) rotate(-6deg);} 50% {transform: translateY(-14px) rotate(6deg);}}
.kilau {position: absolute; font-size: 1.4rem; animation: kedip 2.4s ease-in-out infinite;}
@keyframes kedip {0%, 100% {opacity: .2; transform: scale(.7) rotate(0deg);} 50% {opacity: 1; transform: scale(1.2) rotate(20deg);}}
.ombak {
    position: absolute; left: 0; bottom: 0; width: 100%; height: 34px; opacity: .45;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 40' preserveAspectRatio='none'%3E%3Cpath d='M0 20 Q75 0 150 20 T300 20 T450 20 T600 20 V40 H0Z' fill='white'/%3E%3C/svg%3E") repeat-x;
    background-size: 600px 100%; animation: ombak 6s linear infinite;
}
.ombak.dua {opacity: .25; height: 26px; animation-duration: 10s; animation-direction: reverse;}
@keyframes ombak {from {background-position-x: 0;} to {background-position-x: 600px;}}

/* ---------- teks berjalan ---------- */
.marquee {overflow: hidden; white-space: nowrap; background: #fff; border: 2px solid @@BORDER@@;
          border-radius: 999px; padding: 8px 0; margin-bottom: 22px; color: @@DEEP@@; font-weight: 700;}
.marquee span {display: inline-block; padding-left: 100%; animation: jalan 32s linear infinite;}
@keyframes jalan {to {transform: translateX(-100%);}}

/* ---------- kartu ---------- */
.card {
    border: 3px solid transparent; border-radius: 22px; padding: 16px 20px; min-height: 140px;
    background: linear-gradient(#fff, #fff) padding-box,
        conic-gradient(from var(--sudut), @@P1@@, @@P3@@, @@P4@@, @@P2@@, @@P1@@) border-box;
    box-shadow: 0 6px 20px rgba(@@RGB1@@, .16);
    animation: muncul .8s cubic-bezier(.2, .9, .3, 1.2) both, putar 5s linear infinite;
    transition: transform .25s ease, box-shadow .25s ease;
}
@keyframes putar {to {--sudut: 360deg;}}
.card:hover {transform: translateY(-8px) rotate(-1.2deg) scale(1.04); box-shadow: 0 16px 34px rgba(@@RGB1@@, .32);}
@keyframes muncul {0% {opacity: 0; transform: translateY(30px) scale(.9);} 100% {opacity: 1; transform: translateY(0) scale(1);}}
.card .ico {font-size: 1.7rem; display: inline-block; animation: goyang 3s ease-in-out infinite;}
@keyframes goyang {0%, 100% {transform: rotate(-8deg);} 50% {transform: rotate(8deg);}}
.card .lbl {font-size: .92rem; color: @@MUTED@@; margin: 4px 0; font-weight: 700;}
.card .val {font-size: 1.55rem; font-weight: 800; color: @@DARK@@; min-height: 2.1rem;}
.card .sub {font-size: .85rem; color: @@MUTED2@@; margin-top: 2px;}
.cnt {counter-reset: ca var(--a) cb var(--b); animation-duration: 1.8s;
      animation-timing-function: cubic-bezier(.2, .8, .2, 1); animation-fill-mode: forwards;}
.cnt::after {content: var(--pre) counter(ca) "," counter(cb, decimal-leading-zero) var(--suf);}

/* ---------- insight, bubble, hasil, progress ---------- */
.insight {background: #fff; border: 2px dashed @@BORDER@@; color: @@DARK@@; padding: 14px 18px;
          border-radius: 18px; margin-top: 14px; animation: muncul .9s ease both;}
.mood {display: inline-block; font-size: 1.1rem; font-weight: 800; color: @@DEEP@@; background: @@SOFT@@;
       border-radius: 999px; padding: 2px 14px; margin-left: 6px; animation: denyut 1.8s ease-in-out infinite;}
@keyframes denyut {0%, 100% {transform: scale(1);} 50% {transform: scale(1.1);}}
.kata {display: flex; align-items: center; gap: 14px; margin-top: 14px;}
.kata .avatar {font-size: 2.6rem; animation: lompat 2s ease-in-out infinite;}
.bubble {position: relative; background: #fff; border: 2px solid @@BORDER@@; border-radius: 20px;
         padding: 12px 18px; color: @@DARK@@; font-weight: 700; animation: pop .7s cubic-bezier(.2, .9, .3, 1.4) both;}
.bubble::before {content: ""; position: absolute; left: -10px; top: 50%; width: 16px; height: 16px;
                 background: #fff; border-left: 2px solid @@BORDER@@; border-bottom: 2px solid @@BORDER@@;
                 transform: translateY(-50%) rotate(45deg);}
.hasil {background: linear-gradient(120deg, @@SOFT@@, #fff); border: 2px solid @@BORDER@@; border-radius: 22px;
        padding: 20px 24px; text-align: center; margin-top: 12px; color: @@DARK@@;
        animation: pop .6s cubic-bezier(.2, .9, .3, 1.4) both;}
.hasil .angka {font-size: 2.1rem; font-weight: 800; color: @@DEEP@@;}
@keyframes pop {0% {opacity: 0; transform: scale(.5);} 100% {opacity: 1; transform: scale(1);}}
.bar {height: 26px; border-radius: 999px; background: @@SOFT@@; overflow: hidden; border: 2px solid @@BORDER@@; margin: 6px 0 4px;}
.bar > span {display: block; height: 100%; width: var(--w); border-radius: 999px;
    background: repeating-linear-gradient(45deg, @@P1@@ 0 14px, @@P2@@ 14px 28px); background-size: 40px 40px;
    animation: isi 1.6s cubic-bezier(.2, .9, .3, 1) both, garis 1.2s linear infinite;}
@keyframes isi {from {width: 0;}}
@keyframes garis {to {background-position-x: 40px;}}
.rumus {background: #fff; border-radius: 16px; border: 2px solid @@BORDER@@; padding: 12px 18px;
        font-weight: 700; color: @@DARK@@; text-align: center; margin: 10px 0;}
.target-box {background: #fff; border-radius: 18px; border: 2px dashed @@BORDER@@; padding: 12px 18px;
             color: @@DARK@@; font-weight: 700; margin-top: 8px;}

/* ---------- metrik bawaan Streamlit ---------- */
[data-testid="stMetric"] {background: #fff; border: 2px solid @@BORDER@@; border-radius: 18px;
    padding: 12px 16px; box-shadow: 0 4px 14px rgba(@@RGB1@@, .10);}
[data-testid="stMetricValue"] {color: @@DEEP@@; font-weight: 800;}

/* ---------- tombol, tab, sidebar ---------- */
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(120deg, @@P1@@, @@P2@@); color: #fff; border: none; border-radius: 999px;
    padding: 10px 28px; font-weight: 700; box-shadow: 0 6px 16px rgba(@@RGB1@@, .35);
    transition: transform .2s ease, box-shadow .2s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: scale(1.08) rotate(-1deg); color: #fff; box-shadow: 0 10px 22px rgba(@@RGB1@@, .5);
}
.stTabs [data-baseweb="tab"] {font-size: 1.05rem; font-weight: 700; color: @@DARK@@;}
[data-testid="stSidebar"] {background: linear-gradient(180deg, @@SOFT@@ 0%, @@SIDE2@@ 100%);}
</style>
"""
tokens = {
    "@@P1@@": T["p1"], "@@P2@@": T["p2"], "@@P3@@": T["p3"], "@@P4@@": T["p4"],
    "@@SOFT@@": T["soft"], "@@BORDER@@": T["border"], "@@DEEP@@": T["deep"],
    "@@DARK@@": T["dark"], "@@MUTED@@": T["muted"], "@@MUTED2@@": T["muted2"],
    "@@BG1@@": T["bg1"], "@@BG2@@": T["bg2"], "@@BG3@@": T["bg3"],
    "@@SIDE2@@": T["side2"], "@@RGB1@@": hex_rgb(T["p1"]),
}
for k, v in tokens.items():
    CSS = CSS.replace(k, v)
st.markdown(CSS, unsafe_allow_html=True)

if not gerak:
    st.markdown(
        """<style>
        .fl, .hero, .maskot, .kilau, .ombak, .marquee span, .card, .card .ico, .mood,
        .bar > span, .kata .avatar, .bubble, .insight, .hasil {animation: none !important;}
        </style>""",
        unsafe_allow_html=True,
    )
else:
    hiasan = "".join(
        f'<span class="fl" style="left:{(i * 11 + 4) % 96}%;'
        f"animation-duration:{14 + (i * 3) % 9}s;animation-delay:-{i * 2}s;"
        f'font-size:{18 + (i * 5) % 18}px">{e}</span>'
        for i, e in enumerate(T["ikon"])
    )
    st.markdown(hiasan, unsafe_allow_html=True)


# ---------------------------------------------------------------
# Fungsi bantu
# ---------------------------------------------------------------
def rp(x):
    """Format Rupiah, contoh: Rp 21.766.667"""
    return "Rp " + f"{x:,.0f}".replace(",", ".")


def teks_jt(v):
    return "Rp " + f"{v / 1e6:.2f}".replace(".", ",") + " jt"


def label_bulan(k):
    """Nama bulan: 'Jul (ke-7)' kalau bulan pertama diisi, selain itu 'Bulan ke-7'."""
    k = int(k)
    if awal_nama == "Tidak dipakai":
        return f"Bulan ke-{k}"
    idx = NAMA_BULAN.index(awal_nama)
    return f"{NAMA_BULAN[(idx + k - 1) % 12]} (ke-{k})"


def kartu(idx, ikon_, label, nilai, sub, delay, juta=True):
    """Kartu ringkasan. Angka dihitung naik (count-up) kalau efek gerak aktif."""
    if juta:
        centi = int(round(nilai / 1e6 * 100))
        pre, suf, statis = "Rp ", " jt", teks_jt(nilai)
    else:
        centi = int(round(max(nilai, 0) * 100))
        pre, suf, statis = "", "", f"{nilai:.2f}".replace(".", ",")
    a, b = centi // 100, centi % 100

    if gerak:
        kf = f"kf{idx}"
        css_kf = "<style>@keyframes " + kf + "{to{--a:" + str(a) + ";--b:" + str(b) + "}}</style>"
        isi = (
            f'<div class="val cnt" style=\'animation-name:{kf};animation-delay:{delay}s;'
            f'--pre:"{pre}";--suf:"{suf}"\'></div>'
        )
    else:
        css_kf, isi = "", f'<div class="val">{statis}</div>'

    st.markdown(
        css_kf
        + f'<div class="card" style="animation-delay:{delay}s,0s">'
        + f'<span class="ico">{ikon_}</span><div class="lbl">{label}</div>'
        + isi
        + f'<div class="sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------
# Header + teks berjalan
# ---------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
        <span class="kilau" style="top:14px;right:40px">✨</span>
        <span class="kilau" style="top:62px;right:130px;animation-delay:.8s">💖</span>
        <span class="kilau" style="top:20px;right:230px;animation-delay:1.2s">🌸</span>
        <span class="kilau" style="top:70px;right:330px;animation-delay:1.6s">⭐</span>
        <h1><span class="maskot">{T['maskot']}</span>Prediksi Penjualan UMKM</h1>
        <p>Intip omzet bulan depan dengan cepat dan lucu! 🎀 Lengkap dengan kisaran, skenario,
        target, estimasi laba, dan laporan siap unduh.</p>
        <div class="ombak"></div><div class="ombak dua"></div>
    </div>
    <div class="marquee"><span>
        ✨ Catat penjualan tiap bulan supaya prediksi makin akurat &nbsp;•&nbsp;
        🌸 Makin banyak data, makin tepat perkiraannya &nbsp;•&nbsp;
        🎀 Faktor musiman seperti Lebaran belum dihitung otomatis, coba tab Skenario &nbsp;•&nbsp;
        💖 Semangat jualan hari ini! &nbsp;•&nbsp;
        🎨 Coba ganti tema warna di sidebar
    </span></div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# Ambil data
# ---------------------------------------------------------------
if sumber == "Unggah CSV sendiri":
    if file is None:
        st.info("⬅️ Unggah file CSV di sidebar, atau pilih **Data contoh** ya! 🌸")
        st.stop()
    df = pd.read_csv(file)
elif sumber == "Ketik manual":
    st.subheader("✍️ Ketik data penjualan Anda")
    st.caption("Klik sel untuk mengubah angka. Klik baris kosong paling bawah untuk menambah bulan baru.")
    df = st.data_editor(DATA_CONTOH, num_rows="dynamic", hide_index=True, key="editor_manual")
else:
    df = DATA_CONTOH.copy()

if "Bulan_Ke" not in df.columns or "Total_Penjualan" not in df.columns:
    st.error("Kolom tidak sesuai. Pastikan ada kolom 'Bulan_Ke' dan 'Total_Penjualan'.")
    st.stop()

df = df[["Bulan_Ke", "Total_Penjualan"]].copy()
df["Bulan_Ke"] = pd.to_numeric(df["Bulan_Ke"], errors="coerce")
df["Total_Penjualan"] = pd.to_numeric(df["Total_Penjualan"], errors="coerce")
df = df.dropna().drop_duplicates("Bulan_Ke", keep="last").sort_values("Bulan_Ke")
df["Bulan_Ke"] = df["Bulan_Ke"].astype(int)
if len(df) < 2:
    st.error("Data minimal 2 bulan (angka valid) supaya bisa diprediksi.")
    st.stop()

# ---------------------------------------------------------------
# Latih model & hitung prediksi
# ---------------------------------------------------------------
model = LinearRegression().fit(df[["Bulan_Ke"]], df["Total_Penjualan"])
hitung = model.predict(df[["Bulan_Ke"]])
r2 = r2_score(df["Total_Penjualan"], hitung)
kenaikan = float(model.coef_[0])
awal = float(model.intercept_)
bulan_pertama = int(df["Bulan_Ke"].min())
bulan_terakhir = int(df["Bulan_Ke"].max())
terakhir = float(df.loc[df["Bulan_Ke"] == bulan_terakhir, "Total_Penjualan"].iloc[0])

sisa = df["Total_Penjualan"] - hitung
se = (float((sisa**2).sum()) / (len(df) - 2)) ** 0.5 if len(df) > 2 else 0.0
mae = float(np.mean(np.abs(sisa)))
rmse = float(np.sqrt(np.mean(sisa**2)))
mape = float(np.mean(np.abs(sisa / df["Total_Penjualan"])) * 100)

# Uji "tebak bulan terakhir" memakai data sebelumnya saja
uji_selisih = None
if len(df) >= 3:
    awal_df = df.iloc[:-1]
    m_uji = LinearRegression().fit(awal_df[["Bulan_Ke"]], awal_df["Total_Penjualan"])
    tebak = float(m_uji.predict(df.iloc[[-1]][["Bulan_Ke"]])[0])
    uji_selisih = (tebak - terakhir) / terakhir * 100

pred = pd.DataFrame({"Bulan_Ke": range(bulan_terakhir + 1, bulan_terakhir + n_bulan + 1)})
pred["Total_Penjualan"] = model.predict(pred).round(0)
langkah = pred["Bulan_Ke"] - bulan_terakhir
pred["Bawah"] = (pred["Total_Penjualan"] - 1.5 * se * (1 + 0.15 * langkah)).round(0)
pred["Atas"] = (pred["Total_Penjualan"] + 1.5 * se * (1 + 0.15 * langkah)).round(0)
sebelumnya = pred["Total_Penjualan"].shift(1)
sebelumnya.iloc[0] = terakhir
pred["Naik"] = pred["Total_Penjualan"] - sebelumnya
pred["Persen"] = pred["Naik"] / sebelumnya * 100
pred["Kumulatif"] = pred["Total_Penjualan"].cumsum()
bulan_depan = float(pred["Total_Penjualan"].iloc[0])
total_pred = float(pred["Total_Penjualan"].sum())
rata_pred = float(pred["Total_Penjualan"].mean())
idx_puncak = int(pred["Total_Penjualan"].idxmax())
bulan_puncak = int(pred.loc[idx_puncak, "Bulan_Ke"])
nilai_puncak = float(pred.loc[idx_puncak, "Total_Penjualan"])
tumbuh_akhir = (float(pred["Total_Penjualan"].iloc[-1]) - terakhir) / terakhir * 100

persen = kenaikan / terakhir * 100 if terakhir else 0
if persen >= 5:
    mood, kata = "🚀 Melesat!", "Wow, penjualanmu melesat! Pertahankan ya! 🚀"
elif persen > 0:
    mood, kata = "😊 Naik pelan-pelan", "Naik terus, sedikit demi sedikit lama-lama jadi bukit! 💪"
elif persen > -1:
    mood, kata = "😐 Cenderung stabil", "Penjualan stabil. Coba bikin promo kecil yuk! 🎁"
else:
    mood, kata = "🥺 Sedang turun", "Tenang, yuk cari tahu penyebabnya dan semangat lagi! 🤗"


def kapan_target(target_rp):
    """Bulan ke berapa garis tren mencapai target. None kalau tren tidak naik."""
    if kenaikan <= 0:
        return None
    return int(np.ceil((target_rp - awal) / kenaikan))


# Tabel prediksi lengkap
lengkap = pd.DataFrame(
    {
        "Bulan": [label_bulan(k) for k in pred["Bulan_Ke"]],
        "Prediksi": pred["Total_Penjualan"],
        "Kisaran Bawah": pred["Bawah"],
        "Kisaran Atas": pred["Atas"],
        "Naik dari bulan lalu": pred["Naik"],
        "Pertumbuhan (%)": pred["Persen"].round(2),
        "Kumulatif": pred["Kumulatif"],
    }
)
lengkap_tampil = lengkap.copy()
for kolom in ["Prediksi", "Kisaran Bawah", "Kisaran Atas", "Naik dari bulan lalu", "Kumulatif"]:
    lengkap_tampil[kolom] = lengkap_tampil[kolom].map(rp)
lengkap_tampil["Pertumbuhan (%)"] = lengkap_tampil["Pertumbuhan (%)"].map(lambda v: f"{v:+.2f}%")

arah_k = "naik" if kenaikan >= 0 else "turun"
r2_persen = max(r2, 0) * 100


def buat_kesimpulan():
    return (
        f"Berdasarkan data penjualan {len(df)} bulan (bulan ke-{bulan_pertama} sampai ke-{bulan_terakhir}), "
        f"penjualan cenderung {arah_k} rata-rata sekitar {rp(abs(kenaikan))} per bulan "
        f"({abs(persen):.1f}% dari penjualan terakhir sebesar {rp(terakhir)}).\n\n"
        f"Model regresi linear yang dihasilkan adalah: Penjualan = {rp(awal)} "
        f"{'+' if kenaikan >= 0 else '-'} {rp(abs(kenaikan))} x Bulan ke-. "
        f"Nilai R² sebesar {r2:.2f} berarti sekitar {r2_persen:.0f}% variasi penjualan dapat dijelaskan oleh tren waktu. "
        f"Rata-rata selisih model terhadap data asli (MAE) adalah {rp(mae)} atau kesalahan rata-rata {mape:.1f}% (MAPE).\n\n"
        f"Penjualan bulan ke-{bulan_terakhir + 1} diperkirakan sebesar {rp(bulan_depan)} "
        f"(kisaran {rp(float(pred['Bawah'].iloc[0]))} sampai {rp(float(pred['Atas'].iloc[0]))}). "
        f"Untuk {n_bulan} bulan ke depan, total penjualan diperkirakan {rp(total_pred)} "
        f"dengan rata-rata {rp(rata_pred)} per bulan; puncaknya di {label_bulan(bulan_puncak)} sebesar {rp(nilai_puncak)}.\n\n"
        f"Keterbatasan: jumlah data hanya {len(df)} bulan dan model belum memperhitungkan faktor musiman "
        f"(misalnya Lebaran atau promo), sehingga hasilnya sebaiknya dipakai sebagai perkiraan kasar."
    )


kesimpulan = buat_kesimpulan()

# ---------------------------------------------------------------
# Kartu ringkasan
# ---------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    kartu(0, "💰", "Penjualan terakhir", terakhir, f"{rp(terakhir)} (bulan ke-{bulan_terakhir})", 0.0)
with c2:
    kartu(1, "📈", "Tren per bulan", abs(kenaikan), f"{rp(abs(kenaikan))} {arah_k} tiap bulan", 0.15)
with c3:
    kartu(2, "🎯", "Akurasi model (R²)", r2, "Mendekati 1 = makin cocok", 0.30, juta=False)
with c4:
    kartu(3, "🔮", "Prediksi bulan depan", bulan_depan, f"{rp(bulan_depan)} ({label_bulan(bulan_terakhir + 1)})", 0.45)

st.write("")

# ---------------------------------------------------------------
# Tab
# ---------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["📊 Grafik", "🔮 Prediksi", "🧪 Skenario & Simulasi", "⚖️ Bandingkan Model", "📝 Laporan", "📋 Data"]
)

domain_jenis = ["Aktual", "Prediksi"]
range_jenis = [T["p1"], T["p3"]]

# ======================= TAB 1: GRAFIK ==========================
with tab1:
    aktual = df.assign(Jenis="Aktual")
    sambung = pd.concat(
        [df.tail(1)[["Bulan_Ke", "Total_Penjualan"]], pred[["Bulan_Ke", "Total_Penjualan"]]]
    ).assign(Jenis="Prediksi")
    pita = pd.concat(
        [
            pd.DataFrame({"Bulan_Ke": [bulan_terakhir], "Total_Penjualan": [terakhir], "Atas": [terakhir]}),
            pred[["Bulan_Ke", "Bawah", "Atas"]].rename(columns={"Bawah": "Total_Penjualan"}),
        ]
    )

    sumbu_x = alt.X("Bulan_Ke:Q", title="Bulan ke-", axis=alt.Axis(tickMinStep=1))
    sumbu_y = alt.Y(
        "Total_Penjualan:Q", title="Total Penjualan (Rp)",
        axis=alt.Axis(format="~s"), scale=alt.Scale(zero=False),
    )
    warna = alt.Color(
        "Jenis:N",
        scale=alt.Scale(domain=domain_jenis, range=range_jenis),
        legend=alt.Legend(title=None, orient="top"),
    )
    tip = [
        "Jenis:N",
        alt.Tooltip("Bulan_Ke:Q", title="Bulan ke-"),
        alt.Tooltip("Total_Penjualan:Q", title="Penjualan (Rp)", format=",.0f"),
    ]

    area = alt.Chart(aktual).mark_area(opacity=0.15, interpolate="monotone").encode(x=sumbu_x, y=sumbu_y, color=warna)
    pita_kisaran = alt.Chart(pita).mark_area(opacity=0.18, color=T["p3"]).encode(x=sumbu_x, y=sumbu_y, y2="Atas:Q")
    garis_aktual = alt.Chart(aktual).mark_line(strokeWidth=4, interpolate="monotone").encode(x=sumbu_x, y=sumbu_y, color=warna)
    garis_prediksi = alt.Chart(sambung).mark_line(strokeWidth=4, strokeDash=[8, 6]).encode(x=sumbu_x, y=sumbu_y, color=warna)
    titik = (
        alt.Chart(pd.concat([aktual, pred[["Bulan_Ke", "Total_Penjualan"]].assign(Jenis="Prediksi")]))
        .mark_point(filled=True, size=130)
        .encode(x=sumbu_x, y=sumbu_y, color=warna, tooltip=tip)
    )
    grafik = (
        (area + pita_kisaran + garis_aktual + garis_prediksi + titik)
        .properties(height=380)
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor=T["border"])
    )
    st.altair_chart(grafik)
    st.caption("Area transparan = kisaran perkiraan kasar (makin jauh bulannya, makin lebar).")

    arah_teks = "tren naik 📈" if kenaikan >= 0 else "tren turun 📉"
    st.markdown(
        f"""<div class="insight">💡 <b>Insight:</b> Penjualan menunjukkan {arah_teks},
        rata-rata sekitar <b>{rp(abs(kenaikan))}</b> per bulan.
        Pada {label_bulan(bulan_terakhir + n_bulan)}, penjualan diperkirakan mencapai
        <b>{rp(pred['Total_Penjualan'].iloc[-1])}</b> 🎉<br>
        Mood bisnis: <span class="mood">{mood}</span></div>
        <div class="kata"><div class="avatar">{T['maskot']}</div><div class="bubble">{kata}</div></div>""",
        unsafe_allow_html=True,
    )

    st.subheader("Pertumbuhan tiap bulan 🌱")
    tumbuh = df.copy()
    tumbuh["Pertumbuhan"] = tumbuh["Total_Penjualan"].pct_change() * 100
    tumbuh = tumbuh.dropna()
    batang = (
        alt.Chart(tumbuh)
        .mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10)
        .encode(
            x=alt.X("Bulan_Ke:O", title="Bulan ke-"),
            y=alt.Y("Pertumbuhan:Q", title="Pertumbuhan (%)"),
            color=alt.condition(alt.datum.Pertumbuhan > 0, alt.value(T["p1"]), alt.value(T["p3"])),
            tooltip=[
                alt.Tooltip("Bulan_Ke:O", title="Bulan ke-"),
                alt.Tooltip("Pertumbuhan:Q", title="Pertumbuhan (%)", format=".1f"),
            ],
        )
        .properties(height=240)
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor=T["border"])
    )
    st.altair_chart(batang)

# ======================= TAB 2: PREDIKSI ========================
with tab2:
    st.subheader(f"Ringkasan prediksi {n_bulan} bulan ke depan 🔮")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"Total {n_bulan} bulan", rp(total_pred))
    m2.metric("Rata-rata per bulan", rp(rata_pred))
    m3.metric("Bulan tertinggi", label_bulan(bulan_puncak), rp(nilai_puncak), delta_color="off")
    m4.metric("Dibanding bulan terakhir", f"{tumbuh_akhir:+.1f}%", f"di {label_bulan(bulan_terakhir + n_bulan)}", delta_color="off")

    st.subheader("Tabel prediksi lengkap 📋")
    st.dataframe(lengkap_tampil, hide_index=True)

    tanda = "+" if kenaikan >= 0 else "−"
    st.markdown(
        f'<div class="rumus">📐 Rumus model: Penjualan = {rp(awal)} {tanda} {rp(abs(kenaikan))} × Bulan ke-</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Cek bulan tertentu & target ✨")
    kiri, kanan = st.columns(2)
    with kiri:
        target = st.number_input(
            "Urutan bulan yang ingin diprediksi:",
            min_value=bulan_terakhir + 1, value=bulan_terakhir + 1, step=1,
        )
    with kanan:
        target_rp = st.number_input("Target penjualan (Rp):", min_value=1, value=25000000, step=500000)
    hasil = float(model.predict(pd.DataFrame({"Bulan_Ke": [target]}))[0])

    persen_target = hasil / target_rp * 100
    lebar = max(min(persen_target, 100), 0)
    st.markdown(
        f"""🎯 Perkiraan {label_bulan(target)} mencapai <b>{persen_target:.0f}%</b> dari target {rp(target_rp)}
        <div class="bar" style="--w:{lebar:.0f}%"><span></span></div>""",
        unsafe_allow_html=True,
    )

    bulan_capai = kapan_target(target_rp)
    if bulan_capai is None:
        pesan = "Tren penjualan sedang tidak naik, jadi target ini belum bisa dicapai dari tren saat ini."
    elif bulan_capai <= bulan_terakhir:
        pesan = f"Target ini sudah terlampaui oleh tren sejak {label_bulan(max(bulan_capai, bulan_pertama))}."
    else:
        pesan = (
            f"Dari tren saat ini, target {rp(target_rp)} diperkirakan tercapai pada "
            f"<b>{label_bulan(bulan_capai)}</b>, sekitar {bulan_capai - bulan_terakhir} bulan lagi."
        )
    st.markdown(f'<div class="target-box">⏳ Kapan target tercapai? {pesan}</div>', unsafe_allow_html=True)

    st.write("")
    if st.button("✨ Hitung Prediksi"):
        st.markdown(
            f"""<div class="hasil">Estimasi penjualan {label_bulan(target)} 🎀
            <div class="angka">{rp(hasil)}</div></div>""",
            unsafe_allow_html=True,
        )
        st.balloons()
        st.toast("Yeay! Prediksi selesai 🎉", icon="💖")

    st.write("")
    st.download_button(
        "⬇️ Unduh tabel prediksi lengkap (CSV)",
        lengkap.to_csv(index=False).encode("utf-8"),
        file_name="hasil_prediksi_lengkap.csv",
        mime="text/csv",
    )

    with st.expander("❓ Cara membaca hasil ini"):
        st.markdown(
            """
- **Regresi linear** mencari satu garis lurus yang paling mendekati data penjualan,
  lalu garis itu diperpanjang ke bulan-bulan berikutnya.
- **Tren per bulan** adalah kemiringan garis: rata-rata kenaikan (atau penurunan) penjualan tiap bulan.
- **R²** menunjukkan seberapa cocok garis dengan data. Nilai mendekati 1 berarti sangat cocok.
- **Kisaran** adalah gambaran kasar kemungkinan naik-turunnya hasil. Makin jauh bulannya, makin lebar.
- **Kumulatif** adalah jumlah prediksi dari bulan pertama prediksi sampai bulan itu.
- Model ini belum memperhitungkan musim ramai (Lebaran, promo) dan data yang sedikit
  membuat perkiraan kurang pasti.
            """
        )

# ================= TAB 3: SKENARIO & SIMULASI ===================
with tab3:
    st.subheader("Tiga skenario penjualan 🌦️")
    skenario = pd.DataFrame(
        {
            "Bulan": [label_bulan(k) for k in pred["Bulan_Ke"]],
            "Pesimis 🌧️": pred["Bawah"],
            "Normal ☀️": pred["Total_Penjualan"],
            "Optimis 🌈": pred["Atas"],
        }
    )
    s1, s2, s3 = st.columns(3)
    s1.metric("Total pesimis", rp(float(pred["Bawah"].sum())))
    s2.metric("Total normal", rp(total_pred))
    s3.metric("Total optimis", rp(float(pred["Atas"].sum())))
    tampil_skenario = skenario.copy()
    for kolom in ["Pesimis 🌧️", "Normal ☀️", "Optimis 🌈"]:
        tampil_skenario[kolom] = tampil_skenario[kolom].map(rp)
    st.dataframe(tampil_skenario, hide_index=True)

    panjang = pd.concat(
        [
            pd.DataFrame({"Bulan_Ke": pred["Bulan_Ke"], "Nilai": pred["Bawah"], "Skenario": "Pesimis"}),
            pd.DataFrame({"Bulan_Ke": pred["Bulan_Ke"], "Nilai": pred["Total_Penjualan"], "Skenario": "Normal"}),
            pd.DataFrame({"Bulan_Ke": pred["Bulan_Ke"], "Nilai": pred["Atas"], "Skenario": "Optimis"}),
        ]
    )
    grafik_skenario = (
        alt.Chart(panjang)
        .mark_line(strokeWidth=3, point=True)
        .encode(
            x=alt.X("Bulan_Ke:Q", title="Bulan ke-", axis=alt.Axis(tickMinStep=1)),
            y=alt.Y("Nilai:Q", title="Penjualan (Rp)", axis=alt.Axis(format="~s"), scale=alt.Scale(zero=False)),
            color=alt.Color(
                "Skenario:N",
                scale=alt.Scale(domain=["Pesimis", "Normal", "Optimis"], range=[T["p3"], T["p1"], T["p4"]]),
                legend=alt.Legend(title=None, orient="top"),
            ),
        )
        .properties(height=300)
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor=T["border"])
    )
    st.altair_chart(grafik_skenario)

    st.subheader("Simulasi 'bagaimana kalau...' 🎛️")
    st.caption("Misalnya ada promo, kenaikan harga, atau musim ramai (Lebaran). Atur persentasenya, lalu lihat dampaknya.")
    sk1, sk2 = st.columns(2)
    with sk1:
        efek = st.slider("Efek terhadap penjualan (%)", -30, 100, 10)
    with sk2:
        mulai = st.selectbox(
            "Mulai berlaku di",
            list(pred["Bulan_Ke"]),
            format_func=label_bulan,
        )
    disesuaikan = np.where(pred["Bulan_Ke"] >= mulai, pred["Total_Penjualan"] * (1 + efek / 100), pred["Total_Penjualan"])
    simulasi = pd.DataFrame(
        {
            "Bulan": [label_bulan(k) for k in pred["Bulan_Ke"]],
            "Normal": pred["Total_Penjualan"],
            "Dengan efek": np.round(disesuaikan, 0),
        }
    )
    simulasi["Selisih"] = simulasi["Dengan efek"] - simulasi["Normal"]
    selisih_total = float(simulasi["Selisih"].sum())
    t1, t2 = st.columns(2)
    t1.metric(f"Total dengan efek ({efek:+d}%)", rp(float(simulasi["Dengan efek"].sum())))
    t2.metric("Tambahan / pengurangan total", rp(selisih_total), f"{efek:+d}% mulai {label_bulan(mulai)}", delta_color="off")
    tampil_simulasi = simulasi.copy()
    for kolom in ["Normal", "Dengan efek", "Selisih"]:
        tampil_simulasi[kolom] = tampil_simulasi[kolom].map(rp)
    st.dataframe(tampil_simulasi, hide_index=True)

    st.subheader("Estimasi laba 💰")
    margin = st.slider("Margin laba (% dari penjualan)", 1, 80, 20)
    l1, l2, l3 = st.columns(3)
    l1.metric("Laba pesimis", rp(float(pred["Bawah"].sum()) * margin / 100))
    l2.metric("Laba normal", rp(total_pred * margin / 100))
    l3.metric("Laba optimis", rp(float(pred["Atas"].sum()) * margin / 100))
    st.caption("Perhitungan sederhana: laba = penjualan × margin. Biaya tetap tidak dihitung terpisah.")

# ================= TAB 4: BANDINGKAN MODEL ======================
with tab4:
    st.subheader("Seberapa akurat modelnya? 🎯")
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("MAE (rata-rata selisih)", rp(mae))
    e2.metric("RMSE", rp(rmse))
    e3.metric("MAPE (% kesalahan)", f"{mape:.1f}%")
    if uji_selisih is None:
        e4.metric("Uji tebak bulan terakhir", "butuh ≥3 bulan")
    else:
        e4.metric("Uji tebak bulan terakhir", f"{uji_selisih:+.1f}%", "selisih dari data asli", delta_color="off")
    st.caption(
        "MAE/RMSE/MAPE makin kecil makin baik. 'Uji tebak bulan terakhir' = model hanya melihat data "
        "sebelum bulan terakhir, lalu menebak bulan terakhir itu."
    )

    st.subheader("Bandingkan beberapa model ⚖️")
    x = df["Bulan_Ke"].to_numpy(dtype=float)
    yv = df["Total_Penjualan"].to_numpy(dtype=float)
    x_semua = np.arange(int(x.min()), bulan_terakhir + n_bulan + 1, dtype=float)
    x_depan = np.array([bulan_terakhir + 1, bulan_terakhir + n_bulan], dtype=float)

    daftar = {}
    daftar["Regresi Linear"] = lambda z: model.intercept_ + model.coef_[0] * z
    if len(df) >= 4:
        koef2 = np.polyfit(x, yv, 2)
        daftar["Polinomial (derajat 2)"] = lambda z: np.polyval(koef2, z)
    landai = (yv[-1] - yv[0]) / (x[-1] - x[0]) if x[-1] != x[0] else 0.0
    daftar["Garis awal–akhir"] = lambda z: yv[0] + landai * (z - x[0])

    baris, garis = [], []
    for nama_m, fungsi in daftar.items():
        dalam = fungsi(x)
        baris.append(
            {
                "Model": nama_m,
                "R²": round(float(r2_score(yv, dalam)), 3),
                "Rata-rata selisih": rp(float(np.mean(np.abs(yv - dalam)))),
                f"Bulan ke-{int(x_depan[0])}": rp(float(fungsi(x_depan[0]))),
                f"Bulan ke-{int(x_depan[1])}": rp(float(fungsi(x_depan[1]))),
            }
        )
        garis.append(pd.DataFrame({"Bulan_Ke": x_semua, "Penjualan": fungsi(x_semua), "Model": nama_m}))
    st.dataframe(pd.DataFrame(baris), hide_index=True)
    if len(df) < 4:
        st.caption("Model polinomial baru muncul kalau data minimal 4 bulan.")

    gabung = pd.concat(garis)
    urutan = list(daftar.keys())
    palet = [T["p1"], T["p3"], T["p4"]][: len(urutan)]
    garis_model = (
        alt.Chart(gabung)
        .mark_line(strokeWidth=3)
        .encode(
            x=alt.X("Bulan_Ke:Q", title="Bulan ke-", axis=alt.Axis(tickMinStep=1)),
            y=alt.Y("Penjualan:Q", title="Penjualan (Rp)", axis=alt.Axis(format="~s"), scale=alt.Scale(zero=False)),
            color=alt.Color("Model:N", scale=alt.Scale(domain=urutan, range=palet), legend=alt.Legend(title=None, orient="top")),
        )
    )
    titik_data = (
        alt.Chart(df.rename(columns={"Total_Penjualan": "Penjualan"}))
        .mark_point(filled=True, size=110, color=T["dark"])
        .encode(x="Bulan_Ke:Q", y="Penjualan:Q")
    )
    st.altair_chart(
        (garis_model + titik_data).properties(height=340).configure_view(strokeWidth=0).configure_axis(gridColor=T["border"])
    )
    st.caption(
        "Titik gelap = data asli. Untuk data yang sedikit, model sederhana (linear) biasanya lebih aman; "
        "model yang lebih rumit mudah terlalu menyesuaikan diri dengan data."
    )

# ======================== TAB 5: LAPORAN ========================
with tab5:
    st.subheader("Kesimpulan otomatis 📝")
    st.caption("Teks di bawah bisa langsung disalin ke laporan atau tugas Anda.")
    st.text_area("Kesimpulan siap salin", kesimpulan, height=330)

    GAYA = (
        "body{font-family:'Segoe UI',Arial,sans-serif;max-width:900px;margin:30px auto;padding:0 18px;color:@DARK@;line-height:1.55}"
        "h1{color:@DEEP@;margin-bottom:4px}h2{color:@DEEP@;border-bottom:3px solid @P2@;padding-bottom:4px;margin-top:28px}"
        ".sub{color:@MUTED@;margin-top:0}.box{background:@SOFT@;border-left:6px solid @P1@;padding:10px 16px;border-radius:8px}"
        "table{border-collapse:collapse;width:100%;margin:10px 0}th{background:@P1@;color:#fff;padding:8px;text-align:left}"
        "td{padding:7px 8px;border-bottom:1px solid @BORDER@}tr:nth-child(even) td{background:#fff8fb}"
        ".kecil{color:@MUTED@;font-size:.85rem}"
    )
    for kunci, nilai in [("@DARK@", T["dark"]), ("@DEEP@", T["deep"]), ("@P1@", T["p1"]), ("@P2@", T["p2"]),
                         ("@MUTED@", T["muted"]), ("@SOFT@", T["soft"]), ("@BORDER@", T["border"])]:
        GAYA = GAYA.replace(kunci, nilai)

    data_laporan = df.rename(columns={"Bulan_Ke": "Bulan ke-", "Total_Penjualan": "Total Penjualan"}).copy()
    data_laporan["Total Penjualan"] = data_laporan["Total Penjualan"].map(rp)
    paragraf = "".join(f"<p>{p}</p>" for p in kesimpulan.split("\n\n"))
    html_laporan = (
        "<!DOCTYPE html><html lang='id'><head><meta charset='utf-8'>"
        "<title>Laporan Prediksi Penjualan</title><style>" + GAYA + "</style></head><body>"
        "<h1>Laporan Prediksi Penjualan UMKM</h1>"
        "<p class='sub'>Dibuat otomatis dengan Regresi Linear (scikit-learn)</p>"
        "<h2>1. Data penjualan</h2>" + data_laporan.to_html(index=False, border=0)
        + "<h2>2. Model</h2><div class='box'>Penjualan = " + rp(awal) + (" + " if kenaikan >= 0 else " - ")
        + rp(abs(kenaikan)) + " x Bulan ke-</div>"
        + f"<p>R² = {r2:.3f} &nbsp;|&nbsp; MAE = {rp(mae)} &nbsp;|&nbsp; RMSE = {rp(rmse)} &nbsp;|&nbsp; MAPE = {mape:.1f}%</p>"
        + "<h2>3. Hasil prediksi</h2>" + lengkap_tampil.to_html(index=False, border=0)
        + "<h2>4. Kesimpulan</h2>" + paragraf
        + "<p class='kecil'>Tip: buka file ini di browser, tekan Ctrl+P, lalu pilih 'Simpan sebagai PDF'.</p>"
        "</body></html>"
    )
    st.download_button(
        "⬇️ Unduh laporan lengkap (HTML)",
        html_laporan.encode("utf-8"),
        file_name="laporan_prediksi_penjualan.html",
        mime="text/html",
    )
    st.caption("Buka file hasil unduhan di browser, tekan Ctrl+P, lalu pilih 'Simpan sebagai PDF' kalau butuh PDF.")

# ========================= TAB 6: DATA ==========================
with tab6:
    st.subheader("Data penjualan historis 📋")
    data_tampil = df.rename(columns={"Bulan_Ke": "Bulan ke-", "Total_Penjualan": "Total Penjualan"})
    st.dataframe(data_tampil, hide_index=True)
    st.download_button(
        "⬇️ Unduh data (CSV)",
        df.to_csv(index=False).encode("utf-8"),
        file_name="data_penjualan.csv",
        mime="text/csv",
    )

st.caption(
    "⚠️ Prediksi berupa perkiraan berdasarkan tren. Faktor musiman "
    "(Lebaran, promo, dll.) tidak diperhitungkan otomatis. 🌸"
)
