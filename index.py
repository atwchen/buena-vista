import streamlit as st
import yfinance as yf
import pandas as pd
import time
import requests
from datetime import datetime

# --- CONFIGURAÇÃO DE SESSÃO (Para evitar bloqueios de IP na Nuvem) ---
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

# 1. Configuração da página
st.set_page_config(page_title="Buena Vista | Dash", layout="wide", page_icon="📈")

# 2. Estilização Customizada
st.markdown("""
    <style>
    .section-title {
        font-size: 26px; font-weight: 800; color: #ffffff;
        background-color: #1E88E5; padding: 10px 20px;
        border-radius: 10px; margin-top: 25px; margin-bottom: 15px;
    }
    .ticker-name { font-size: 28px !important; font-weight: 900; color: #4dabf7; }
    .strategy-box { 
        font-size: 14px !important; color: #e9ecef !important; 
        background-color: #2b2f33; padding: 12px; 
        border-radius: 8px; border-left: 5px solid #4dabf7;
        margin-bottom: 10px; min-height: 80px;
    }
    .alavancado-warning {
        color: #ff4b4b; font-weight: 800; font-size: 11px;
        display: block; margin-top: 5px;
        background-color: rgba(255, 75, 75, 0.1);
        padding: 4px; border-radius: 4px;
    }
    .div-label { color: #888; font-size: 13px; margin-top: 8px; }
    .div-value { color: #40c057; font-size: 20px; font-weight: bold; }
    .stMetric { background-color: #1e2124; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Definição dos Ativos (Filtrados por Liquidez)
categorias = {
    "🎯 Estratégias High Income (Líquidos)": {
        "SPYI11.SA": "Ações do S&P 500 + Covered Calls para renda mensal estável.",
        "QQQI11.SA": "Ações de tecnologia (Nasdaq-100) + Venda de opções.",
        "XSPI11.SA": "S&P 500 Alavancado. <span class='alavancado-warning'>⚠️ ALTA VOLATILIDADE</span>",
    },
    "🌐 Cripto & Ativos Digitais": {
        "COIN11.SA": "Ecossistema Cripto e Blockchain com foco em dividendos.",
        "ETHY11.SA": "Exposição ao Ethereum combinada com venda de opções.",
        "XBCI11.SA": "Bitcoin Alavancado focado em máxima distribuição.<br><span class='alavancado-warning'>⚠️ ALAVANCADO</span>",
    },
    "🛡️ Proteção e Ativos Reais": {
        "AURO11.SA": "Ouro físico aliado à estratégia de renda mensal.",
        "PIPE11.SA": "Infraestrutura de Energia e Oleodutos (MLPs) nos EUA.",
        "CASA11.SA": "Renda dolarizada proveniente de REITs (Imóveis EUA).",
    }
}

# 4. Função de busca Robusta
@st.cache_data(ttl=300)
def buscar_dados_etf(ticker_name):
    try:
        tk = yf.Ticker(ticker_name, session=session)
        # Buscamos 1 ano de histórico para extrair tudo de uma vez (evita tk.info)
        hist = tk.history(period="1y")
        
        if hist.empty:
            return {"erro": True}
        
        preco_atual = float(hist['Close'].iloc[-1])
        prev_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else preco_atual
        var = ((preco_atual - prev_close) / prev_close) * 100
        
        # Máximas e Mínimas calculadas localmente
        max_52s = float(hist['High'].max())
        min_52s = float(hist['Low'].min())
        volume = float(hist['Volume'].iloc[-1])
        
        # Dividendos
        divs = tk.dividends
        ultimo_div = float(divs.iloc[-1]) if not divs.empty else 0.0
        dy_mensal = (ultimo_div / preco_atual) * 100 if preco_atual > 0 else 0.0
        
        return {
            "preco": preco_atual, "variacao": var, "div": ultimo_div,
            "yield_mensal": dy_mensal, "volume": volume,
            "max_52s": max_52s, "min_52s": min_52s,
            "horario": hist.index[-1].strftime("%d/%m %H:%M"),
            "erro": False
        }
    except:
        return {"erro": True}

# 5. Sidebar - Minha Posição e Controles
with st.sidebar:
    st.image("https://buenavista.com.br/wp-content/uploads/2023/04/Logo-Buena-Vista-Horizontal-Branco.png", width=200)
    st.markdown("---")
    st.header("👤 Minha Posição")
    qtd_coin = 3000
    st.metric("COIN11 Acumulado", f"{qtd_coin:,.0f} cotas")
    
    # Dados em tempo real para o Sidebar
    dados_coin = buscar_dados_etf("COIN11.SA")
    if not dados_coin["erro"]:
        patrimonio_coin = qtd_coin * dados_coin["preco"]
        renda_estimada = qtd_coin * dados_coin["div"]
        st.write(f"**Patrimônio:** R$ {patrimonio_coin:,.2f}")
        st.write(f"**Renda do Mês:** R$ {renda_estimada:,.2f}")
    
    st.markdown("---")
    auto_refresh = st.toggle("🔄 Auto-Refresh (60s)", value=False)
    if st.button("🚀 Forçar Atualização"):
        st.cache_data.clear()
        st.rerun()

# 6. Título Principal
st.title("📈 Monitor Buena Vista ETFs")
st.caption(f"Última atualização do servidor: {datetime.now().strftime('%H:%M:%S')}")

# 7. Grid de Exibição
for nome_cat, ativos in categorias.items():
    st.markdown(f"<div class='section-title'>{nome_cat}</div>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for idx, (ticker, objetivo) in enumerate(ativos.items()):
        with cols[idx % 3]:
            dados = buscar_dados_etf(ticker)
            
            with st.container(border=True):
                st.markdown(f"<div class='ticker-name'>{ticker.replace('.SA', '')}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='strategy-box'>{objetivo}</div>", unsafe_allow_html=True)
                
                if dados["erro"]:
                    st.error("Erro ao carregar dados do Yahoo.")
                else:
                    st.metric("Cotação", f"R$ {dados['preco']:.2f}", f"{dados['variacao']:.2f}%")
                    
                    if dados['div'] > 0:
                        st.markdown(f"""
                            <div class='div-label'>Último Provento</div>
                            <div class='div-value'>R$ {dados['div']:.2f} 
                            <span style='font-size:12px; color:#aaa'>(DY: {dados['yield_mensal']:.2f}%)</span></div>
                        """, unsafe_allow_html=True)
                    else:
                        st.caption("Sem dividendos recentes.")

                    with st.expander("📊 Detalhes de Mercado"):
                        col_a, col_b = st.columns(2)
                        col_a.write(f"**Mín 52s:** R${dados['min_52s']:.2f}")
                        col_a.write(f"**Máx 52s:** R${dados['max_52s']:.2f}")
                        col_b.write(f"**Volume:** {dados['volume']:,.0f}")
                        st.caption(f"🕒 {dados['horario']}")

# 8. Rodapé Informativo
st.markdown("---")
st.info("💡 **Dica de Rebalanceamento:** Use os dividendos do COIN11 para comprar SPYI11 e QQQI11, diluindo seu risco sem vender suas cotas.")

# 9. Lógica de Refresh
if auto_refresh:
    time.sleep(60)
    st.rerun()
