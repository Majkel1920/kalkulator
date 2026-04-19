import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Konfiguracja strony i ciemny motyw
st.set_page_config(page_title="Business Calculator", layout="wide")

# Wymuszenie minimalistycznego stylu i ciemnych kolorów
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0e1117; color: #ffffff; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .stMetric { border: 1px solid #30363d; padding: 15px; border-radius: 5px; background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

# Wybór trybu na samej górze
mode = st.radio("Model biznesowy", ["E-commerce (ROAS)", "Usługi (Lead Generation)"], horizontal=True)

st.title("Business Performance Simulator")
st.divider()

# --- SIDEBAR: KONFIGURACJA ---
st.sidebar.header("Parametry finansowe")
budzet = st.sidebar.number_input("Budżet reklamowy", min_value=0.0, value=5000.0, step=500.0)

if mode == "E-commerce (ROAS)":
    cena_brutto = st.sidebar.number_input("Cena sprzedaży brutto", min_value=1.0, value=250.0)
    marza_procent = st.sidebar.slider("Marża produktu (%)", 1, 100, 50)
    prowizje = st.sidebar.slider("Prowizje i koszty zmienne (%)", 0, 30, 5)
    docelowy_roas = st.sidebar.slider("Symulowany ROAS", 0.1, 20.0, 4.0, step=0.1)
    
    # Obliczenia E-com
    cena_netto = cena_brutto / 1.23
    marza_kwotowa = (cena_netto * (marza_procent / 100)) - (cena_netto * (prowizje / 100))
    przychod_symulowany = budzet * docelowy_roas
    liczba_zamowien = przychod_symulowany / cena_brutto
    koszt_reklamy_na_sztuke = budzet / liczba_zamowien if liczba_zamowien > 0 else 0
    zysk_calkowity = (marza_kwotowa * liczba_zamowien) - budzet
    be_roas = cena_brutto / marza_kwotowa if marza_kwotowa > 0 else 0

else:
    wartosc_leada = st.sidebar.number_input("Średnia wartość klienta (LTV)", min_value=1.0, value=2000.0)
    skutecznosc_sprzedazy = st.sidebar.slider("Skuteczność sprzedaży z leada (%)", 1, 100, 20)
    docelowy_cpl = st.sidebar.number_input("Symulowany koszt leada (CPL)", min_value=1.0, value=50.0)
    
    # Obliczenia Lead Gen
    liczba_leadow = budzet / docelowy_cpl
    liczba_klientow = liczba_leadow * (skutecznosc_sprzedazy / 100)
    przychod_symulowany = liczba_klientow * wartosc_leada
    zysk_calkowity = przychod_symulowany - budzet
    be_cpl = (wartosc_leada * (skutecznosc_sprzedazy / 100))

# --- WIDOK GŁÓWNY: METRYKI ---
col1, col2, col3 = st.columns(3)

if mode == "E-commerce (ROAS)":
    col1.metric("Symulowany Zysk", f"{round(zysk_calkowity, 2)} PLN")
    col2.metric("Przychód (Brutto)", f"{round(przychod_symulowany, 2)} PLN")
    col3.metric("Break-even ROAS", f"{round(be_roas, 2)}x")
else:
    col1.metric("Symulowany Zysk", f"{round(zysk_calkowity, 2)} PLN")
    col2.metric("Liczba Klientów", f"{int(liczba_klientow)}")
    col3.metric("Max CPL (Break-even)", f"{round(be_cpl, 2)} PLN")

st.divider()

# --- WYKRES SYMULACJI ---
st.subheader("Analiza rentowności w funkcji skali")

# Generowanie danych do wykresu
x_range = np.linspace(budzet * 0.5, budzet * 2.0, 20)
if mode == "E-commerce (ROAS)":
    y_profit = [((marza_kwotowa * (x * docelowy_roas / cena_brutto)) - x) for x in x_range]
    xlabel = "Budżet Reklamowy"
else:
    y_profit = [((x / docelowy_cpl * (skutecznosc_sprzedazy / 100) * wartosc_leada) - x) for x in x_range]
    xlabel = "Budżet Reklamowy"

fig = go.Figure()
fig.add_trace(go.Scatter(x=x_range, y=y_profit, mode='lines+markers', name='Zysk', line=dict(color='#00ff88')))
fig.add_hline(y=0, line_dash="dash", line_color="red")
fig.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=20, r=20, t=20, b=20),
    xaxis_title=xlabel,
    yaxis_title="Zysk Netto"
)
st.plotly_chart(fig, use_container_width=True)

# --- EKSPORT ---
st.sidebar.divider()
if st.sidebar.button("Generuj raport tekstowy"):
    raport = f"Raport Symulacji - {mode}\n"
    raport += f"Budzet: {budzet} PLN\n"
    raport += f"Przewidywany zysk: {round(zysk_calkowity, 2)} PLN\n"
    st.sidebar.download_button("Pobierz plik tekstowy", raport, "raport.txt")
    st.sidebar.info("PDF wymaga dodatkowych bibliotek systemowych. Wygenerowano raport tekstowy jako stabilniejszą alternatywę.")
