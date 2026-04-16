import streamlit as st
import pandas as pd
import data_orchestrator
import ui_components
import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Monitor de Mercado | + Copilot", page_icon="📈", layout="wide")
ui_components.apply_custom_styles()
ui_components.render_header()

st.title("📊 Monitor de Mercado en Tiempo Real")
st.markdown("Visualización de datos financieros, bonos y fondos comunes de inversión.")

# --- OBTENCIÓN DE DATOS ---
with st.sidebar:
    st.header("Configuración")
    if st.button("🔄 Actualizar Datos"):
        st.cache_data.clear()
        st.rerun()
    
    st.info(f"Última actualización: {datetime.datetime.now().strftime('%H:%M:%S')}")

@st.cache_data(ttl=600)  # Caché de 10 minutos
def load_market_data():
    return data_orchestrator.get_all_market_context()

market_context = load_market_data()

if not market_context:
    st.error("No se pudieron cargar los datos de mercado. Por favor, reintenta más tarde.")
    st.stop()

# --- INTERFAZ DE TABS ---
tab_dolar, tab_bonos, tab_fci, tab_bcra = st.tabs([
    "📜 Bonos y Letras", 
    "💵 Dólares y Riesgo", 
    "🏦 FCIs (Rendimientos)", 
    "🏛️ BCRA e Indicadores"
])

# 1. TAB: BONOS Y LETRAS
with tab_bonos:
    col_b1, col_b2 = st.columns(2)
    
    with col_b1:
        st.subheader("Bonos Soberanos (USD)")
        sovereign = market_context.get("sovereign_bonds", [])
        if sovereign:
            df_sov = pd.DataFrame(sovereign)
            st.dataframe(df_sov[["symbol", "price_usd", "pct_change", "bid", "ask"]].sort_values("symbol"), 
                         use_container_width=True, hide_index=True)
        else:
            st.warning("No hay datos de bonos soberanos.")

    with col_b2:
        st.subheader("LECAPs y BONCAPs")
        lecap = market_context.get("lecap_boncap", [])
        if lecap:
            df_lecap = pd.DataFrame(lecap)
            st.dataframe(df_lecap[["symbol", "type", "price", "bid", "ask"]], 
                         use_container_width=True, hide_index=True)
        else:
            st.warning("No hay datos de LECAPs/BONCAPs.")

# 2. TAB: DOLARES Y RIESGO
with tab_dolar:
    st.subheader("Cotizaciones Principales")
    rates = market_context.get("exchange_rates", {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        price = rates.get("oficial", {}).get("price", "N/A")
        st.metric("Dólar Oficial", f"${price}")
    
    with col2:
        price = rates.get("mep", {}).get("price", "N/A")
        st.metric("Dólar MEP", f"${price}")
        
    with col3:
        price = rates.get("ccl", {}).get("price", "N/A")
        st.metric("Dólar CCL", f"${price}")
        
    with col4:
        value = rates.get("riesgo_pais", {}).get("value", "N/A")
        st.metric("Riesgo País", f"{value} bps")

    st.divider()
    
    # Cotizaciones BCRA
    bcra_rates = market_context.get("bcra_exchange_rates_summary", {})
    if bcra_rates.get("destacadas"):
        st.subheader("Otras Monedas (BCRA)")
        df_bcra_rates = pd.DataFrame(bcra_rates["destacadas"])
        st.dataframe(df_bcra_rates[["nombre", "codigo", "cotizacion"]], use_container_width=True, hide_index=True)

# 3. TAB: FCIs (RENDIMIENTOS)
with tab_fci:
    st.subheader("Rendimientos de Fondos Comunes de Inversión")
    fci_data = market_context.get("fci_data", [])
    
    if fci_data:
        df_fci = pd.DataFrame(fci_data)
        # Formatear columnas
        df_fci['tna'] = df_fci['tna'].map('{:.2f}%'.format)
        df_fci['patrimonio'] = df_fci['patrimonio'].map('${:,.0f}'.format)
        
        st.dataframe(df_fci[["nombre", "tna", "patrimonio", "fechaHasta"]].sort_values("tna", ascending=False), 
                     use_container_width=True, hide_index=True)
    else:
        st.warning("No hay datos de rendimientos de FCIs.")

# 4. TAB: BCRA E INDICADORES
with tab_bcra:
    st.subheader("Indicadores Macroeconómicos (BCRA)")
    bcra_macro = market_context.get("bcra_macro_indicators", {}).get("data", [])
    
    if bcra_macro:
        df_macro = pd.DataFrame(bcra_macro)
        # Organizar por categorías
        categorias = df_macro['categoria'].unique()
        for cat in categorias:
            with st.expander(f"📌 {cat}", expanded=True):
                df_cat = df_macro[df_macro['categoria'] == cat]
                st.dataframe(df_cat[["nombre", "valor", "unidad", "fecha"]], 
                             use_container_width=True, hide_index=True)
    else:
        st.warning("No hay datos macroeconómicos del BCRA.")

st.info("⚠️ Los datos mostrados tienen fines informativos y provienen de fuentes públicas.")
