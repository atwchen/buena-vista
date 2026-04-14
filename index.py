import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. Configuração da página
st.set_page_config(page_title="Buena Vista | Dash", layout="wide", page_icon="📈")

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
    .alavancado-warning {
        color: #ff4b4b; font-weight: 800; font-size: 11px;
        display: block; margin-top: 5px;
        background-color: rgba(255, 75, 75, 0.1);
        padding: 4px; border-radius: 4px;
    }
    .time-stamp {
        font-size: 11px;
        color: #888;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO: GRÁFICO DE TEMPERATURA HTML/CSS ---
def termometro_52s(min_val, max_val, atual):
    if max_val == min_val:
        pos = 50
    else:
        pos = ((atual - min_val) / (max_val - min_val)) * 100
        pos = max(0, min(100, pos))
    
    html = f"""
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
    return html

# 3. Definição do Portfólio Completo Buena Vista
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
    "XBCI11.SA": "Bitcoin Alavancado focado em Yield. <span class='alavancado-warning'>⚠️ ALAVANCADO</span>",
    "XSPI11.SA": "S&P 500 Alavancado. <span class='alavancado-warning'>⚠️ ALTA VOLATILIDADE</span>"
}

# --- BUSCA EM LOTE ---
@st.cache_data(ttl=600)
def carregar_todos_os_dados(lista):
    try:
        # Puxamos 1 ano para ter o histórico de 52 semanas
        dados = yf.download(lista, period="1y", group_by='ticker', threads=True)
        return dados
    except:
        return None

with st.spinner('Sincronizando dados com a B3...'):
    df_global = carregar_todos_os_dados(tickers_list)

# 5. Sidebar - CALCULADORA DE REBALANCEAMENTO
with st.sidebar:
    st.header("⚖️ Calculadora de Aporte")
    aporte = st.number_input("💸 Novo Aporte (R$):", min_value=0.0, value=1000.0, step=100.0)
    
    st.markdown("**Minhas Cotas:**")
    # Iniciando zerado para privacidade
    qtd_spyi = st.number_input("SPYI11", min_value=0, value=0)
    qtd_qqqi = st.number_input("QQQI11", min_value=0, value=0)
    qtd_ethy = st.number_input("ETHY11", min_value=0, value=0)
    qtd_coin = st.number_input("COIN11", min_value=0, value=0)
    
    st.markdown("**Alvos (%):**")
    col1, col2 = st.columns(2)
    alvo_spyi = col1.number_input("% SPYI", value=50)
    alvo_qqqi = col2.number_input("% QQQI", value=30)
    alvo_ethy = col1.number_input("% ETHY", value=10)
    alvo_coin = col2.number_input("% COIN", value=10)
    
    if st.button("Calcular Rebalanceamento", use_container_width=True):
        if (alvo_spyi + alvo_qqqi + alvo_ethy + alvo_coin) != 100:
            st.error("Soma dos alvos deve ser 100%.")
        elif df_global is not None:
            try:
                p_spyi = float(df_global['SPYI11.SA']['Close'].dropna().iloc[-1])
                p_qqqi = float(df_global['QQQI11.SA']['Close'].dropna().iloc[-1])
                p_ethy = float(df_global['ETHY11.SA']['Close'].dropna().iloc[-1])
                p_coin = float(df_global['COIN11.SA']['Close'].dropna().iloc[-1])
                
                v_atuais = {
                    'SPYI11': qtd_spyi * p_spyi, 'QQQI11': qtd_qqqi * p_qqqi,
                    'ETHY11': qtd_ethy * p_ethy, 'COIN11': qtd_coin * p_coin
                }
                
                pat_futuro = sum(v_atuais.values()) + aporte
                alvos = {'SPYI11': alvo_spyi/100, 'QQQI11': alvo_qqqi/100, 'ETHY11': alvo_ethy/100, 'COIN11': alvo_coin/100}
                precos = {'SPYI11': p_spyi, 'QQQI11': p_qqqi, 'ETHY11': p_ethy, 'COIN11': p_coin}
                
                st.markdown("---")
                st.write("🛒 **Sugestão de Compra:**")
                for ativo, alvo in alvos.items():
                    ideal = pat_futuro * alvo
                    falta = max(0, ideal - v_atuais[ativo])
                    if falta >= precos[ativo]:
                        cotas = int(falta // precos[ativo])
                        st.success(f"**{ativo}:** {cotas} cotas")
            except:
                st.error("Erro nos cálculos. Verifique os dados.")

    st.markdown("---")
    auto_refresh = st.toggle("🔄 Auto-Refresh (10 min)", value=False)
    if st.button("🚀 Forçar Atualização"):
        st.cache_data.clear()
        st.rerun()

# 6. Painel Principal
st.title("📈 Monitor Buena Vista ETFs")
st.caption(f"Dados consolidados via Yahoo Finance | {datetime.now().strftime('%H:%M:%S')}")

if df_global is not None and not df_global.empty:
    categorias = [
        ("🎯 Renda & Índices Acionários", ["SPYI11.SA", "QQQI11.SA", "IWMI11.SA", "GDIV11.SA", "QQQQ11.SA", "XSPI11.SA"]),
        ("🌐 Cripto & Ativos Digitais", ["COIN11.SA", "ETHY11.SA", "XBCI11.SA", "GBTC11.SA"]),
        ("🛡️ Proteção, Temáticos & Ativos Reais", ["AURO11.SA", "PIPE11.SA", "CASA11.SA", "FIXX11.SA", "RICO11.SA"])
    ]

    for nome_cat, ativos in categorias:
        st.markdown(f"<div class='section-title'>{nome_cat}</div>", unsafe_allow_html=True)
        for i in range(0, len(ativos), 3):
            cols = st.columns(3)
            for idx, ticker in enumerate(ativos[i:i+3]):
                with cols[idx]:
                    try:
                        df_ativo = df_global[ticker].dropna(subset=['Close'])
                        if not df_ativo.empty:
                            preco_atual = float(df_ativo['Close'].iloc[-1])
                            preco_ant = float(df_ativo['Close'].iloc[-2]) if len(df_ativo) > 1 else preco_atual
                            var = ((preco_atual - preco_ant) / preco_ant) * 100
                            
                            # CÁLCULO DE HORÁRIO E HISTÓRICO
                            horario_negoc = df_ativo.index[-1].strftime("%d/%m %H:%M")
                            min_52s = float(df_ativo['Low'].min())
                            max_52s = float(df_ativo['High'].max())
                            
                            with st.container(border=True):
                                st.markdown(f"<div class='ticker-name'>{ticker.replace('.SA', '')}</div>", unsafe_allow_html=True)
                                st.markdown(f"<div class='strategy-box'>{descricoes[ticker]}</div>", unsafe_allow_html=True)
                                
                                st.metric("Cotação", f"R$ {preco_atual:.2f}", f"{var:.2f}%")
                                
                                # Termômetro Visual
                                st.markdown(termometro_52s(min_52s, max_52s, preco_atual), unsafe_allow_html=True)
                                
                                # TIMESTAMP DA ÚLTIMA NEGOCIAÇÃO
                                st.markdown(f"<div class='time-stamp'>🕒 Última Negociação: {horario_negoc}</div>", unsafe_allow_html=True)
                        else:
                            raise ValueError
                    except:
                        with st.container(border=True):
                            st.markdown(f"<div class='ticker-name'>{ticker.replace('.SA', '')}</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='strategy-box'>{descricoes[ticker]}</div>", unsafe_allow_html=True)
                            st.caption("Aguardando pregão...")
else:
    st.error("Conexão instável. Tente atualizar em alguns minutos.")

if auto_refresh:
    time.sleep(600)
    st.rerun()
