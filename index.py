import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. Configuração da página
st.set_page_config(page_title="Buena Vista | Dash", layout="wide", page_icon="💰")

# 2. Estilização (Mantida a sua, que está excelente)
st.markdown("""
    <style>
    .section-title {
        font-size: 28px; font-weight: 800; color: #ffffff;
        background-color: #1E88E5; padding: 10px 20px;
        border-radius: 10px; margin-top: 30px; margin-bottom: 20px;
    }
    .ticker-name { font-size: 32px !important; font-weight: 900; color: #4dabf7; }
    .strategy-box { 
        font-size: 15px !important; color: #e9ecef !important; 
        background-color: #343a40; padding: 12px; 
        border-radius: 8px; border-left: 6px solid #4dabf7;
        margin-bottom: 15px; min-height: 90px;
    }
    .alavancado-warning {
        color: #ff4b4b; font-weight: 800; font-size: 11px;
        display: block; margin-top: 8px;
        background-color: rgba(255, 75, 75, 0.1);
        padding: 4px; border-radius: 4px;
    }
    .div-label { color: #888; font-size: 14px; margin-top: 10px; }
    .div-value { color: #40c057; font-size: 22px; font-weight: bold; }
    .error-text { color: #ff6b6b; font-size: 16px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. Categorias (Mantidas)
categorias = {
    "🎯 Estratégias High Income (Renda)": {
        "SPYI11.SA": "S&P 500 + Covered Calls para renda mensal.",
        "QQQI11.SA": "Nasdaq-100 + Covered Calls (Maximização de Dividendos).",
        "IWMI11.SA": "Small Caps (Russell 2000) com estratégia ativa de renda.",
        "GDIV11.SA": "Empresas globais sólidas e baixa volatilidade histórica.",
        "XSPI11.SA": "S&P 500 Alavancado.<br><span class='alavancado-warning'>⚠️ RISCO ALAVANCADO</span>"
    },
    "🌐 Cripto & Ativos Digitais": {
        "COIN11.SA": "Ecossistema Cripto e Blockchain com foco em renda.",
        "ETHY11.SA": "Ethereum + Opções para gerar dividendos.",
        "XBCI11.SA": "Bitcoin Alavancado.<br><span class='alavancado-warning'>⚠️ RISCO ALAVANCADO</span>",
        "GBTC11.SA": "Proteção: Ouro + Bitcoin (Ouro Digital)."
    },
    "🛡️ Proteção & Temáticos": {
        "FIXX11.SA": "Caixa em Dólar (T-Bills 1-3 meses).",
        "AURO11.SA": "Ouro Físico + Estratégia de Renda.",
        "CASA11.SA": "REITs de qualidade (Imobiliário EUA).",
        "PIPE11.SA": "Infraestrutura de Energia e Oleodutos (MLPs).",
        "RICO11.SA": "Portfólio dos maiores Bilionários Institucionais."
    }
}

# 4. Função de busca OTIMIZADA para Nuvem
@st.cache_data(ttl=300) # Cache de 5 min para evitar bloqueio de IP
def buscar_dados_otimizado(ticker_name):
    try:
        tk = yf.Ticker(ticker_name)
        
        # Usar history em vez de info (info quebra na nuvem)
        hist = tk.history(period="1y") 
        if hist.empty: return {"erro": True}
        
        preco_atual = float(hist['Close'].iloc[-1])
        prev_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else preco_atual
        var = ((preco_atual - prev_close) / prev_close) * 100
        
        # Máximas e Mínimas calculadas do histórico (muito mais rápido)
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

# 5. Interface
st.title("📈 Buena Vista ETF Monitor")

# Sidebar para seu controle pessoal
with st.sidebar:
    st.header("Minha Posição")
    st.info("Monitorando: 3.000 cotas de COIN11")
    # Pequeno cálculo de rebalanceamento automático no futuro pode vir aqui
    auto_refresh = st.checkbox("🔄 Auto-Refresh (60s)", value=False)

if st.button("🔄 Forçar Atualização"):
    st.cache_data.clear()
    st.rerun()

# 6. Grid de Ativos
for nome_cat, ativos in categorias.items():
    st.markdown(f"<div class='section-title'>{nome_cat}</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for idx, (ticker, objetivo) in enumerate(ativos.items()):
        with cols[idx % 3]:
            dados = buscar_dados_otimizado(ticker)
            with st.container(border=True):
                st.markdown(f"<div class='ticker-name'>{ticker.split('.')[0]}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='strategy-box'>{objetivo}</div>", unsafe_allow_html=True)
                
                if dados.get("erro"):
                    st.markdown("<div class='error-text'>⚠️ Erro na API (Yahoo)</div>", unsafe_allow_html=True)
                else:
                    st.metric("Preço", f"R$ {dados['preco']:.2f}", f"{dados['variacao']:.2f}%")
                    if dados['div'] > 0:
                        st.markdown(f"""
                            <div class='div-label'>Último Provento</div>
                            <div class='div-value'>R$ {dados['div']:.2f} 
                            <small style='font-size:12px'>(DY: {dados['yield_mensal']:.2f}%)</small></div>
                        """, unsafe_allow_html=True)
                    
                    with st.expander("Detalhes"):
                        st.write(f"**Mín 52s:** R$ {dados['min_52s']:.2f}")
                        st.write(f"**Máx 52s:** R$ {dados['max_52s']:.2f}")
                        st.write(f"**Vol:** {dados['volume']:,.0f}")

# 7. Lógica de Refresh
if auto_refresh:
    time.sleep(60)
    st.rerun()
