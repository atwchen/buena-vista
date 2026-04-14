import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. Configuração da página
st.set_page_config(page_title="Buena Vista | Dash", layout="wide", page_icon="💰")

# 2. Estilização para contraste e leitura
st.markdown("""
    <style>
    .section-title {
        font-size: 28px;
        font-weight: 800;
        color: #ffffff;
        background-color: #1E88E5;
        padding: 10px 20px;
        border-radius: 10px;
        margin-top: 30px;
        margin-bottom: 20px;
    }
    .ticker-name { font-size: 32px !important; font-weight: 900; color: #4dabf7; }
    .strategy-box { 
        font-size: 15px !important; 
        color: #e9ecef !important; 
        background-color: #343a40; 
        padding: 12px; 
        border-radius: 8px;
        border-left: 6px solid #4dabf7;
        margin-bottom: 15px;
        min-height: 90px;
    }
    .alavancado-warning {
        color: #ff4b4b;
        font-weight: 800;
        font-size: 13px;
        display: block;
        margin-top: 8px;
        background-color: rgba(255, 75, 75, 0.1);
        padding: 4px;
        border-radius: 4px;
    }
    .div-label { color: #888; font-size: 14px; margin-top: 10px; }
    .div-value { color: #40c057; font-size: 22px; font-weight: bold; }
    .error-text { color: #ff6b6b; font-size: 18px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. Categorias de Ativos (Descrições Revisadas com Alertas de Alavancagem)
categorias = {
    "🎯 Estratégias High Income (Renda)": {
        "SPYI11.SA": "Ações do S&P 500 unidas à estratégia de venda de opções (Covered Calls) para gerar renda mensal.",
        "QQQI11.SA": "Ações de tecnologia (Nasdaq-100) unidas à venda de opções para maximização de dividendos.",
        "IWMI11.SA": "Exposição às Small Caps americanas (Russell 2000) com estratégia ativa de renda via opções.",
        "GDIV11.SA": "Seleção global de empresas sólidas, boas pagadoras de dividendos e com baixa volatilidade histórica.",
        "XSPI11.SA": "Estratégia agressiva de renda focada no S&P 500.<br><span class='alavancado-warning'>⚠️ ETF ALAVANCADO: Multiplica a exposição e os riscos do índice. Altíssima volatilidade.</span>"
    },
    "🌐 Cripto & Ativos Digitais": {
        "COIN11.SA": "Geração de renda através de empresas ligadas ao ecossistema de criptomoedas e blockchain.",
        "ETHY11.SA": "Exposição ao Ethereum combinada com venda de opções para suavizar quedas e gerar dividendos.",
        "XBCI11.SA": "Exposição potencializada ao Bitcoin visando máxima distribuição de caixa.<br><span class='alavancado-warning'>⚠️ ETF ALAVANCADO: Riscos multiplicados. Focado em curtíssimo prazo ou posições táticas.</span>",
        "GBTC11.SA": "Portfólio de proteção que mescla a reserva de valor milenar (Ouro) com o Ouro Digital (Bitcoin)."
    },
    "🛡️ Proteção, Caixa e Temáticos": {
        "FIXX11.SA": "Proteção de caixa em Dólar: Investe em Títulos Curtos do Tesouro Americano (T-Bills de 1-3 meses).",
        "AURO11.SA": "Exposição física ao Ouro aliada à estratégia de opções para transformar um ativo estático em gerador de renda.",
        "CASA11.SA": "Renda dolarizada proveniente do setor imobiliário americano através de REITs de qualidade.",
        "PIPE11.SA": "Altos dividendos gerados pelo setor de infraestrutura de energia e oleodutos nos EUA (MLPs).",
        "RICO11.SA": "Fundo temático que replica as principais posições acionárias dos maiores investidores institucionais (Bilionários)."
    }
}

# 4. Função de busca robusta (Agora com Yield Mensal)
@st.cache_data(ttl=60) # Cache reduzido para 60 segundos para casar com o Auto-Refresh
def buscar_dados(ticker_name):
    try:
        tk = yf.Ticker(ticker_name)
        
        # Puxamos os últimos 5 dias para cálculo seguro de preço e fechamento anterior
        hist = tk.history(period="5d")
        
        if hist.empty:
            raise ValueError("Histórico vazio retornado pelo Yahoo Finance")
            
        # Extração segura dos preços
        preco = float(hist['Close'].iloc[-1])
        
        # Pega o penúltimo fechamento
        if len(hist) > 1:
            prev_close = float(hist['Close'].iloc[-2])
        else:
            prev_close = preco
            
        var = float(((preco - prev_close) / prev_close) * 100) if prev_close > 0 else 0.0
        volume = float(hist['Volume'].iloc[-1])
        
        # Busca rápida intradiária só para pegar os minutos da última negociação
        hist_intra = tk.history(period="1d", interval="1m")
        if not hist_intra.empty:
            horario_mercado = hist_intra.index[-1].strftime("%d/%m %H:%M")
        else:
            horario_mercado = hist.index[-1].strftime("%d/%m")
            
        # Tratamento para Máximas e Mínimas
        try:
            info = tk.info
            max_52s = float(info.get('fiftyTwoWeekHigh', 0.0))
            min_52s = float(info.get('fiftyTwoWeekLow', 0.0))
        except:
            max_52s = 0.0
            min_52s = 0.0
            
        # Tratamento de Dividendos (Foco no YIELD MENSAL)
        divs = tk.dividends
        ultimo_valor_div = 0.0
        yield_mensal = 0.0
        
        if not divs.empty:
            ultimo_valor_div = float(divs.iloc[-1])
            # Cálculo simples: último provento dividido pela cotação atual
            yield_mensal = float((ultimo_valor_div / preco) * 100) if preco > 0 else 0.0
            
        return {
            "preco": preco, 
            "variacao": var, 
            "div": ultimo_valor_div, 
            "yield_mensal": yield_mensal, 
            "horario": horario_mercado,
            "volume": volume,
            "max_52s": max_52s,
            "min_52s": min_52s,
            "erro": False
        }
    except Exception as e:
        print(f"Erro ao buscar {ticker_name}: {e}")
        return {"preco": 0.0, "variacao": 0.0, "div": 0.0, "yield_mensal": 0.0, "horario": "", "volume": 0.0, "max_52s": 0.0, "min_52s": 0.0, "erro": True}

# 5. Layout do Topo com controles de atualização
col_titulo, col_botoes = st.columns([0.7, 0.3])

with col_titulo:
    st.title("📈 Monitor Buena Vista ETFs")

with col_botoes:
    st.write("") 
    # Toggle para atualização automática (novo)
    auto_refresh = st.toggle("🔄 Atualização Automática (60s)", value=False)
    # Botão manual mantido para quem não quer ligar o automático
    if st.button("Atualizar Agora", use_container_width=True):
        st.cache_data.clear() 
        st.rerun()

# 6. Construção da Interface
for nome_cat, ativos in categorias.items():
    st.markdown(f"<div class='section-title'>{nome_cat}</div>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for idx, (ticker, objetivo) in enumerate(ativos.items()):
        with cols[idx % 3]:
            dados = buscar_dados(ticker)
            with st.container(border=True):
                st.markdown(f"<div class='ticker-name'>{ticker.replace('.SA', '')}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='strategy-box'>{objetivo}</div>", unsafe_allow_html=True)
                
                if dados["erro"]:
                    st.markdown("<div class='error-text'>⚠️ Dados Indisponíveis no momento</div>", unsafe_allow_html=True)
                    st.caption("Verifique o ticker ou atualize as cotações.")
                else:
                    # Cotação Principal
                    st.metric("Cotação Atual", f"R$ {dados['preco']:.2f}", f"{dados['variacao']:.2f}%")
                    st.caption(f"🕒 Mercado: **{dados['horario']}**")
                    
                    # Proventos (Atualizado para Yield Mensal)
                    if dados['div'] > 0:
                        st.markdown("<div class='div-label'>Último Provento Pago</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='div-value'>R$ {dados['div']:.2f} <small style='font-size:13px; color:#aaa'>(Yield Mensal: {dados['yield_mensal']:.2f}%)</small></div>", unsafe_allow_html=True)
                    else:
                        st.caption("Sem dividendos listados recentemente.")
                    
                    # Expander de Detalhes
                    with st.expander("📊 Ver mais detalhes"):
                        st.write(f"**Mínima (52 sem):** R$ {dados['min_52s']:.2f}")
                        st.write(f"**Máxima (52 sem):** R$ {dados['max_52s']:.2f}")
                        st.write(f"**Volume Diário:** {dados['volume']:,.0f}".replace(",", "."))

# 7. Rodapé
st.markdown("---")
st.caption("Atualizado via Yahoo Finance. Os dados de dividendos refletem o último pagamento registrado na B3 e o Yield Mensal sobre a cotação atual.")

# 8. Lógica de Atualização Automática no fim do script
if auto_refresh:
    time.sleep(60) # Aguarda 60 segundos
    st.cache_data.clear() # Limpa o cache antigo
    st.rerun() # Recarrega a página inteira