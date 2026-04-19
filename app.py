import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Konfiguracja strony
st.set_page_config(page_title="Kalkulator progów rentowności", layout="wide")

# Minimalistyczny styl dla jasnego motywu
st.markdown("""
    <style>
    .stMetric { border: 1px solid #e6e9ef; padding: 15px; border-radius: 5px; background-color: #f8f9fb; }
    .main { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# Wybór trybu na samej górze
mode = st.radio("Model biznesowy", ["E-commerce (BEP)", "Usługi (Lead Generation)"], horizontal=True)

st.title("Kalkulator progów rentowności")
st.divider()

# --- SIDEBAR: KONFIGURACJA ---
st.sidebar.header("Parametry finansowe")
budzet = st.sidebar.number_input("Budzet reklamowy (netto)", min_value=0.0, value=5000.0, step=500.0)
koszt_obslugi = st.sidebar.number_input("Koszt obslugi / agencji (netto)", min_value=0.0, value=0.0, step=100.0)

if mode == "E-commerce (BEP)":
    marza_brutto_procent = st.sidebar.slider("Marza brutto produktu (%)", 1, 100, 40)
    prowizja_procent = st.sidebar.slider("Prowizja platformy / bramki (%)", 0, 30, 12)
    koszt_smart_procent = st.sidebar.slider("Koszt Allegro Smart / Dostawy (%)", 0, 20, 5)
    koszt_opakowania = st.sidebar.number_input("Koszt opakowania na sztuce (netto)", min_value=0.0, value=2.0)
    
    # Zmiana na wpisywanie reczne ROAS
    docelowy_roas = st.sidebar.number_input("Symulowany ROAS", min_value=0.1, max_value=100.0, value=5.0, step=0.1)
    srednia_wartosc_zamowienia = st.sidebar.number_input("Srednia wartosc zamowienia (AOV brutto)", min_value=1.0, value=150.0)
    
    # OBLICZENIA BEP E-COMMERCE
    # Sumujemy koszty procentowe (prowizja + smart)
    total_procent_costs = (prowizja_procent + koszt_smart_procent) / 100
    marza_po_kosztach_proc = (marza_brutto_procent / 100) - total_procent_costs
    
    # Próg rentowności (ROAS) uwzgledniajacy marze po prowizjach
    be_roas = 1 / marza_po_kosztach_proc if marza_po_kosztach_proc > 0 else 0
    
    przychod_symulowany = budzet * docelowy_roas
    liczba_zamowien = przychod_symulowany / srednia_wartosc_zamowienia if srednia_wartosc_zamowienia > 0 else 0
    
    # Zysk = (Przychod * Marza po prowizjach) - Koszty staler (reklama + obsluga + opakowania)
    zysk_calkowity = (przychod_symulowany * marza_po_kosztach_proc) - budzet - koszt_obslugi - (liczba_zamowien * koszt_opakowania)

else:
    wartosc_leada = st.sidebar.number_input("Srednia wartosc klienta (LTV)", min_value=1.0, value=2000.0)
    skutecznosc_sprzedazy = st.sidebar.slider("Skutecznosc sprzedazy z leada (%)", 1, 100, 20)
    docelowy_cpl = st.sidebar.number_input("Symulowany koszt leada (CPL)", min_value=1.0, value=50.0)
    
    liczba_leadow = budzet / docelowy_cpl
    liczba_klientow = liczba_leadow * (skutecznosc_sprzedazy / 100)
    przychod_symulowany = liczba_klientow * wartosc_leada
    zysk_calkowity = przychod_symulowany - budzet - koszt_obslugi
    be_cpl = ((wartosc_leada * (skutecznosc_sprzedazy / 100)) * (budzet / (budzet + koszt_obslugi)) if budzet > 0 else 0)

# --- WIDOK GLOWNY: METRYKI ---
col1, col2, col3 = st.columns(3)

col1.metric("Symulowany Zysk Netto", f"{round(zysk_calkowity, 2)} PLN")
col2.metric("Przychod z symulacji", f"{round(przychod_symulowany, 2)} PLN")

if mode == "E-commerce (BEP)":
    col3.metric("Break-even ROAS", f"{round(be_roas, 2)}x")
else:
    col3.metric("Max CPL (Break-even)", f"{round(be_cpl, 2)} PLN")

st.divider()

# --- WYKRES ---
st.subheader("Symulacja wyniku finansowego")

if mode == "E-commerce (BEP)":
    # Wykres zysku w zaleznosci od ROAS
    x_range = np.linspace(0.5, max(be_roas * 1.5, 15), 50)
    y_profit = [(budzet * x * marza_po_kosztach_proc) - budzet - koszt_obslugi - ((budzet * x / srednia_wartosc_zamowienia) * koszt_opakowania) for x in x_range]
    xlabel = "Poziom ROAS"
else:
    x_range = np.linspace(budzet * 0.5, budzet * 2.0, 20)
    y_profit = [((x / docelowy_cpl * (skutecznosc_sprzedazy / 100) * wartosc_leada) - x - koszt_obslugi) for x in x_range]
    xlabel = "Budzet Reklamowy"

fig = go.Figure()
fig.add_trace(go.Scatter(x=x_range, y=y_profit, mode='lines', name='Zysk', line=dict(color='#28a745', width=3)))
fig.add_hline(y=0, line_dash="dash", line_color="#dc3545")

fig.update_layout(
    template="plotly_white",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis_title=xlabel,
    yaxis_title="Zysk Netto (PLN)",
    margin=dict(l=0, r=0, t=20, b=0)
)
st.plotly_chart(fig, use_container_width=True)

# --- EKSPORT ---
if st.sidebar.button("Generuj raport"):
    raport = f"Kalkulator progow rentownosci - {mode}\nBudzet: {budzet} PLN\nKoszt obslugi: {koszt_obslugi} PLN\nWynik: {round(zysk_calkowity, 2)} PLN"
    st.sidebar.download_button("Pobierz .txt", raport, "raport.txt")
