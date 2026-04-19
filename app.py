import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Konfiguracja strony
st.set_page_config(page_title="Kalkulator progów rentowności", layout="wide")

# Stylistyka
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
    dochod_brutto
