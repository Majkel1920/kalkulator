import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Konfiguracja strony
st.set_page_config(page_title="Kalkulator progów rentowności", layout="wide")

# Stylistyka jasnego motywu
st.markdown("""
    <style>
    .stMetric { border: 1px solid #e6e9ef; padding: 15px; border-radius: 5px; background-color: #f8f9fb; }
    .main { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

mode = st.radio("Model biznesowy", ["E-commerce (BEP)", "Usługi (Lead Generation)"], horizontal=True)

st.title("Kalkulator progów rentowności")
st.divider()

# --- SIDEBAR: KONFIGURACJA OPERACYJNA ---
st.sidebar.header("Parametry operacyjne")
budzet = st.sidebar.number_input("Budżet reklamowy (netto)", min_value=0.0, value=5000.0, step=500.0)
koszt_obslugi = st.sidebar.number_input("Koszt obsługi / agencji (netto)", min_value=0.0, value=2000.0, step=100.0)

if mode == "E-commerce (BEP)":
    marza_brutto_procent = st.sidebar.slider("Marża brutto produktu (%)", 1, 100, 40)
    prowizja_procent = st.sidebar.slider("Prowizja platformy / bramki (%)", 0, 30, 12)
    koszt_smart_procent = st.sidebar.slider("Koszt Allegro Smart / Dostawy (%)", 0, 20, 5)
    koszt_opakowania = st.sidebar.number_input("Koszt opakowania na sztuce (netto)", min_value=0.0, value=2.0)
    docelowy_roas = st.sidebar.number_input("Symulowany ROAS", min_value=0.1, value=5.0, step=0.1)
    srednia_wartosc_zamowienia = st.sidebar.number_input("Średnia wartość zamówienia (AOV brutto)", min_value=1.0, value=150.0)
    
    marza_po_kosztach_proc = (marza_brutto_procent / 100) - ((prowizja_procent + koszt_smart_procent) / 100)
    be_roas = 1 / marza_po_kosztach_proc if marza_po_kosztach_proc > 0 else 0
    przychod_symulowany = budzet * docelowy_roas
    liczba_zamowien = przychod_symulowany / srednia_wartosc_zamowienia if srednia_wartosc_zamowienia > 0 else 0
    
    # DEFINICJA ZMIENNEJ (Poprawka błędu ze zdjęcia)
    dochod_brutto_firmy = (przychod_symulowany * marza_po_kosztach_proc) - budzet - koszt_obslugi - (liczba_zamowien * koszt_opakowania)

else:
    wartosc_leada = st.sidebar.number_input("Średnia wartość klienta (LTV)", min_value=1.0, value=2000.0)
    skutecznosc_sprzedazy = st.sidebar.slider("Skuteczność sprzedaży (%)", 1, 100, 20)
    docelowy_cpl = st.sidebar.number_input("Symulowany koszt leada (CPL)", min_value=1.0, value=50.0)
    
    liczba_leadow = budzet / docelowy_cpl
    liczba_klientow = liczba_leadow * (skutecznosc_sprzedazy / 100)
    przychod_symulowany = liczba_klientow * wartosc_leada
    
    # DEFINICJA ZMIENNEJ (Poprawka błędu ze zdjęcia)
    dochod_brutto_firmy = przychod_symulowany - budzet - koszt_obslugi
    be_cpl = ((wartosc_leada * (skutecznosc_sprzedazy / 100)) * (budzet / (budzet + koszt_obslugi)) if (budzet + koszt_obslugi) > 0 else 0)

# --- SIDEBAR: PODATKI I ZUS ---
st.sidebar.header("Podatki i ZUS")
typ_zusu = st.sidebar.selectbox("Rodzaj składek ZUS", ["Ulga na start", "ZUS preferencyjny", "Mały ZUS Plus / Normalny"])

zus_slownik = {"Ulga na start": 450, "ZUS preferencyjny": 1150, "Mały ZUS Plus / Normalny": 2150}
zus_wartosc = zus_slownik[typ_zusu]

forma_opodatkowania = st.sidebar.selectbox("Forma opodatkowania", ["Skala podatkowa", "Podatek liniowy", "Ryczałt"])

if forma_opodatkowania == "Skala podatkowa":
    stawka_podatku = st.sidebar.number_input("Stawka podatku (%)", value=12.0)
elif forma_opodatkowania == "Podatek liniowy":
    stawka_podatku = st.sidebar.number_input("Stawka podatku (%)", value=19.0)
else:
    stawka_podatku = st.sidebar.number_input("Stawka ryczałtu (%)", value=8.5)

# Obliczenia końcowe netto
dochod_po_zus = max(0, dochod_brutto_firmy - zus_wartosc)
podatek_kwota = dochod_po_zus * (stawka_podatku / 100)
zysk_na_czysto = dochod_po_zus - podatek_kwota

# --- WIDOK GŁÓWNY: METRYKI ---
c1, c2, c3 = st.columns(3)
c1.metric("Zysk na czysto", f"{round(zysk_na_czysto, 2)} PLN")
c2.metric("Dochód przed podatkiem", f"{round(dochod_brutto_firmy, 2)} PLN")
if mode == "E-commerce (BEP)":
    c3.metric("Break-even ROAS", f"{round(be_roas, 2)}x")
else:
    c3.metric("Max CPL (BEP)", f"{round(be_cpl, 2)} PLN")

st.divider()

# --- WYKRES ---
st.subheader("Wizualizacja rentowności netto")

if mode == "E-commerce (BEP)":
    x_range = np.linspace(0.1, max(be_roas * 1.5, 15), 50)
    y_vals = []
    for x in x_range:
        d_br = (budzet * x * marza_po_kosztach_proc) - budzet - koszt_obslugi - ((budzet * x / srednia_wartosc_zamowienia) * koszt_opakowania)
        d_nt = max(0, d_br - zus_wartosc) * (1 - (stawka_podatku / 100))
        y_vals.append(d_nt)
    xlabel = "Poziom ROAS"
else:
    x_range = np.linspace(budzet * 0.5, budzet * 2.5, 20)
    y_vals = []
    for x in x_range:
        d_br = (x / docelowy_cpl * (skutecznosc_sprzedazy / 100) * wartosc_leada) - x - koszt_obslugi
        d_nt = max(0, d_br - zus_wartosc) * (1 - (stawka_podatku / 100))
        y_vals.append(d_nt)
    xlabel = "Budżet Reklamowy"

fig = go.Figure()
fig.add_trace(go.Scatter(x=x_range, y=y_vals, mode='lines', name='Zysk Netto', line=dict(color='#28a745', width=3)))
fig.add_hline(y=0, line_dash="dash", line_color="#dc3545")
fig.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=20, b=0), xaxis_title=xlabel, yaxis_title="Zysk netto (PLN)")
st.plotly_chart(fig, use_container_width=True)

with st.expander("Szczegóły obciążeń"):
    st.write(f"- Koszty stałe (Reklama + Agencja): {budzet + koszt_obslugi} PLN")
    st.write(f"- Składki ZUS: {zus_wartosc} PLN")
    st.write(f"- Podatek dochodowy ({stawka_podatku}%): {round(podatek_kwota, 2)} PLN")
