import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Konfiguracja strony
st.set_page_config(page_title="Kalkulator progów rentowności", layout="wide")

# Stylizacja dla lepszego widoku mobilnego
st.markdown("""
    <style>
    .stMetric { border: 1px solid #e6e9ef; padding: 15px; border-radius: 5px; background-color: #f8f9fb; }
    div[data-testid="stExpander"] { border: 1px solid #e6e9ef; background-color: #ffffff; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("Kalkulator progów rentowności")

# WYBÓR TRYBU NA GÓRZE
mode = st.radio("Model biznesowy", ["E-commerce (BEP)", "Usługi (Lead Generation)"], horizontal=True)

# --- SEKCJA 1: PARAMETRY OPERACYJNE ---
with st.expander("1. Konfiguracja budżetu i kosztów", expanded=True):
    col_a, col_b = st.columns(2)
    budzet = col_a.number_input("Budżet reklamowy (netto)", min_value=0.0, value=5000.0, step=500.0)
    koszt_obslugi = col_b.number_input("Koszt obsługi / agencji (netto)", min_value=0.0, value=2000.0, step=100.0)

if mode == "E-commerce (BEP)":
    with st.expander("2. Parametry sprzedaży i ROAS", expanded=True):
        c1, c2, c3 = st.columns(3)
        marza_brutto_procent = c1.slider("Marża brutto produktu (%)", 1, 100, 40)
        prowizja_procent = c2.slider("Prowizja platformy (%)", 0, 30, 12)
        koszt_smart_procent = c3.slider("Koszt Dostawy / Smart (%)", 0, 20, 5)
        
        c4, c5, c6 = st.columns(3)
        docelowy_roas = c4.number_input("Symulowany ROAS", min_value=0.1, value=5.0, step=0.1)
        srednia_wartosc_zamowienia = c5.number_input("Średnia wartość zamówienia (AOV)", min_value=1.0, value=150.0)
        koszt_opakowania = c6.number_input("Koszt opakowania (netto/szt)", min_value=0.0, value=2.0)
    
    # Obliczenia E-com
    marza_po_kosztach_proc = (marza_brutto_procent / 100) - ((prowizja_procent + koszt_smart_procent) / 100)
    be_roas = 1 / marza_po_kosztach_proc if marza_po_kosztach_proc > 0 else 0
    przychod_symulowany = budzet * docelowy_roas
    liczba_zamowien = przychod_symulowany / srednia_wartosc_zamowienia if srednia_wartosc_zamowienia > 0 else 0
    dochod_brutto_firmy = (przychod_symulowany * marza_po_kosztach_proc) - budzet - koszt_obslugi - (liczba_zamowien * koszt_opakowania)

else:
    with st.expander("2. Parametry lejka sprzedażowego", expanded=True):
        c1, c2, c3 = st.columns(3)
        wartosc_leada = c1.number_input("Wartość klienta (LTV)", min_value=1.0, value=2000.0)
        skutecznosc_sprzedazy = c2.slider("Skuteczność sprzedaży (%)", 1, 100, 20)
        docelowy_cpl = c3.number_input("Koszt leada (CPL)", min_value=1.0, value=50.0)
    
    # Obliczenia Lead Gen
    liczba_leadow = budzet / docelowy_cpl
    liczba_klientow = liczba_leadow * (skutecznosc_sprzedazy / 100)
    przychod_symulowany = liczba_klientow * wartosc_leada
    dochod_brutto_firmy = przychod_symulowany - budzet - koszt_obslugi
    be_cpl = ((wartosc_leada * (skutecznosc_sprzedazy / 100)) * (budzet / (budzet + koszt_obslugi)) if (budzet + koszt_obslugi) > 0 else 0)
    be_roas = 0 # Inicjalizacja dla wykresu

# --- SEKCJA 2: PODATKI I ZUS ---
with st.expander("3. Podatki i ZUS", expanded=True):
    col_z, col_p = st.columns(2)
    typ_zusu = col_z.selectbox("Rodzaj składek ZUS", ["Ulga na start", "ZUS preferencyjny", "Mały ZUS Plus / Normalny"])
    forma_opodatkowania = col_p.selectbox("Forma opodatkowania", ["Skala podatkowa", "Podatek liniowy", "Ryczałt"])
    
    if forma_opodatkowania == "Skala podatkowa":
        stawka_podatku = st.select_slider("Wybierz próg podatkowy (%)", options=[12, 32], value=12)
    elif forma_opodatkowania == "Podatek liniowy":
        stawka_podatku = 19
        st.info("Podatek liniowy: stała stawka 19%")
    else: # Ryczałt
        stawka_podatku = st.selectbox("Wybierz stawkę ryczałtu (%)", [2, 3, 5.5, 8.5, 10, 12, 14, 15, 17], index=3)

# Obliczenia końcowe
zus_slownik = {"Ulga na start": 450, "ZUS preferencyjny": 1150, "Mały ZUS Plus / Normalny": 2150}
zus_wartosc = zus_slownik[typ_zusu]
dochod_po_zus = max(0, dochod_brutto_firmy - zus_wartosc)
podatek_kwota = dochod_po_zus * (stawka_podatku / 100)
zysk_na_czysto = dochod_po_zus - podatek_kwota

st.divider()

# --- WIDOK GŁÓWNY: WYNIKI ---
c1, c2, c3 = st.columns(3)
c1.metric("Zysk na czysto (Netto)", f"{round(zysk_na_czysto, 2)} PLN")
c2.metric("Dochód przed podatkiem", f"{round(dochod_brutto_firmy, 2)} PLN")
if mode == "E-commerce (BEP)":
    c3.metric("Break-even ROAS", f"{round(be_roas, 2)}x")
else:
    c3.metric("Max CPL (BEP)", f"{round(be_cpl, 2)} PLN")

# --- WYKRES ---
st.subheader("Wizualizacja rentowności netto")
# Naprawiona linia 96 (domknięcie nawiasów)
if mode == "E-commerce (BEP)":
    x_range = np.linspace(0.1, max(be_roas * 1.5, 15), 50)
else:
    x_range = np.linspace(budzet * 0.5, budzet * 2.5, 20)

y_vals = []
for x in x_range:
    if mode == "E-commerce (BEP)":
        d_br = (budzet * x * marza_po_kosztach_proc) - budzet - koszt_obslugi - ((budzet * x / srednia_wartosc_zamowienia) * koszt_opakowania)
    else:
        d_br = (x / docelowy_cpl * (skutecznosc_sprzedazy / 100) * wartosc_leada) - x - koszt_obslugi
    d_nt = max(0, d_br - zus_wartosc) * (1 - (stawka_podatku / 100))
    y_vals.append(d_nt)

fig = go.Figure()
fig.add_trace(go.Scatter(x=x_range, y=y_vals, mode='lines', name='Zysk Netto', line=dict(color='#28a745', width=3)))
fig.add_hline(y=0, line_dash="dash", line_color="#dc3545")
fig.update_layout(template="plotly_white", height=400, margin=dict(l=0, r=0, t=20, b=0))
st.plotly_chart(fig, use_container_width=True)

with st.expander("Szczegóły obciążeń"):
    st.write(f"- Składki ZUS: {zus_wartosc} PLN")
    st.write(f"- Podatek dochodowy ({stawka_podatku}%): {round(podatek_kwota, 2)} PLN")
    st.write(f"- Koszty stałe operacyjne (Budżet + Obsługa): {budzet + koszt_obslugi} PLN")
    
