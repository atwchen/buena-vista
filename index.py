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
    .ticker-name { font-size: 26px !important; font-weight: 900; color: #4dabf7; margin-bottom: 5px;}
    .strategy-box { font-size: 13px !important; color: #e9ecef !important; background-color: #2b2f33; padding: 10px; border-radius: 8px; border-left: 5px solid #4dabf7; margin-bottom: 10px; min-height: 70px; }
    .div-box { background-color: rgba(64, 192, 87, 0.1); padding: 8px; border-radius: 5px; margin-top: 10px; border-left: 3px solid #40c057;}
    .div-value { color: #40c057; font-size: 14px; font-weight: bold; }
    .div-yield { color: #aaa; font-size: 12px; }
    .liquidez-label { font-size: 11px; color: #888; font-weight: bold; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

def termometro_52s(min_val, max_val, atual):
    pos = ((atual - min_val) / (max_val - min_val)) * 100 if max_val != min_val else 50
    pos = max(0, min(100, pos))
    return f"""
    <div style="margin-top: 15px; margin-bottom: 25px; padding: 0 5px;">
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

# --- REQUISIÇÃO ÚNICA DE DADOS ---
@st.cache_data(ttl=600)
def fetch_everything_single_batch():
    try:
        df = yf.download(all_tickers, period="1y", actions=True, group_by='ticker', threads=True)
        return df
    except:
        return None

with st.spinner("Sincronizando mercado..."):
    df_global = fetch_everything_single_batch()

# 5. Sidebar - Calculadora de Rebalanceamento
with st.sidebar:
    st.header("⚖️ Calculadora Inteligente")
    aporte_valor = st.number_input("💸 Novo Aporte (R$):", min_value=0.0, value=1000.0, step=100.0)
    
    st.markdown("**Cotas Atuais (Preencha):**")
    q_spyi = st.number_input("SPYI11", 0)
    q_qqqi = st.number_input("QQQI11", 0)
    q_ethy = st.number_input("ETHY11", 0)
    q_coin = st.number_input("COIN11", 0)
    
    st.markdown("**Alvos Desejados (%):**")
    col1, col2 = st.columns(2)
    a_spyi = col1.number_input("% SPYI", 50)
    a_qqqi = col2.number_input("% QQQI", 30)
    a_ethy = col1.number_input("% ETHY", 10)
    a_coin = col2.number_input("% COIN", 10)
    
    if st.button("🧮 Calcular Onde Aportar"):
        if (a_spyi + a_qqqi + a_ethy + a_coin) != 100:
            st.error("A soma dos alvos deve ser 100%.")
        elif df_global is not None:
            try:
                precos = {
                    'SPYI11': df_global['SPYI11.SA']['Close'].dropna().iloc[-1],
                    'QQQI11': df_global['QQQI11.SA']['Close'].dropna().iloc[-1],
                    'ETHY11': df_global['ETHY11.SA']['Close'].dropna().iloc[-1],
                    'COIN11': df_global['COIN11.SA']['Close'].dropna().iloc[-1]
                }
                
                valores_atuais = {
                    'SPYI11': q_spyi * precos['SPYI11'],
                    'QQQI11': q_qqqi * precos['QQQI11'],
                    'ETHY11': q_ethy * precos['ETHY11'],
                    'COIN11': q_coin * precos['COIN11']
                }
                
                pat_total_atual = sum(valores_atuais.values())
                pat_futuro_alvo = pat_total_atual + aporte_valor
                
                alvos_pct = {'SPYI11': a_spyi/100, 'QQQI11': a_qqqi/100, 'ETHY11': a_ethy/100, 'COIN11': a_coin/100}
                deficits = {at: max(0, (pat_futuro_alvo * alvos_pct[at]) - valores_atuais[at]) for at in alvos_pct}
                soma_deficits = sum(deficits.values())
                
                st.markdown("---")
                st.write("🛒 **Sugestão de Compra:**")
                if soma_deficits > 0:
                    for at, deficit in deficits.items():
                        if deficit > 0:
                            fatia_aporte = aporte_valor * (deficit / soma_deficits)
                            qtd_compra = int(fatia_aporte // precos[at])
                            if qtd_compra > 0:
                                st.success(f"**{at}:** Comprar {qtd_compra} cotas")
                else:
                    st.info("Sua carteira já está equilibrada.")
            except:
                st.error("Erro ao processar dados. Tente atualizar.")

    st.markdown("---")
    if st.button("🚀 Limpar Cache e Forçar Atualização"):
        st.cache_data.clear()
        st.rerun()

# 6. Dashboard Principal
hora_br = (datetime.utcnow() - timedelta(hours=3)).strftime('%H:%M:%S')
st.title("📈 Monitor Buena Vista ETFs")
st.caption(f"Sincronizado BRT: {hora_br} | ⚠️ Delay padrão B3: ~15min")

if df_global is not None and not df_global.empty:
    for cat, ativos in tickers_dict.items():
        st.markdown(f"<div class='section-title'>{cat}</div>", unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, t in enumerate(ativos):
            with cols[idx % 3]:
                with st.container(border=True):
                    try:
                        # Extrai dados e tira preços zerados que o Yahoo manda por engano
                        d_ativo = df_global[t].dropna(subset=['Close'])
                        d_ativo = d_ativo[d_ativo['Close'] > 0]
                        
                        if not d_ativo.empty:
                            p_atual = float(d_ativo['Close'].iloc[-1])
                            p_ant = float(d_ativo['Close'].iloc[-2]) if len(d_ativo) > 1 else p_atual
                            var = ((p_atual - p_ant) / p_ant) * 100
                            
                            # FILTRO SALVA-VIDAS: Ignora dias com mínima igual a 0
                            lows_validos = d_ativo[d_ativo['Low'] > 0]['Low']
                            min_52 = float(lows_validos.min()) if not lows_validos.empty else p_atual
                            max_52 = float(d_ativo['High'].max())
                            
                            divs_pagos = d_ativo[d_ativo['Dividends'] > 0]['Dividends']
                            ultimo_div = float(divs_pagos.iloc[-1]) if not divs_pagos.empty else 0.0
                            yield_m = (ultimo_div / p_atual) * 100 if p_atual > 0 else 0.0
                            
                            # LIQUIDEZ MÉDIA DE 5 DIAS: Resolve o bug do "Volume 0 hoje"
                            vol_medio = d_ativo['Volume'].tail(5).mean()
                            liquidez_fin = p_atual * vol_medio
                            
                            st.markdown(f"<div class='ticker-name'>{t.replace('.SA','')}</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='strategy-box'>{descricoes[t]}</div>", unsafe_allow_html=True)
                            
                            st.metric("Cotação", f"R$ {p_atual:.2f}", f"{var:.2f}%")
                            
                            if ultimo_div > 0:
                                st.markdown(f"""
                                <div class='div-box'>
                                    <span class='div-value'>💰 R$ {ultimo_div:.2f}</span><br>
                                    <span class='div-yield'>Yield Mensal: {yield_m:.2f}%</span>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown(termometro_52s(min_52, max_52, p_atual), unsafe_allow_html=True)
                            
                            st.markdown(f"<div class='liquidez-label'>Liquidez Média (5d): R$ {liquidez_fin:,.2f}</div>".replace(",", "X").replace(".", ",").replace("X", "."), unsafe_allow_html=True)
                            if liquidez_fin < 500000:
                                st.warning("⚠️ Liquidez Restrita: Cuidado em ordens grandes.")
                        else:
                            raise ValueError
                    except Exception as e:
                        st.markdown(f"<div class='ticker-name'>{t.replace('.SA','')}</div>", unsafe_allow_html=True)
                        st.error("Dados indisponíveis no momento.")
else:
    st.error("⚠️ Falha na conexão com o Yahoo Finance.")
