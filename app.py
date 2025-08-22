import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard de Validação Fiscal", page_icon="📊", layout="wide")

# --- CSS PARA DEIXAR OS NÚMEROS E TÍTULOS MAIORES ---
st.markdown("""
<style>
/* Estilos gerais de Títulos */
h1 {font-size: 48px !important;}
h2 {font-size: 36px !important;}
h3 {font-size: 28px !important;}

/* Nosso novo componente de "Big Number" customizado */
.custom-metric {
    text-align: center;
    padding: 10px 0;
}
.custom-metric-value {
    font-size: 60px !important;
    font-weight: bold;
    line-height: 1;
}
.custom-metric-label {
    font-size: 30px !important;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)




# --- URLs DOS DADOS ---
URL_BASE = "https://docs.google.com/spreadsheets/d/1j_gp1Wviqi2XtsqXmN6LM9v6NUg1CfuwuFPNBwIBNzs/export?format=csv&gid=0"
URL_REGRAS = "https://docs.google.com/spreadsheets/d/1j_gp1Wviqi2XtsqXmN6LM9v6NUg1CfuwuFPNBwIBNzs/export?format=csv&gid=811132636"
URL_DIVERGENCIAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQXjBJDTJKEqmfsJ7--1yKYu4GS_HGjSL6oYqmxvBQAuq531vP9Tn8aAtslzfcv7-nBI2etu-66UFg1/pub?gid=89787833&single=true&output=csv"
URL_RESUMO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQXjBJDTJKEqmfsJ7--1yKYu4GS_HGjSL6oYqmxvBQAuq531vP9Tn8aAtslzfcv7-nBI2etu-66UFg1/pub?gid=1794490689&single=true&output=csv"

@st.cache_data(show_spinner=False)
def carregar_dados_url(url):
    """Carrega dados de uma URL CSV."""
    if not url: return None
    try:
        df = pd.read_csv(url)
        if df.empty: return None
        return df
    except Exception:
        return None

# Carrega os quatro DataFrames
df_base = carregar_dados_url(URL_BASE)
df_regras = carregar_dados_url(URL_REGRAS)
df_divergencias = carregar_dados_url(URL_DIVERGENCIAS)
df_resumo = carregar_dados_url(URL_RESUMO)

# Título principal sempre aparece
st.title("📊 Dashboard de Validação de NFs")
st.markdown("---")

dados_essenciais_carregados = df_base is not None and df_regras is not None and df_resumo is not None

if not dados_essenciais_carregados:
    st.error("Falha ao carregar os dados essenciais (Base, Regras ou Resumo). Verifique os links e permissões.")
else:
    # --- SEÇÃO DE COBERTURA DE TESTES (NOVA SEÇÃO PRINCIPAL) ---
    st.header("Cobertura de Testes das Regras")

    # Nomes das colunas do arquivo resumo
    col_regra = "Regra"
    col_notas = "Notas Conferidas"
    col_sucesso = "Sucesso"
    col_erro = "Erro"

    # --- LÓGICA DE CÁLCULO ---
    total_regras_catalogo = len(df_resumo)
    total_notas_conferidas = df_resumo[col_notas].sum()
    total_sucesso = df_resumo[col_sucesso].sum()
    total_erro = df_resumo[col_erro].sum()

    taxa_de_sucesso = (total_sucesso / total_notas_conferidas) if total_notas_conferidas > 0 else 0
    taxa_de_erro = (total_erro / total_notas_conferidas) if total_notas_conferidas > 0 else 0

    # NOVO KPI: Total de cenários avaliados = número de linhas da aba regras
    total_cenarios_avaliados = len(df_regras)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Percentual de Sucesso e Erro")
        # Força os valores para garantir o mapeamento correto das cores
        df_cobertura = pd.DataFrame({
            'Status': ['Sucesso', 'Erro'],
            'Quantidade': [total_sucesso, total_erro]
        })
        df_cobertura['Status'] = df_cobertura['Status'].astype(str).str.strip()
        fig_pizza = px.pie(
            df_cobertura,
            values='Quantidade',
            names='Status',
            hole=.3,
            color='Status',
            color_discrete_map={
                'Sucesso': '#3498db',  # azul
                'Erro': '#FF6F61'      # vermelho
            }
        )
        fig_pizza.update_traces(outsidetextfont_size=32, textfont_size=32)
        fig_pizza.update_layout(legend_font_size=28)
        st.plotly_chart(fig_pizza, use_container_width=True)

    with col2:
        st.subheader("Resumo do Catálogo de Regras")
        # Layout dos KPIs conforme o modelo do print: 2 linhas, 2 azuis à esquerda, 2 azuis à direita, 2 vermelhos à direita, percentual centralizado abaixo
        kpi_row1 = st.columns([1,1,1])
        with kpi_row1[0]:
            st.markdown(f'<div class="custom-metric"><div class="custom-metric-value" style="color: #3498db;">{total_regras_catalogo}</div><div class="custom-metric-label">Quantidade de regras avaliadas</div></div>', unsafe_allow_html=True)
        with kpi_row1[1]:
            st.markdown(f'<div class="custom-metric"><div class="custom-metric-value" style="color: #3498db;">{total_notas_conferidas}</div><div class="custom-metric-label">Total de conferências realizadas</div></div>', unsafe_allow_html=True)
        with kpi_row1[2]:
            st.markdown(f'<div class="custom-metric"><div class="custom-metric-value" style="color: #FF6F61;">{taxa_de_erro:.2%}</div><div class="custom-metric-label">Conferências com erro</div></div>', unsafe_allow_html=True)

        kpi_row2 = st.columns([1,1,1])
        with kpi_row2[0]:
            st.markdown(f'<div class="custom-metric"><div class="custom-metric-value" style="color: #3498db;">{total_cenarios_avaliados}</div><div class="custom-metric-label">Total de cenários avaliados</div></div>', unsafe_allow_html=True)
        with kpi_row2[1]:
            st.markdown(f'<div class="custom-metric"><div class="custom-metric-value" style="color: #3498db;">{total_sucesso}</div><div class="custom-metric-label">Conferências sem erro</div></div>', unsafe_allow_html=True)
        with kpi_row2[2]:
            st.markdown(f'<div class="custom-metric"><div class="custom-metric-value" style="color: #FF6F61;">{total_erro}</div><div class="custom-metric-label">Conferências com erro</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="custom-metric" style="text-align:center;"><div class="custom-metric-value" style="color: #3498db;">{taxa_de_sucesso:.2%}</div><div class="custom-metric-label">Percentual de conferências sem erro</div></div>', unsafe_allow_html=True)
    st.markdown("---")

# --- SEÇÃO DE ANÁLISE DAS DIVERGÊNCIAS ---
    st.header("Análise das Divergências Encontradas")

    if df_divergencias is None or df_divergencias.empty:
        st.success("🎉 Nenhuma divergência encontrada na amostra de dados!")
    else:
        # Pega os nomes das colunas de forma segura
        col_cod_filial = df_divergencias.columns[0]
        col_numnota = df_divergencias.columns[3]
        col_serie = df_divergencias.columns[4]
        col_regra_aplicada = df_divergencias.columns[10]
        col_estado = df_divergencias.columns[1]

        nfs_com_erro = df_divergencias[[col_cod_filial, col_numnota, col_serie]].drop_duplicates().shape[0]
        df_divergencias['ID_Regra'] = df_divergencias[col_regra_aplicada].astype(str).str.split(' - ').str[0:2].str.join(' - ').str.replace('Regra: ', '')

        # --- ALTERAÇÃO APLICADA AQUI ---
        # Substituindo st.metric por st.markdown com o estilo customizado
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        with col_kpi1:
            st.markdown(f'<div class="custom-metric"><div class="custom-metric-value" style="color: #3498db;">{len(df_base.drop_duplicates())}</div><div class="custom-metric-label">NFs na Amostra</div></div>', unsafe_allow_html=True)
        with col_kpi2:
            st.markdown(f'<div class="custom-metric"><div class="custom-metric-value" style="color: #FF6F61;">{nfs_com_erro}</div><div class="custom-metric-label">NFs com Divergência</div></div>', unsafe_allow_html=True)
        with col_kpi3:
            st.markdown(f'<div class="custom-metric"><div class="custom-metric-value" style="color: #FF6F61;">{len(df_divergencias)}</div><div class="custom-metric-label">Regras com Divergência</div></div>', unsafe_allow_html=True)
        # --- FIM DA ALTERAÇÃO ---

        with st.expander("Clique aqui para ver o detalhamento dos erros"):
            st.markdown('<div class="custom-metric-value" style="margin-bottom: 10px;">Clique aqui para ver o detalhamento dos erros</div>', unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("##### Top Regras-Mãe com Mais Falhas")
                regras_mais_frequentes = df_divergencias['ID_Regra'].value_counts().head(10)
                df_regras_chart = pd.DataFrame({'ID_Regra': regras_mais_frequentes.index, 'Contagem': regras_mais_frequentes.values})
                fig_regras = px.bar(df_regras_chart.sort_values(by='Contagem', ascending=True), 
                                    x='Contagem', y='ID_Regra', orientation='h', text='Contagem')
                fig_regras.update_layout(showlegend=False, yaxis_title='', xaxis_title='Quantidade de Divergências')
                st.plotly_chart(fig_regras, use_container_width=True)
            with col_b:
                st.markdown("##### Proporção de Divergências por Estado")
                divergencias_por_estado = df_divergencias[col_estado].value_counts()
                df_estado_chart = pd.DataFrame({'Estado': divergencias_por_estado.index, 'Quantidade': divergencias_por_estado.values})
                fig_donut = px.pie(df_estado_chart, values='Quantidade', names='Estado', hole=.3)
                st.plotly_chart(fig_donut, use_container_width=True)