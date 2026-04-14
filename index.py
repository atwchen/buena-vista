import streamlit as st
import yfinance as yf
import pandas as pd
import time
import requests
from datetime import datetime, timedelta

# 1. Configuração da página
st.set_page_config(page_title="Buena Vista | Dash", layout="wide", page_icon="📈")

# --- CONFIGURAÇÃO DE SESSÃO (Essencial para não ser bloqueado na nuvem) ---
@st.cache_resource
def get_session():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    return session

# 2. Estilização Global
st.markdown("""
    <style>
    .section-title {
        font-size: 24px; font-weight: 800; color: #ffffff;
        background-color: #1E88E5; padding: 10px 20px;
        border-radius: 10px; margin-top: 20px; margin-bottom: 15px;
    }
    .ticker-name { font-size: 26px !important; font-weight: 900; color: #4dabf7; }
    .strategy-box { 
        font-size: 13px !important; color: #e9ecef !important; 
        background-color: #2b2f33; padding: 10px; 
        border-radius: 8px; border-left: 5px solid #4dabf7;
        margin-bottom: 10px; min-height: 70px;
    }
    .time-stamp { font-size: 11px; color: #888; margin-top: 5px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO: TERMÔMETRO ---
def termometro_52s(min_val, max_val, atual):
    if max_val == min_val: pos = 50
    else:
        pos = ((atual - min_val) / (max_val - min_val)) * 100
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
tickers_list = [
    "SPYI11.SA", "QQQI11.SA", "COIN11.SA", "IWMI11.SA", "QQQQ11.SA", 
    "CASA11.SA", "FIXX11.SA", "RICO11.SA", "GBTC11.SA", "AURO11.SA", 
    "GDIV11.SA", "ETHY11.SA", "PIPE11.SA", "XBCI11.SA", "XSPI11.SA"
]

descricoes = {
    "SPYI11.SA": "S&P 500 + Covered Calls para renda mensal.",
    "QQQI11.SA": "Nasdaq-100 + Venda de opções (Renda Tech).",
    "COIN11.SA": "Empresas do ecossistema Cripto e Blockchain.",
    "IWMI11.SA": "Small Caps (Russell 2000) com venda de opções.",
    "QQQQ11.SA": "Nasdaq High Beta (Empresas de maior volatilidade).",
    "CASA11.SA": "REITs de qualidade (Imobiliário EUA).",
    "FIXX11.SA": "Caixa em Dólar (T-Bills 1-3 meses).",
    "RICO11.SA": "Portfólio que replica as posições de Grandes Bilionários.",
    "GBTC11.SA": "Proteção Mista: Ouro Físico + Bitcoin.",
    "AURO11.SA": "Ouro Físico + Estratégia de Renda Mensal.",
    "GDIV11.SA": "Ações globais sólidas e pagadoras de dividendos.",
    "ETHY11.SA": "Ethereum + Opções (Geração de Yield).",
    "PIPE11.SA": "Infraestrutura de Energia e Oleodutos (MLPs).",
    "XBCI11.SA": "Bitcoin Alavancado focado em Yield.",
    "XSPI11.SA": "S&P 500 Alavancado. ⚠️ ALTA VOLATILIDADE"
}

# --- BUSCA DE DADOS COM TRATAMENTO DE ERRO ---
@st.cache_data(ttl=600)
def buscar_dados_seguro(lista):
    sess = get_session()
    try:
        # Busca 1 ano (Diário) para Termômetro
        df_1y = yf.download(lista, period="1y", group_by='ticker', session=sess, threads=True)
        # Busca 5 dias (1 minuto) para Preço e Hora Real
        df_1m = yf.download(lista, period="5d", interval="1m", group_by='ticker', session=sess, threads=True)
        return df_1y, df_1m
    except:
        return None, None

df_1y, df_1m = buscar_dados_seguro(tickers_list)

# 4. Sidebar
with st.sidebar:
    st.header("⚖️ Calculadora")
    aporte = st.number_input("💸 Novo Aporte (R$):", min_value=0.0, value=1000.0)
    st.markdown("**Cotas Atuais:**")
    qtd_spyi = st.number_input("SPYI11", value=0)
    qtd_qqqi = st.number_input("QQQI11", value=0)
    qtd_ethy = st.number_input("ETHY11", value=0)
    qtd_coin = st.number_input("COIN11", value=0)
    
    if st.button("Calcular Rebalanceamento", use_container_width=True):
        st.info("Cálculo baseado nos preços de mercado atuais.")
        # Lógica simplificada de cálculo para evitar crash
        try:
            p_spyi = df_1m['SPYI11.SA']['Close'].dropna().iloc[-1]
            # (Adicionar lógica de cálculo aqui se desejar, similar ao anterior)
            st.write(f"Preço SPYI: R$ {p_spyi:.2f}")
        except:
            st.error("Dados insuficientes para cálculo.")

    st.markdown("---")
    if st.button("🚀 Atualizar Tudo"):
        st.cache_data.clear()
        st.rerun()

# 5. Dashboard Principal
hora_br = (datetime.utcnow() - timedelta(hours=3)).strftime('%H:%M:%S')
st.title("📈 Monitor Buena Vista ETFs")
st.caption(f"Sincronizado com Brasília: {hora_br}")

if df_1y is not None:
    categorias = [
        ("🎯 Renda & Índices", ["SPYI11.SA", "QQQI11.SA", "IWMI11.SA", "GDIV11.SA", "QQQQ11.SA", "XSPI11.SA"]),
        ("🌐 Cripto ativos", ["COIN11.SA", "ETHY11.SA", "XBCI11.SA", "GBTC11.SA"]),
        ("🛡️ Proteção & Real", ["AURO11.SA", "PIPE11.SA", "CASA11.SA", "FIXX11.SA", "RICO11.SA"])
    ]

    for nome_cat, ativos in categorias:
        st.markdown(f"<div class='section-title'>{nome_cat}</div>", unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, ticker in enumerate(ativos):
            with cols[idx % 3]:
                with st.container(border=True):
                    try:
                        # Extração segura dos dados
                        d_1y = df_1y[ticker].dropna()
                        d_1m = df_1m[ticker].dropna() if df_1m is not None else d_1y
                        
                        p_atual = float(d_1m['Close'].iloc[-1])
                        p_ant = float(d_1y['Close'].iloc[-2])
                        var = ((p_atual - p_ant) / p_ant) * 100
                        
                        min_52 = float(d_1y['Low'].min())
                        max_52 = float(d_1y['High'].max())
                        # Ajuste de hora (se index for datetime)
                        hora_txt = d_1m.index[-1].strftime("%d/%m %H:%M")
                        
                        st.markdown(f"<div class='ticker-name'>{ticker.replace('.SA','')}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='strategy-box'>{descricoes[ticker]}</div>", unsafe_allow_html=True)
                        st.metric("Cotação", f"R$ {p_atual:.2f}", f"{var:.2f}%")
                        st.markdown(termometro_52s(min_52, max_52, p_atual), unsafe_allow_html=True)
                        st.markdown(f"<div class='time-stamp'>🕒 Negócio: {hora_txt}</div>", unsafe_allow_html=True)
                    except:
                        st.warning(f"Dados de {ticker} temporariamente indisponíveis.")
else:
    st.error("Erro ao conectar com a API. Tente forçar a atualização.")
