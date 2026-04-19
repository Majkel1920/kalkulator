import streamlit as st

# Ustawienia strony
st.set_page_config(page_title="Kalkulator Break-even ROAS", page_icon="📊")

st.title("📊 Kalkulator Progu Rentowności (BEP)")
st.write("Oblicz minimalny ROAS i przychód, aby Twoje reklamy nie przynosiły strat.")

# --- SIDEBAR: WEJŚCIE DANYCH ---
st.sidebar.header("Ustawienia Produktu/Biznesu")

# Cena sprzedaży i koszty stałe
cena_sprzedazy = st.sidebar.number_input("Cena sprzedaży brutto (zł)", min_value=1.0, value=100.0, step=1.0)
koszt_produktu = st.sidebar.number_input("Koszt produktu/zakupu netto (zł)", min_value=0.0, value=40.0, step=1.0)
podatek_vat = st.sidebar.selectbox("Stawka VAT (%)", [23, 8, 5, 0], index=0)

# Prowizje i inne koszty zmienne
st.sidebar.subheader("Prowizje i Opłaty")
prowizja_procent = st.sidebar.slider("Prowizja (np. Allegro/Bramka płatnicza) %", 0, 30, 10)
koszty_stale_na_zamowienie = st.sidebar.number_input("Inne koszty na zamówienie (np. opakowanie) zł", min_value=0.0, value=2.0)

# --- LOGIKA OBLICZEŃ ---
# 1. Obliczamy cenę netto
cena_netto = cena_sprzedazy / (1 + podatek_vat/100)

# 2. Koszt prowizji w zł
wartosc_prowizji = cena_netto * (prowizja_procent / 100)

# 3. Marża kwotowa (Zysk przed kosztem reklamy)
marża_na_czysto = cena_netto - koszt_produktu - wartosc_prowizji - koszty_stale_na_zamowienie

# 4. Obliczenie Break-even ROAS (Przychód / Koszt reklamy)
# BEP ROAS = Cena Sprzedaży / Marża na czysto
if marża_na_czysto > 0:
    be_roas = cena_sprzedazy / marża_na_czysto
else:
    be_roas = 0

# --- WIZUALIZACJA WYNIKÓW ---
col1, col2 = st.columns(2)

with col1:
    st.metric("Próg Rentowności (ROAS)", f"{round(be_roas, 2)}x")
    st.caption("Jeśli Twój ROAS jest WYŻSZY niż ten wynik, zarabiasz.")

with col2:
    st.metric("Marża na sztuce (przed reklamą)", f"{round(marża_na_czysto, 2)} zł")
    st.caption("Tyle maksymalnie możesz wydać na pozyskanie jednego zamówienia (CPA).")

st.divider()

# Dodatkowy opis dla "vibe"
if be_roas > 0:
    st.info(f"💡 Aby wyjść na zero, przy sprzedaży za **{cena_sprzedazy} zł**, nie możesz wydać na reklamę więcej niż **{round(marża_na_czysto, 2)} zł**.")
else:
    st.error("⚠️ Uwaga! Twoje koszty są wyższe niż cena netto. Dokładasz do każdego zamówienia nawet bez reklam!")

# --- TABELA PODSUMOWUJĄCA ---
with st.expander("Zobacz szczegóły obliczeń"):
    st.write(f"- Cena netto: {round(cena_netto, 2)} zł")
    st.write(f"- Prowizja: {round(wartosc_prowizji, 2)} zł")
    st.write(f"- Łączne koszty (bez reklam): {round(koszt_produktu + wartosc_prowizji + koszty_stale_na_zamowienie, 2)} zł")
