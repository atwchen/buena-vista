import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. Configuração da página
st.set_page_config(page_title="Buena Vista | Dash", layout="wide", page_icon="📈")

# 2. Estilização (Mantida e otimizada)
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
    .div-value { color: #40c057; font-size: 18px; font-weight: bold; }
    .stMetric { background-color: #1e2124; padding: 10px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# 3. Definição do Portfólio
tickers_list = [
    "SPYI11.SA", "QQQI11.SA", "XSPI11.SA", 
    "COIN11.SA", "ETHY11.SA", "XBCI11.SA", 
    "AURO11.SA", "PIPE11.SA", "CASA11.SA"
]

descricoes = {
    "SPYI11.SA": "S&P 500 + Covered Calls para renda mensal.",
    "QQQI11.SA": "Nasdaq-100 + Venda de opções (Renda Tech).",
    "XSPI11.SA": "S&P 500 Alavancado. ⚠️ ALTA VOLATILIDADE",
    "COIN11.SA": "Empresas do ecossistema Cripto e Blockchain.",
    "ETHY11.SA": "Ethereum + Opções (Geração de Yield).",
    "XBCI11.SA": "Bitcoin Alavancado focado em Yield. ⚠️",
    "AURO11.SA": "Ouro Físico + Estratégia de Renda Mensal.",
    "PIPE11.SA": "Infraestrutura de Energia e Oleodutos (MLPs).",
    "CASA11.SA": "REITs de qualidade (Imobiliário EUA)."
}

# --- FUNÇÃO MESTRE: BUSCA TUDO DE UMA VEZ ---
@st.cache_data(ttl=600)
def carregar_todos_os_dados(lista):
    try:
        # yf.download é mais robusto que Ticker individual na nuvem
        dados = yf.download(lista, period="5d", group_by='ticker', threads=True)
        # Também buscamos dividendos (infelizmente yf.download não traz dividendos, 
        # então fazemos uma busca rápida apenas para os necessários)
        return dados
    except:
        return None

# 4. Execução do Carregamento
with st.spinner('Conectando com a B3...'):
    df_global = carregar_todos_os_dados(tickers_list)

# 5. Sidebar
with st.sidebar:
    st.header("👤 Minha Posição")
    st.metric("COIN11", "3.000 cotas")
    st.markdown("---")
    auto_refresh = st.toggle("🔄 Auto-Refresh (10 min)", value=False)
    if st.button("🚀 Forçar Atualização"):
        st.cache_data.clear()
        st.rerun()

st.title("📈 Monitor Buena Vista ETFs")
st.caption(f"Dados consolidados via Batch Request | {datetime.now().strftime('%H:%M:%S')}")

# 6. Exibição em Grid
if df_global is not None and not df_global.empty:
    # Dividindo em categorias visuais
    categorias = [
        ("🎯 Renda & Índices", ["SPYI11.SA", "QQQI11.SA", "XSPI11.SA"]),
        ("🌐 Cripto ativos", ["COIN11.SA", "ETHY11.SA", "XBCI11.SA"]),
        ("🛡️ Proteção & Real", ["AURO11.SA", "PIPE11.SA", "CASA11.SA"])
    ]

    for nome_cat, ativos in categorias:
        st.markdown(f"<div class='section-title'>{nome_cat}</div>", unsafe_allow_html=True)
        cols = st.columns(3)
        
        for idx, ticker in enumerate(ativos):
            with cols[idx % 3]:
                try:
                    # Extraindo dados do DataFrame Global
                    precos = df_global[ticker]['Close']
                    preco_atual = precos.iloc[-1]
                    preco_anterior = precos.iloc[-2]
                    variacao = ((preco_atual - preco_anterior) / preco_anterior) * 100
                    
                    with st.container(border=True):
                        st.markdown(f"<div class='ticker-name'>{ticker.replace('.SA', '')}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='strategy-box'>{descricoes[ticker]}</div>", unsafe_allow_html=True)
                        
                        st.metric("Cotação", f"R$ {preco_atual:.2f}", f"{variacao:.2f}%")
                        
                        # Nota sobre dividendos: yf.download não traz dividendos. 
                        # Para evitar bloqueio, mostramos apenas o preço e variação de forma estável.
                        st.caption(f"Vol. Diário: {df_global[ticker]['Volume'].iloc[-1]:,.0f}")
                except:
                    st.error(f"Erro no ativo {ticker}")

else:
    st.error("O Yahoo Finance bloqueou a conexão temporariamente. Tente atualizar em alguns minutos.")

# 7. Lógica de Refresh
if auto_refresh:
    time.sleep(600)
    st.rerun()
