import streamlit as st
import yfinance as yf
import pandas as pd
import time
import requests
import random
from datetime import datetime, timedelta

# 1. Configuração da página
st.set_page_config(page_title="Buena Vista | Dash", layout="wide", page_icon="📈")

# --- LISTA DE USER-AGENTS PARA EVITAR BLOQUEIO ---
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
]

@st.cache_resource
def get_session():
    session = requests.Session()
    session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
    return session

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
    "XSPI11.SA": "S&P 500 Alavancado. ⚠️"
}

# 4. Busca de Dados
@st.cache_data(ttl=600)
def fetch_data():
    sess = get_session()
    # Puxa 1 ano para as métricas térmicas
    try:
        data_1y = yf.download(all_tickers, period="1y", group_by='ticker', session=sess, threads=True)
        # Puxa 5 dias com intervalo de 1m para o preço real e hora
        data_1m = yf.download(all_tickers, period="5d", interval="1m", group_by='ticker', session=sess, threads=True)
        return data_1y, data_1m
    except:
        return None, None

df_1y, df_1m = fetch_data()

# 5. Sidebar
with st.sidebar:
    st.header("⚖️ Calculadora")
    aporte = st.number_input("Aporte (R$):", min_value=0.0, value=1000.0)
    st.markdown("**Cotas Atuais:**")
    q_spyi = st.number_input("SPYI11", 0)
    q_qqqi = st.number_input("QQQI11", 0)
    q_ethy = st.number_input("ETHY11", 0)
    q_coin = st.number_input("COIN11", 0)
    
    if st.button("🚀 Forçar Atualização"):
        st.cache_data.clear()
        st.rerun()

# 6. Dashboard
hora_br = (datetime.utcnow() - timedelta(hours=3)).strftime('%H:%M:%S')
st.title("📈 Monitor Buena Vista ETFs")
st.caption(f"Sincronizado BRT: {hora_br}")

if df_1y is not None and not df_1y.empty:
    for cat, ativos in tickers_dict.items():
        st.markdown(f"<div class='section-title'>{cat}</div>", unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, t in enumerate(ativos):
            with cols[idx % 3]:
                with st.container(border=True):
                    try:
                        # Extração segura
                        d_long = df_1y[t].dropna()
                        d_short = df_1m[t].dropna() if df_1m is not None else d_long
                        
                        p_atual = float(d_short['Close'].iloc[-1])
                        p_ant = float(d_long['Close'].iloc[-2])
                        var = ((p_atual - p_ant) / p_ant) * 100
                        
                        min_52, max_52 = float(d_long['Low'].min()), float(d_long['High'].max())
                        # Ajuste do Horário (Yahoo traz UTC ou Local da Bolsa)
                        # O index do 1m já costuma vir com o fuso correto
                        hora_txt = d_short.index[-1].strftime("%d/%m %H:%M")
                        
                        st.markdown(f"<div class='ticker-name'>{t.replace('.SA','')}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='strategy-box'>{descricoes[t]}</div>", unsafe_allow_html=True)
                        st.metric("Cotação", f"R$ {p_atual:.2f}", f"{var:.2f}%")
                        st.markdown(termometro_52s(min_52, max_52, p_atual), unsafe_allow_html=True)
                        st.markdown(f"<div class='time-stamp'>🕒 Último negócio: {hora_txt}</div>", unsafe_allow_html=True)
                    except:
                        st.markdown(f"<div class='ticker-name'>{t.replace('.SA','')}</div>", unsafe_allow_html=True)
                        st.error("Sem sinal da B3 no momento.")
else:
    st.warning("⚠️ Erro de conexão com o Yahoo Finance. O servidor deles pode estar recusando requisições da nuvem agora. Tente novamente em 5 minutos.")

# Auto-refresh a cada 10 min
if st.sidebar.toggle("🔄 Auto-Refresh", value=False):
    time.sleep(600)
    st.rerun()
