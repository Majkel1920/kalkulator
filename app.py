import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Konfiguracja strony
st.set_page_config(page_title="Business Performance Simulator", layout="wide")

# Minimalistyczny styl dla jasnego motywu
st.markdown("""
    <style>
    .stMetric { border: 1px solid #e6e9ef; padding: 15px; border-radius: 5px; background-color: #f8f9fb; }
    .main { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# Wybór trybu na samej górze
mode = st.radio("Model biznesowy", ["E-commerce (BEP)", "Usługi (Lead Generation)"], horizontal=True)

st.title("Business Performance Simulator")
st.divider()

# --- SIDEBAR: KONFIGURACJA ---
st.sidebar.header("Parametry finansowe")
budzet = st.sidebar.number_input("Budzet reklamowy", min_value=0.0, value=5000.0, step=500.0)

if mode == "E-commerce (BEP)":
    marza_brutto_procent = st.sidebar.slider("Marza brutto produktu (%)", 1, 100, 40)
    prowizja_procent = st.sidebar.slider("Prowizja platformy / bramki (%)", 0, 30, 12)
    koszt_opakowania = st.sidebar.number_input("Koszt opakowania (szt)", min_value=0.0, value=2.0)
    koszt_smart = st.sidebar.number_input("Koszt Allegro Smart / Dostawy (szt)", min_value=0.0, value=4.99)
    docelowy_roas = st.sidebar.slider("Symulowany ROAS", 0.1, 100.0, 5.0, step=0.1)
    srednia_wartosc_zamowienia = st.sidebar.number_input("Srednia wartosc zamowienia (AOV)", min_value=1.0, value=150.0)
    
    # OBLICZENIA BEP E-COMMERCE
    marza_po_prowizji = (marza_brutto_procent - prowizja_procent) / 100
    be_roas = 1 / marza_po_prowizji if marza_po_prowizji > 0 else 0
    
    przychod_symulowany = budzet * docelowy_roas
    liczba_zamowien = przychod_symulowany / srednia_wartosc_zamowienia if srednia_wartosc_zamowienia > 0 else 0
    
    koszty_operacyjne = liczba_zamowien * (koszt_opakowania + koszt_smart)
    zysk_calkowity = (przychod_symulowany * marza_po_prowizji) - budzet - koszty_operacyjne

else:
    wartosc_leada = st.sidebar.number_input("Srednia wartosc klienta (LTV)", min_value=1.0, value=2000.0)
    skutecznosc_sprzedazy = st.sidebar.slider("Skutecznosc sprzedazy z leada (%)", 1, 100, 20)
    docelowy_cpl = st.sidebar.number_input("Symulowany koszt leada (CPL)", min_value=1.0, value=50.0)
    
    liczba_leadow = budzet / docelowy_cpl
    liczba_klientow = liczba_leadow * (skutecznosc_sprzedazy / 100)
    przychod_symulowany = liczba_klientow * wartosc_leada
    zysk_calkowity = przychod_symulowany - budzet
    be_cpl = (wartosc_leada * (skutecznosc_sprzedazy / 100))

# --- WIDOK GLOWNY: METRYKI ---
col1, col2, col3 = st.columns(3)

if mode == "E-commerce (BEP)":
    col1.metric("Symulowany Zysk Netto", f"{round(zysk_calkowity, 2)} PLN")
    col2.metric("Przychod z symulacji", f"{round(przychod_symulowany, 2)} PLN")
    col3.metric("Break-even ROAS", f"{round(be_roas, 2)}x")
else:
    col1.metric("Symulowany Zysk Netto", f"{round(zysk_calkowity, 2)} PLN")
    col2.metric
