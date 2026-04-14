import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. Configuração da página
st.set_page_config(page_title="Buena Vista | Dash", layout="wide", page_icon="📈")

# 2. Estilização
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
    </style>
    """, unsafe_allow_html=True)

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
    "QQQQ11.SA": "Nasdaq High Beta (Foco em empresas de maior volatilidade e crescimento).",
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

# --- FUNÇÃO MESTRE: BUSCA EM LOTE (Evita bloqueios do Yahoo) ---
@st.cache_data(ttl=600)
def carregar_todos_os_dados(lista):
    try:
        dados = yf.download(lista, period="5d", group_by='ticker', threads=True)
        return dados
    except:
        return None

with st.spinner('Conectando com a B3...'):
    df_global = carregar_todos_os_dados(tickers_list)

# 5. Sidebar - CALCULADORA DE APORTE INTELIGENTE (Privada/Sem dados fixos)
with st.sidebar:
    st.header("⚖️ Calculadora de Aporte")
    st.caption("Insira suas cotas atuais para calcular o rebalanceamento da carteira base.")
    
    aporte = st.number_input("💸 Valor do Novo Aporte (R$):", min_value=0.0, value=1000.0, step=100.0)
    
    st.markdown("**Minha Carteira Atual (Cotas):**")
    # Valores zerados por padrão para proteger privacidade no GitHub
    qtd_spyi = st.number_input("SPYI11", min_value=0, value=0, step=1)
    qtd_qqqi = st.number_input("QQQI11", min_value=0, value=0, step=1)
    qtd_ethy = st.number_input("ETHY11", min_value=0, value=0, step=1)
    qtd_coin = st.number_input("COIN11", min_value=0, value=0, step=1)
    
    st.markdown("**Alvos Desejados (%):**")
    col1, col2 = st.columns(2)
    alvo_spyi = col1.number_input("% SPYI", value=50, max_value=100)
    alvo_qqqi = col2.number_input("% QQQI", value=30, max_value=100)
    alvo_ethy = col1.number_input("% ETHY", value=10, max_value=100)
    alvo_coin = col2.number_input("% COIN", value=10, max_value=100)
    
    if st.button("Calcular Rebalanceamento", use_container_width=True):
        if (alvo_spyi + alvo_qqqi + alvo_ethy + alvo_coin) != 100:
            st.error("A soma dos alvos deve ser exatamente 100%.")
        elif df_global is not None and not df_global.empty:
            try:
                # Preços em Tempo Real
                p_spyi = float(df_global['SPYI11.SA']['Close'].iloc[-1])
                p_qqqi = float(df_global['QQQI11.SA']['Close'].iloc[-1])
                p_ethy = float(df_global['ETHY11.SA']['Close'].iloc[-1])
                p_coin = float(df_global['COIN11.SA']['Close'].iloc[-1])
                
                # Patrimônio Atual
                v_spyi = qtd_spyi * p_spyi
                v_qqqi = qtd_qqqi * p_qqqi
                v_ethy = qtd_ethy * p_ethy
                v_coin = qtd_coin * p_coin
                
                pat_atual = v_spyi + v_qqqi + v_ethy + v_coin
                pat_futuro = pat_atual + aporte
                
                # Lógica de Distância do Alvo
                alvos = {'SPYI11': alvo_spyi/100, 'QQQI11': alvo_qqqi/100, 'ETHY11': alvo_ethy/100, 'COIN11': alvo_coin/100}
                valores_atuais = {'SPYI11': v_spyi, 'QQQI11': v_qqqi, 'ETHY11': v_ethy, 'COIN11': v_coin}
                precos = {'SPYI11': p_spyi, 'QQQI11': p_qqqi, 'ETHY11': p_ethy, 'COIN11': p_coin}
                
                deficits = {}
                for ativo, alvo in alvos.items():
                    ideal = pat_futuro * alvo
                    falta = ideal - valores_atuais[ativo]
                    deficits[ativo] = max(0, falta)
                
                soma_deficits = sum(deficits.values())
                
                st.markdown("---")
                st.write(f"**Patrimônio Base:** R$ {pat_atual:,.2f}")
                st.write("🛒 **Ordem de Compra Sugerida:**")
                
                if soma_deficits > 0:
                    compras_feitas = False
                    for ativo, deficit in deficits.items():
                        if deficit > 0:
                            fatia_dinheiro = aporte * (deficit / soma_deficits)
                            if fatia_dinheiro >= precos[ativo]:
                                cotas_comprar = int(fatia_dinheiro // precos[ativo])
                                val_compra = cotas_comprar * precos[ativo]
                                st.success(f"**{ativo}:** {cotas_comprar} cotas (R$ {val_compra:,.2f})")
                                compras_feitas = True
                                
                    if not compras_feitas:
                        st.info("Aporte insuficiente para comprar cotas inteiras dos ativos em déficit.")
                else:
                    st.success("Sua carteira está perfeitamente alinhada com o alvo!")
                    
            except Exception as e:
                st.error("Aguarde a atualização de preços para calcular.")
        else:
            st.warning("Sem dados para calcular. Tente recarregar.")

    st.markdown("---")
    auto_refresh = st.toggle("🔄 Auto-Refresh (10 min)", value=False)
    if st.button("🚀 Forçar Atualização"):
        st.cache_data.clear()
        st.rerun()

# 6. Painel Principal
st.title("📈 Monitor Buena Vista ETFs")
st.caption(f"Dados consolidados via Batch Request | {datetime.now().strftime('%H:%M:%S')}")

if df_global is not None and not df_global.empty:
    # Agrupamento para exibição
    categorias = [
        ("🎯 Renda & Índices Acionários", ["SPYI11.SA", "QQQI11.SA", "IWMI11.SA", "GDIV11.SA", "QQQQ11.SA", "XSPI11.SA"]),
        ("🌐 Cripto & Ativos Digitais", ["COIN11.SA", "ETHY11.SA", "XBCI11.SA", "GBTC11.SA"]),
        ("🛡️ Proteção, Temáticos & Ativos Reais", ["AURO11.SA", "PIPE11.SA", "CASA11.SA", "FIXX11.SA", "RICO11.SA"])
    ]

    for nome_cat, ativos in categorias:
        st.markdown(f"<div class='section-title'>{nome_cat}</div>", unsafe_allow_html=True)
        # Cria colunas limitadas a 3 por linha
        for i in range(0, len(ativos), 3):
            cols = st.columns(3)
            linha_ativos = ativos[i:i+3]
            
            for idx, ticker in enumerate(linha_ativos):
                with cols[idx]:
                    try:
                        precos = df_global[ticker]['Close']
                        preco_atual = precos.iloc[-1]
                        preco_anterior = precos.iloc[-2]
                        variacao = ((preco_atual - preco_anterior) / preco_anterior) * 100
                        volume = df_global[ticker]['Volume'].iloc[-1]
                        
                        with st.container(border=True):
                            st.markdown(f"<div class='ticker-name'>{ticker.replace('.SA', '')}</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='strategy-box'>{descricoes[ticker]}</div>", unsafe_allow_html=True)
                            
                            st.metric("Cotação", f"R$ {preco_atual:.2f}", f"{variacao:.2f}%")
                            st.caption(f"Vol. Diário: {volume:,.0f}")
                    except:
                        # Fallback elegante caso um ativo novo não tenha histórico suficiente
                        with st.container(border=True):
                            st.markdown(f"<div class='ticker-name'>{ticker.replace('.SA', '')}</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='strategy-box'>{descricoes[ticker]}</div>", unsafe_allow_html=True)
                            st.caption("Aguardando volume de negociação...")
else:
    st.error("O Yahoo Finance bloqueou a conexão temporariamente. Tente atualizar em alguns minutos.")

if auto_refresh:
    time.sleep(600)
    st.cache_data.clear()
    st.rerun()
