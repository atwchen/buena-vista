import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta

# 1. Configuração da página
st.set_page_config(page_title="Buena Vista | Dash", layout="wide", page_icon="📈")

# 2. Estilização Master (Compacta & Eficiente)
st.markdown("""
    <style>
    .section-title { font-size: 24px; font-weight: 800; color: #ffffff; background-color: #1E88E5; padding: 10px 20px; border-radius: 10px; margin-top: 20px; margin-bottom: 15px; }
    
    /* Layout do Ticker + Alerta em linha */
    .ticker-header { display: flex; align-items: center; gap: 10px; margin-bottom: 5px; }
    .ticker-name { font-size: 26px !important; font-weight: 900; color: #4dabf7; }
    .alavancado-badge { background-color: #ff4b4b; color: white; padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: 900; text-transform: uppercase; }
    
    .strategy-box { font-size: 13px !important; color: #e9ecef !important; background-color: #2b2f33; padding: 10px; border-radius: 8px; border-left: 5px solid #4dabf7; margin-bottom: 10px; min-height: 70px; }
    .div-box { background-color: rgba(64, 192, 87, 0.1); padding: 8px; border-radius: 5px; margin-top: 10px; border-left: 3px solid #40c057;}
    .div-value { color: #40c057; font-size: 14px; font-weight: bold; }
    .div-yield { color: #aaa; font-size: 12px; }
    
    .liquidez-bar { display: flex; justify-content: space-between; align-items: center; margin-top: 15px; margin-bottom: 15px; border-top: 1px solid #444; padding-top: 12px; }
    .liquidez-texto { font-size: 11px; color: #888; font-weight: 600; }
    .badge-low { background-color: rgba(255, 193, 7, 0.1); color: #ffc107; padding: 2px 8px; border-radius: 10px; font-size: 10px; border: 1px solid #ffc107; }
    </style>
    """, unsafe_allow_html=True)

def format_liq(valor):
    if valor >= 1_000_000: return f"R$ {valor/1_000_000:.1f}M"
    if valor >= 1_000: return f"R$ {valor/1_000:.0f}k"
    return f"R$ {valor:.0f}"

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
    "🎯 Renda & Índices": ["SPYI11.SA", "QQQI11.SA", "GDIV11.SA", "IWMI11.SA", "QQQQ11.SA", "XSPI11.SA"],
    "🌐 Cripto ativos": ["COIN11.SA", "ETHY11.SA", "XBCI11.SA", "GBTC11.SA"],
    "🛡️ Proteção & Temáticos": ["AURO11.SA", "PIPE11.SA", "CASA11.SA", "FIXX11.SA", "RICO11.SA"]
}
all_tickers = [t for sub in tickers_dict.values() for t in sub]
alavancados = ["XSPI11.SA", "XBCI11.SA"]

descricoes = {
    "SPYI11.SA": "S&P 500 + Covered Calls para renda mensal.", "QQQI11.SA": "Nasdaq-100 + Venda de opções.",
    "COIN11.SA": "Ecossistema Bitcoin e Blockchain.", "ETHY11.SA": "Ethereum + Estratégia de Renda.",
    "AURO11.SA": "Ouro Físico + Renda Mensal (Seguro de Portfólio).", "GDIV11.SA": "Ações globais sólidas e dividendos.",
    "IWMI11.SA": "Small Caps (Russell 2000) + Opções.", "QQQQ11.SA": "Nasdaq High Beta (Máxima Volatilidade).",
    "PIPE11.SA": "Infraestrutura de Energia (MLPs).", "CASA11.SA": "REITs de qualidade (Imóveis EUA).",
    "FIXX11.SA": "Caixa em Dólar (T-Bills 1-3 meses).", "RICO11.SA": "Copia Grandes Bilionários.",
    "GBTC11.SA": "Ouro Físico + Bitcoin.", "XBCI11.SA": "Bitcoin Potencializado (Yield).",
    "XSPI11.SA": "S&P 500 Potencializado. ⚠️"
}

@st.cache_data(ttl=600)
def fetch_data():
    try: return yf.download(all_tickers, period="1y", actions=True, group_by='ticker', threads=True)
    except: return None

with st.spinner("Sincronizando mercado..."):
    df_global = fetch_data()

# 5. Sidebar - Estratégia "Shield & Grow"
with st.sidebar:
    st.header("⚖️ Estratégia Shield & Grow")
    aporte_valor = st.number_input("💸 Novo Aporte (R$):", min_value=0.0, value=1000.0, step=100.0)
    
    st.markdown("**Cotas Atuais:**")
    q_spyi = st.number_input("SPYI11", 0)
    q_qqqi = st.number_input("QQQI11", 0)
    q_auro = st.number_input("AURO11", 0)
    q_coin = st.number_input("COIN11", 0)
    q_ethy = st.number_input("ETHY11", 0)
    
    st.markdown("**Alvos Alocação (%):**")
    c1, c2 = st.columns(2)
    a_spyi = c1.number_input("% SPYI", 30)
    a_qqqi = c2.number_input("% QQQI", 30)
    a_auro = c1.number_input("% AURO", 20)
    a_coin = c2.number_input("% COIN", 10)
    a_ethy = c1.number_input("% ETHY", 10)
    
    if st.button("🧮 Calcular Onde Aportar", use_container_width=True):
        if (a_spyi + a_qqqi + a_auro + a_coin + a_ethy) != 100:
            st.error("A soma deve ser 100%.")
        elif df_global is not None:
            try:
                precos = {
                    'SPYI11': df_global['SPYI11.SA']['Close'].dropna().iloc[-1],
                    'QQQI11': df_global['QQQI11.SA']['Close'].dropna().iloc[-1],
                    'AURO11': df_global['AURO11.SA']['Close'].dropna().iloc[-1],
                    'COIN11': df_global['COIN11.SA']['Close'].dropna().iloc[-1],
                    'ETHY11': df_global['ETHY11.SA']['Close'].dropna().iloc[-1]
                }
                v_at = {'SPYI11': q_spyi*precos['SPYI11'], 'QQQI11': q_qqqi*precos['QQQI11'], 'AURO11': q_auro*precos['AURO11'], 'COIN11': q_coin*precos['COIN11'], 'ETHY11': q_ethy*precos['ETHY11']}
                pat_fut = sum(v_at.values()) + aporte_valor
                alvos = {'SPYI11': a_spyi/100, 'QQQI11': a_qqqi/100, 'AURO11': a_auro/100, 'COIN11': a_coin/100, 'ETHY11': a_ethy/100}
                deficits = {at: max(0, (pat_fut * alvos[at]) - v_at[at]) for at in alvos}
                soma_def = sum(deficits.values())
                
                st.markdown("---")
                st.write("🛒 **Comprar agora:**")
                for at, defic in deficits.items():
                    if defic > 0 and soma_def > 0:
                        qtd = int((aporte_valor * (defic/soma_def)) // precos[at])
                        if qtd > 0: st.success(f"**{at}:** {qtd} cotas")
            except: st.error("Erro nos dados.")

    if st.button("🚀 Forçar Atualização"):
        st.cache_data.clear()
        st.rerun()

# 6. Painel Principal
hora_br = (datetime.utcnow() - timedelta(hours=3)).strftime('%H:%M:%S')
st.title("📈 Monitor Buena Vista ETFs")
st.caption(f"Sincronizado BRT: {hora_br} | ⚠️ Delay B3: ~15min")

if df_global is not None and not df_global.empty:
    for cat, ativos in tickers_dict.items():
        st.markdown(f"<div class='section-title'>{cat}</div>", unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, t in enumerate(ativos):
            with cols[idx % 3]:
                with st.container(border=True):
                    try:
                        d_at = df_global[t].dropna(subset=['Close'])
                        d_at = d_at[d_at['Close'] > 0]
                        if not d_at.empty:
                            p_at = float(d_at['Close'].iloc[-1])
                            p_ant = float(d_at['Close'].iloc[-2]) if len(d_at) > 1 else p_at
                            var = ((p_at - p_ant) / p_ant) * 100
                            l_v = d_at[d_at['Low'] > 0]['Low']
                            min_52, max_52 = float(l_v.min()), float(d_at['High'].max())
                            d_p = d_at[d_at['Dividends'] > 0]['Dividends']
                            u_d, y_m = (float(d_p.iloc[-1]), (float(d_p.iloc[-1])/p_at)*100) if not d_p.empty else (0.0, 0.0)
                            l_f = p_at * d_at['Volume'].tail(5).mean()
                            
                            # Ticker + Badge Alavancado na mesma linha
                            badge_alavancado = f"<span class='alavancado-badge'>ALAVANCADO</span>" if t in alavancados else ""
                            st.markdown(f"""
                                <div class='ticker-header'>
                                    <span class='ticker-name'>{t.replace('.SA','')}</span>
                                    {badge_alavancado}
                                </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown(f"<div class='strategy-box'>{descricoes[t]}</div>", unsafe_allow_html=True)
                            st.metric("Cotação", f"R$ {p_at:.2f}", f"{var:.2f}%")
                            
                            if u_d > 0:
                                st.markdown(f"<div class='div-box'><span class='div-value'>💰 R$ {u_d:.2f}</span><br><span class='div-yield'>Yield Mensal: {y_m:.2f}%</span></div>", unsafe_allow_html=True)
                            
                            st.markdown(termometro_52s(min_52, max_52, p_at), unsafe_allow_html=True)
                            badge_liq = "<span class='badge-low'>⚠️ Restrita</span>" if l_f < 100000 else ""
                            st.markdown(f"<div class='liquidez-bar'><span class='liquidez-texto'>💧 Liq (5d): {format_liq(l_f)}</span>{badge_liq}</div>", unsafe_allow_html=True)
                        else: raise ValueError
                    except: st.error(f"Erro em {t}")
else: st.error("Falha na conexão.")
