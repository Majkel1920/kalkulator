import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -----------------------------
# KONFIGURACJA STRONY
# -----------------------------
st.set_page_config(
    page_title="CreditAI - Kalkulator zdolności kredytowej",
    layout="wide"
)

# -----------------------------
# STYLIZACJA
# -----------------------------
st.markdown("""
    <style>
    .stMetric {
        border: 1px solid #e6e9ef;
        padding: 15px;
        border-radius: 8px;
        background-color: #f8f9fb;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #e6e9ef;
        background-color: #ffffff;
        margin-bottom: 10px;
    }
    .main-title {
        font-size: 34px;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 17px;
        color: #5f6368;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# TYTUŁ
# -----------------------------
st.markdown('<div class="main-title">CreditAI - Kalkulator zdolności kredytowej</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Prototyp bankowego systemu wspomagania decyzji kredytowej z wykorzystaniem reguł eksperckich.</div>',
    unsafe_allow_html=True
)

# -----------------------------
# FUNKCJE POMOCNICZE
# -----------------------------

def oblicz_rate(kwota_kredytu, oprocentowanie_roczne, okres_lat):
    """
    Oblicza miesięczną ratę kredytu przy założeniu rat równych.
    """
    liczba_rat = okres_lat * 12
    oprocentowanie_miesieczne = oprocentowanie_roczne / 100 / 12

    if oprocentowanie_miesieczne == 0:
        return kwota_kredytu / liczba_rat

    rata = kwota_kredytu * (
        oprocentowanie_miesieczne * (1 + oprocentowanie_miesieczne) ** liczba_rat
    ) / (
        (1 + oprocentowanie_miesieczne) ** liczba_rat - 1
    )

    return rata


def oblicz_maksymalna_kwote(max_rata, oprocentowanie_roczne, okres_lat):
    """
    Oblicza maksymalną kwotę kredytu na podstawie maksymalnej akceptowalnej raty.
    """
    liczba_rat = okres_lat * 12
    oprocentowanie_miesieczne = oprocentowanie_roczne / 100 / 12

    if oprocentowanie_miesieczne == 0:
        return max_rata * liczba_rat

    kwota = max_rata * (
        (1 + oprocentowanie_miesieczne) ** liczba_rat - 1
    ) / (
        oprocentowanie_miesieczne * (1 + oprocentowanie_miesieczne) ** liczba_rat
    )

    return kwota


def ocena_zatrudnienia(forma_zatrudnienia):
    """
    Nadaje punkty za stabilność zatrudnienia.
    """
    punkty = {
        "Umowa o pracę na czas nieokreślony": 25,
        "Umowa o pracę na czas określony": 18,
        "Działalność gospodarcza": 16,
        "Umowa zlecenie / o dzieło": 10,
        "Inne / nieregularne źródło dochodu": 5
    }
    return punkty.get(forma_zatrudnienia, 0)


def ocena_historii(historia):
    """
    Nadaje punkty za historię kredytową.
    """
    punkty = {
        "Bardzo dobra": 25,
        "Dobra": 20,
        "Średnia": 12,
        "Słaba": 5,
        "Brak historii": 10
    }
    return punkty.get(historia, 0)


def klasyfikacja_ryzyka(score, dti, bufor):
    """
    Klasyfikuje klienta do poziomu ryzyka.
    """
    if score >= 75 and dti <= 40 and bufor >= 1500:
        return "Niskie ryzyko", "Wysoka szansa na uzyskanie kredytu"
    elif score >= 55 and dti <= 50 and bufor >= 700:
        return "Średnie ryzyko", "Umiarkowana szansa na uzyskanie kredytu"
    else:
        return "Wysokie ryzyko", "Niska szansa na uzyskanie kredytu"


# -----------------------------
# TRYB KREDYTU
# -----------------------------
typ_kredytu = st.radio(
    "Rodzaj analizowanego kredytu",
    ["Kredyt gotówkowy", "Kredyt hipoteczny"],
    horizontal=True
)

# -----------------------------
# SEKCJA 1: DANE KLIENTA
# -----------------------------
with st.expander("1. Dane finansowe klienta", expanded=True):
    col1, col2, col3 = st.columns(3)

    dochod_netto = col1.number_input(
        "Miesięczny dochód netto gospodarstwa domowego",
        min_value=0.0,
        value=7000.0,
        step=500.0
    )

    miesieczne_wydatki = col2.number_input(
        "Stałe miesięczne koszty życia",
        min_value=0.0,
        value=3000.0,
        step=250.0
    )

    obecne_zobowiazania = col3.number_input(
        "Aktualne miesięczne raty i zobowiązania",
        min_value=0.0,
        value=800.0,
        step=100.0
    )

    col4, col5, col6 = st.columns(3)

    liczba_osob = col4.number_input(
        "Liczba osób w gospodarstwie domowym",
        min_value=1,
        value=2,
        step=1
    )

    forma_zatrudnienia = col5.selectbox(
        "Forma zatrudnienia",
        [
            "Umowa o pracę na czas nieokreślony",
            "Umowa o pracę na czas określony",
            "Działalność gospodarcza",
            "Umowa zlecenie / o dzieło",
            "Inne / nieregularne źródło dochodu"
        ]
    )

    historia_kredytowa = col6.selectbox(
        "Historia kredytowa",
        [
            "Bardzo dobra",
            "Dobra",
            "Średnia",
            "Słaba",
            "Brak historii"
        ]
    )

# -----------------------------
# SEKCJA 2: PARAMETRY KREDYTU
# -----------------------------
with st.expander("2. Parametry kredytu", expanded=True):
    col1, col2, col3 = st.columns(3)

    if typ_kredytu == "Kredyt gotówkowy":
        domyslna_kwota = 50000.0
        domyslny_okres = 5
        domyslne_oprocentowanie = 11.5
    else:
        domyslna_kwota = 400000.0
        domyslny_okres = 25
        domyslne_oprocentowanie = 7.5

    kwota_kredytu = col1.number_input(
        "Wnioskowana kwota kredytu",
        min_value=1000.0,
        value=domyslna_kwota,
        step=5000.0
    )

    okres_lat = col2.slider(
        "Okres kredytowania w latach",
        min_value=1,
        max_value=35,
        value=domyslny_okres
    )

    oprocentowanie_roczne = col3.number_input(
        "Oprocentowanie roczne (%)",
        min_value=0.0,
        value=domyslne_oprocentowanie,
        step=0.1
    )

    col4, col5 = st.columns(2)

    limit_dti = col4.slider(
        "Maksymalny akceptowany wskaźnik DTI (%)",
        min_value=20,
        max_value=70,
        value=45
    )

    minimalny_bufor = col5.number_input(
        "Minimalny wymagany bufor po opłaceniu rat",
        min_value=0.0,
        value=1000.0,
        step=100.0
    )

# -----------------------------
# OBLICZENIA
# -----------------------------

rata_kredytu = oblicz_rate(kwota_kredytu, oprocentowanie_roczne, okres_lat)

laczne_zobowiazania_po_kredycie = obecne_zobowiazania + rata_kredytu

dti = (laczne_zobowiazania_po_kredycie / dochod_netto * 100) if dochod_netto > 0 else 0

dochod_rozporzadzalny = dochod_netto - miesieczne_wydatki - obecne_zobowiazania

bufor_po_racie = dochod_netto - miesieczne_wydatki - obecne_zobowiazania - rata_kredytu

maksymalna_bezpieczna_rata = max(
    0,
    (dochod_netto * (limit_dti / 100)) - obecne_zobowiazania
)

maksymalna_kwota_kredytu = oblicz_maksymalna_kwote(
    maksymalna_bezpieczna_rata,
    oprocentowanie_roczne,
    okres_lat
)

# -----------------------------
# SCORING
# -----------------------------

score = 0

# Dochód rozporządzalny
if dochod_rozporzadzalny >= 4000:
    score += 25
elif dochod_rozporzadzalny >= 2500:
    score += 18
elif dochod_rozporzadzalny >= 1000:
    score += 10
else:
    score += 3

# DTI
if dti <= 30:
    score += 25
elif dti <= 40:
    score += 18
elif dti <= 50:
    score += 10
else:
    score += 3

# Zatrudnienie
score += ocena_zatrudnienia(forma_zatrudnienia)

# Historia kredytowa
score += ocena_historii(historia_kredytowa)

# Korekta za liczbę osób
if liczba_osob >= 4:
    score -= 5

score = max(0, min(score, 100))

poziom_ryzyka, rekomendacja = klasyfikacja_ryzyka(score, dti, bufor_po_racie)

# Decyzja systemu
if rata_kredytu <= maksymalna_bezpieczna_rata and bufor_po_racie >= minimalny_bufor and score >= 55:
    decyzja = "Pozytywna wstępna rekomendacja"
elif rata_kredytu <= maksymalna_bezpieczna_rata and score >= 45:
    decyzja = "Warunkowa rekomendacja"
else:
    decyzja = "Negatywna wstępna rekomendacja"

# -----------------------------
# WYNIKI GŁÓWNE
# -----------------------------
st.divider()
st.subheader("Wyniki analizy kredytowej")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Szacowana rata miesięczna",
    f"{round(rata_kredytu, 2)} PLN"
)

c2.metric(
    "Wskaźnik DTI",
    f"{round(dti, 2)}%"
)

c3.metric(
    "Maksymalna zdolność kredytowa",
    f"{round(maksymalna_kwota_kredytu, 2)} PLN"
)

c4.metric(
    "Scoring klienta",
    f"{score}/100"
)

st.divider()

c5, c6, c7 = st.columns(3)

c5.metric(
    "Dochód rozporządzalny przed nowym kredytem",
    f"{round(dochod_rozporzadzalny, 2)} PLN"
)

c6.metric(
    "Bufor po opłaceniu nowej raty",
    f"{round(bufor_po_racie, 2)} PLN"
)

c7.metric(
    "Maksymalna bezpieczna rata",
    f"{round(maksymalna_bezpieczna_rata, 2)} PLN"
)

# -----------------------------
# REKOMENDACJA
# -----------------------------
st.subheader("Rekomendacja systemu")

if decyzja == "Pozytywna wstępna rekomendacja":
    st.success(f"{decyzja}: {rekomendacja}. Poziom ryzyka: {poziom_ryzyka}.")
elif decyzja == "Warunkowa rekomendacja":
    st.warning(f"{decyzja}: {rekomendacja}. Poziom ryzyka: {poziom_ryzyka}.")
else:
    st.error(f"{decyzja}: {rekomendacja}. Poziom ryzyka: {poziom_ryzyka}.")

# Komentarz ekspercki
with st.expander("Komentarz systemu eksperckiego", expanded=True):
    if dti > limit_dti:
        st.write(
            f"- Wskaźnik DTI wynosi {round(dti, 2)}%, czyli przekracza przyjęty limit {limit_dti}%."
        )
    else:
        st.write(
            f"- Wskaźnik DTI wynosi {round(dti, 2)}%, czyli mieści się w przyjętym limicie {limit_dti}%."
        )

    if bufor_po_racie < minimalny_bufor:
        st.write(
            f"- Bufor po spłacie raty wynosi {round(bufor_po_racie, 2)} PLN, czyli jest niższy niż wymagane {minimalny_bufor} PLN."
        )
    else:
        st.write(
            f"- Bufor po spłacie raty wynosi {round(bufor_po_racie, 2)} PLN, czyli spełnia założone minimum."
        )

    if kwota_kredytu > maksymalna_kwota_kredytu:
        st.write(
            "- Wnioskowana kwota kredytu jest wyższa niż szacowana maksymalna zdolność kredytowa."
        )
    else:
        st.write(
            "- Wnioskowana kwota kredytu mieści się w szacowanej zdolności kredytowej klienta."
        )

    st.write(
        "- System nie podejmuje ostatecznej decyzji kredytowej. Pełni funkcję narzędzia wspomagającego analizę klienta."
    )

# -----------------------------
# WYKRES 1: ZDOLNOŚĆ W ZALEŻNOŚCI OD OKRESU
# -----------------------------
st.subheader("Symulacja zdolności kredytowej w zależności od okresu spłaty")

okresy = np.arange(1, 36)
kwoty = [
    oblicz_maksymalna_kwote(
        maksymalna_bezpieczna_rata,
        oprocentowanie_roczne,
        int(okres)
    )
    for okres in okresy
]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=okresy,
    y=kwoty,
    mode="lines+markers",
    name="Szacowana maksymalna kwota kredytu",
    line=dict(width=3)
))

fig.add_hline(
    y=kwota_kredytu,
    line_dash="dash",
    annotation_text="Wnioskowana kwota kredytu",
    annotation_position="top left"
)

fig.update_layout(
    template="plotly_white",
    height=420,
    margin=dict(l=0, r=0, t=30, b=0),
    xaxis_title="Okres kredytowania w latach",
    yaxis_title="Maksymalna kwota kredytu [PLN]"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# WYKRES 2: RATA W ZALEŻNOŚCI OD KWOTY
# -----------------------------
st.subheader("Symulacja miesięcznej raty w zależności od kwoty kredytu")

kwoty_symulacja = np.linspace(
    max(1000, kwota_kredytu * 0.3),
    kwota_kredytu * 1.7,
    40
)

raty_symulacja = [
    oblicz_rate(kwota, oprocentowanie_roczne, okres_lat)
    for kwota in kwoty_symulacja
]

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=kwoty_symulacja,
    y=raty_symulacja,
    mode="lines",
    name="Miesięczna rata",
    line=dict(width=3)
))

fig2.add_hline(
    y=maksymalna_bezpieczna_rata,
    line_dash="dash",
    annotation_text="Maksymalna bezpieczna rata",
    annotation_position="top left"
)

fig2.update_layout(
    template="plotly_white",
    height=420,
    margin=dict(l=0, r=0, t=30, b=0),
    xaxis_title="Kwota kredytu [PLN]",
    yaxis_title="Miesięczna rata [PLN]"
)

st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# TABELA ANALITYCZNA
# -----------------------------
with st.expander("Tabela analityczna - warianty okresu kredytowania"):
    tabela = pd.DataFrame({
        "Okres kredytowania [lata]": okresy,
        "Maksymalna kwota kredytu [PLN]": np.round(kwoty, 2),
        "Rata dla wnioskowanej kwoty [PLN]": [
            round(oblicz_rate(kwota_kredytu, oprocentowanie_roczne, int(okres)), 2)
            for okres in okresy
        ]
    })

    st.dataframe(tabela, use_container_width=True)

# -----------------------------
# OPIS MODELU SI
# -----------------------------
with st.expander("Opis działania systemu SI"):
    st.write("""
    Aplikacja CreditAI jest prototypem systemu wspomagania decyzji kredytowej w bankowości.
    System analizuje dane finansowe klienta, oblicza ratę kredytu, wskaźnik DTI,
    dochód rozporządzalny oraz maksymalną możliwą kwotę finansowania.

    Zastosowany mechanizm można traktować jako prosty system ekspercki.
    Oznacza to, że decyzja nie jest podejmowana losowo, lecz na podstawie zestawu reguł:
    poziomu dochodu, obciążeń finansowych, historii kredytowej, formy zatrudnienia,
    liczby osób w gospodarstwie domowym oraz relacji rat do dochodu.

    System klasyfikuje klienta do jednej z grup ryzyka i generuje wstępną rekomendację:
    pozytywną, warunkową lub negatywną. W realnym wdrożeniu bankowym taki model mógłby
    zostać rozszerzony o uczenie maszynowe trenowane na historycznych danych klientów.
    """)

# -----------------------------
# STOPKA
# -----------------------------
st.caption(
    "Uwaga: kalkulator ma charakter edukacyjny i demonstracyjny. Wyniki nie stanowią rzeczywistej decyzji kredytowej banku."
)
