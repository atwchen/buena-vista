import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da página
st.set_page_config(page_title="Buena Vista | Dash", layout="wide", page_icon="📈")

# 2. Estilização
st.markdown("""
    <style>
    .section-title { font-size: 24px; font-weight: 800; color: #ffffff; background-color: #1E88E5; padding: 10px 20px; border-radius: 10px; margin-top: 20px; margin-bottom: 15px; }
    .ticker-name { font-size: 26px !important; font-weight: 900; color: #4dabf7; }
    .strategy-box { font-size: 13px !important; color: #e9ecef !important; background-color: #2b2f33; padding: 10px; border-radius: 8px; border-left: 5px solid #4dabf7; margin-bottom: 10px; min-height: 70px; }
    .time-stamp { font-size: 11px; color: #888; margin-top: 5px; font-weight: 600; }
    .stMetric { background-color: #1e2124; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO: TERMÔMETRO VISUAL ---
def termometro_52s(min_val, max_val, atual):
    pos = ((atual - min_val) / (max_val - min_val)) * 100 if max_val != min_val else 50
    pos = max(0, min(100, pos))
    return f"""
    <div style="margin-top: 15px; margin-bottom: 5px; padding: 0 5px;">
        <div style="display: flex; justify-content: space-between; font-size: 11px; color: #888; margin-bottom: 4px;">
            <span>Mín: R$ {min_val:.2f}</span>
            <span>Máx: R$ {max_val:.2f}</span>
        </div>
        <div style="width: 100%; height: 6px; background: linear-gradient(to right, #1E88E5, #fca311, #ff4b4b); border-radius: 3px; position: relative;">
            <div style="position: absolute; left: {pos}%; top: -3px; width: 4px; height: 12px; background-color: #ffffff; border-radius: 2px; box-shadow: 0 0 3px rgba(0,0,0,0.5); transform: translateX(-50%);"></div>
        </div>
    </div>
    """

# 3. Definição do Portfólio
tickers_dict = {
    "🎯 Renda & Índices": ["SPYI11.SA", "QQQI11.SA", "IWMI11.SA", "GDIV11.SA", "QQQQ11.SA", "XSPI11.SA"],
    "🌐 Cripto ativos": ["COIN11.SA", "ETHY11.SA", "XBCI11.SA", "GBTC11.SA"],
    "🛡️ Proteção & Real": ["AURO11.SA", "PIPE11.SA", "CASA11.SA", "FIXX11.SA", "RICO11.SA"]
}
all_tickers = [t for sub in tickers_dict.values() for t in sub]

descricoes = {
    "SPYI11.SA": "S&P 500 + Covered Calls para renda mensal.", "QQQI11.SA": "Nasdaq-100 + Venda de opções.",
    "COIN11.SA": "Ecossistema Cripto e Blockchain.", "IWMI11.SA": "Small Caps (Russell 2000) + Opções.",
    "QQQQ11.SA": "Nasdaq High Beta (Alta Volatilidade).", "CASA11.SA": "REITs de qualidade (Imobiliário EUA).",
    "FIXX11.SA": "Caixa em Dólar (T-Bills 1-3 meses).", "RICO11.SA": "Copia Grandes Bilionários.",
    "GBTC11.SA": "Ouro Físico + Bitcoin.", "AURO11.SA": "Ouro Físico + Renda Mensal.",
    "GDIV11.SA": "Ações globais sólidas e dividendos.", "ETHY11.SA": "Ethereum + Opções.",
    "PIPE11.SA": "Infraestrutura de Energia (MLPs).", "XBCI11.SA": "Bitcoin Alavancado (Yield).",
    "XSPI11.SA": "S&P 500 Alavancado. ⚠️ ALAVANCADO"
}

# --- O RETORNO DO BATCH ESTÁVEL ---
@st.cache_data(ttl=600)
def fetch_data_batch():
    try:
        # Apenas UMA chamada leve e diária. É isso que passa liso no Yahoo.
        return yf.download(all_tickers, period="1y", group_by='ticker', threads=True)
    except:
        return None

with st.spinner("Sincronizando com a B3 em lote..."):
    df_global = fetch_data_batch()

# 5. Sidebar - Calculadora de Rebalanceamento
with st.sidebar:
    st.header("⚖️ Calculadora")
    aporte = st.number_input("Aporte (R$):", min_value=0.0, value=1000.0)
    st.markdown("**Cotas Atuais:**")
    q_spyi = st.number_input("SPYI11", 0)
    q_qqqi = st.number_input("QQQI11", 0)
    q_ethy = st.number_input("ETHY11", 0)
    q_coin = st.number_input("COIN11", 0)
    
    st.markdown("**Alvos (%):**")
    col1, col2 = st.columns(2)
    a_spyi = col1.number_input("% SPYI", 50)
    a_qqqi = col2.number_input("% QQQI", 30)
    a_ethy = col1.number_input("% ETHY", 10)
    a_coin = col2.number_input("% COIN", 10)
    
    if st.button("🚀 Forçar Atualização"):
        st.cache_data.clear()
        st.rerun()

# 6. Dashboard Principal
hora_br = (datetime.utcnow() - timedelta(hours=3)).strftime('%H:%M:%S')
st.title("📈 Monitor Buena Vista ETFs")
st.caption(f"Sincronizado BRT: {hora_br}")

if df_global is not None and not df_global.empty:
    for cat, ativos in tickers_dict.items():
        st.markdown(f"<div class='section-title'>{cat}</div>", unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, t in enumerate(ativos):
            with cols[idx % 3]:
                with st.container(border=True):
                    try:
                        # Limpa dias sem pregão
                        d_ativo = df_global[t].dropna(subset=['Close'])
                        
                        if not d_ativo.empty:
                            p_atual = float(d_ativo['Close'].iloc[-1])
                            p_ant = float(d_ativo['Close'].iloc[-2]) if len(d_ativo) > 1 else p_atual
                            var = ((p_atual - p_ant) / p_ant) * 100
                            
                            min_52, max_52 = float(d_ativo['Low'].min()), float(d_ativo['High'].max())
                            
                            # A SACADA: Formata para exibir APENAS A DATA, removendo o 00:00 chato
                            data_pregao = d_ativo.index[-1].strftime("%d/%m/%Y")
                            
                            st.markdown(f"<div class='ticker-name'>{t.replace('.SA','')}</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='strategy-box'>{descricoes[t]}</div>", unsafe_allow_html=True)
                            st.metric("Cotação", f"R$ {p_atual:.2f}", f"{var:.2f}%")
                            st.markdown(termometro_52s(min_52, max_52, p_atual), unsafe_allow_html=True)
                            
                            # Exibe "Último fechamento" em vez de tentar inventar a hora
                            st.markdown(f"<div class='time-stamp'>📅 Último fechamento: {data_pregao}</div>", unsafe_allow_html=True)
                        else:
                            raise ValueError
                    except:
                        st.markdown(f"<div class='ticker-name'>{t.replace('.SA','')}</div>", unsafe_allow_html=True)
                        st.error("Aguardando histórico...")
else:
    st.warning("⚠️ O Yahoo Finance recusou a conexão temporariamente. Tente novamente em alguns minutos.")

# Auto-refresh
if st.sidebar.toggle("🔄 Auto-Refresh (10 min)", value=False):
    time.sleep(600)
    st.rerun()
