import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard de Validação XML", page_icon="📄", layout="wide")

# --- CSS PARA DEIXAR OS NÚMEROS E TÍTULOS MAIORES ---
st.markdown("""
<style>
h1 {font-size: 48px !important;}
h2 {font-size: 36px !important;}
h3 {font-size: 28px !important;}
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
URL_REGRAS_XML = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQXjBJDTJKEqmfsJ7--1yKYu4GS_HGjSL6oYqmxvBQAuq531vP9Tn8aAtslzfcv7-nBI2etu-66UFg1/pub?gid=1940409074&single=true&output=csv"
URL_DIVERGENCIAS_XML = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQXjBJDTJKEqmfsJ7--1yKYu4GS_HGjSL6oYqmxvBQAuq531vP9Tn8aAtslzfcv7-nBI2etu-66UFg1/pub?gid=783374226&single=true&output=csv"
URL_RESUMO_XML = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQXjBJDTJKEqmfsJ7--1yKYu4GS_HGjSL6oYqmxvBQAuq531vP9Tn8aAtslzfcv7-nBI2etu-66UFg1/pub?gid=2111793638&single=true&output=csv"

@st.cache_data(show_spinner=False)
def carregar_dados_url(url):
    if not url: return None
    try:
        df = pd.read_csv(url)
        if df.empty: return None
        return df
    except Exception:
        return None

# Carrega os quatro DataFrames
df_base = carregar_dados_url(URL_BASE)
df_regras_xml = carregar_dados_url(URL_REGRAS_XML)
df_divergencias_xml = carregar_dados_url(URL_DIVERGENCIAS_XML)
df_resumo_xml = carregar_dados_url(URL_RESUMO_XML)

st.title("📄 Dashboard de Validação XML")
st.markdown("---")

dados_essenciais_carregados = df_base is not None and df_regras_xml is not None and df_resumo_xml is not None

if not dados_essenciais_carregados:
    st.error("Falha ao carregar os dados essenciais (Base, Regras XML ou Resumo XML). Verifique os links e permissões.")
else:
    # --- SEÇÃO DE COBERTURA DE TESTES ---
    st.header("Cobertura de Testes das Regras XML")

    col_regra = "Regra XML"
    col_itens = "Itens Conferidos"
    col_sucesso = "Sucesso"
    col_erro = "Erro"

    total_regras_catalogo = len(df_resumo_xml)
    total_itens_conferidos = df_resumo_xml[col_itens].sum()
    total_sucesso = df_resumo_xml[col_sucesso].sum()
    total_erro = df_resumo_xml[col_erro].sum()

    taxa_de_sucesso = (total_sucesso / total_itens_conferidos) if total_itens_conferidos > 0 else 0
    taxa_de_erro = (total_erro / total_itens_conferidos) if total_itens_conferidos > 0 else 0

    total_cenarios_avaliados = len(df_regras_xml)

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
                'Sucesso': '#27ae60',  # verde
                'Erro': '#e74c3c'      # vermelho mais forte
            }
        )
        fig_pizza.update_traces(outsidetextfont_size=25, textfont_size=25)
        fig_pizza.update_layout(legend_font_size=28)
        st.plotly_chart(fig_pizza, use_container_width=True)

    with col2:
        st.subheader("Resumo do Catálogo de Regras XML")
        # Layout dos KPIs conforme o primeiro print: 2 linhas, 2 azuis à esquerda, 2 azuis à direita, 2 vermelhos à direita, percentual centralizado abaixo
        kpi_row1 = st.columns([1,1,1])
        with kpi_row1[0]:
            st.markdown(f'<div class="custom-metric"><div class="custom-metric-value" style="color: #27ae60;">{total_regras_catalogo}</div><div class="custom-metric-label">Quantidade de regras avaliadas</div></div>', unsafe_allow_html=True)
        with kpi_row1[1]:
            st.markdown(f'<div class="custom-metric"><div class="custom-metric-value" style="color: #27ae60;">{total_itens_conferidos}</div><div class="custom-metric-label">Total de conferências realizadas</div></div>', unsafe_allow_html=True)
        with kpi_row1[2]:
            st.markdown(f'<div class="custom-metric"><div class="custom-metric-value" style="color: #e74c3c;">{taxa_de_erro:.2%}</div><div class="custom-metric-label">Conferências com erro</div></div>', unsafe_allow_html=True)

        kpi_row2 = st.columns([1,1,1])
        with kpi_row2[0]:
            st.markdown(f'<div class="custom-metric"><div class="custom-metric-value" style="color: #27ae60;">{total_cenarios_avaliados}</div><div class="custom-metric-label">Total de cenários avaliados</div></div>', unsafe_allow_html=True)
        with kpi_row2[1]:
            st.markdown(f'<div class="custom-metric"><div class="custom-metric-value" style="color: #27ae60;">{total_sucesso}</div><div class="custom-metric-label">Conferências sem erro</div></div>', unsafe_allow_html=True)
        with kpi_row2[2]:
            st.markdown(f'<div class="custom-metric"><div class="custom-metric-value" style="color: #e74c3c;">{total_erro}</div><div class="custom-metric-label">Conferências com erro</div></div>', unsafe_allow_html=True)

        # Percentual centralizado abaixo dos KPIs, mas dentro do mesmo bloco de coluna para alinhamento
        st.markdown(f'<div class="custom-metric" style="text-align:center; margin-top: 5px;"><div class="custom-metric-value" style="color: #27ae60;">{taxa_de_sucesso:.2%}</div><div class="custom-metric-label">Percentual de conferências sem erro</div></div>', unsafe_allow_html=True)
    # Linha do progress bar removida conforme solicitado
    st.markdown("---")

    # --- SEÇÃO DE ANÁLISE DAS DIVERGÊNCIAS ---
    st.header("Análise das Divergências Encontradas no XML")

    if df_divergencias_xml is None or df_divergencias_xml.empty:
        st.success("🎉 Nenhuma divergência encontrada na amostra de dados!")
    else:
        col_chave = df_divergencias_xml.columns[0]
        col_produto = df_divergencias_xml.columns[1]
        col_campo = df_divergencias_xml.columns[2]
        col_valor_xml = df_divergencias_xml.columns[3]
        col_valor_planilha = df_divergencias_xml.columns[4]
        col_obs = df_divergencias_xml.columns[5]

        nfs_com_erro = df_divergencias_xml[[col_chave, col_produto]].drop_duplicates().shape[0]
        df_divergencias_xml['ID_Regra'] = df_divergencias_xml[col_campo].astype(str).str.split(' - ').str[0:2].str.join(' - ')

        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        with col_kpi1:
            st.markdown(f'<div class="custom-metric"><div class="custom-metric-value" style="color: #27ae60;">{len(df_base.drop_duplicates())}</div><div class="custom-metric-label">NFs na Amostra</div></div>', unsafe_allow_html=True)
        with col_kpi2:
            st.markdown(f'<div class="custom-metric"><div class="custom-metric-value" style="color: #e74c3c;">{nfs_com_erro}</div><div class="custom-metric-label">NFs com Divergência</div></div>', unsafe_allow_html=True)
        with col_kpi3:
            st.markdown(f'<div class="custom-metric"><div class="custom-metric-value" style="color: #e74c3c;">{len(df_divergencias_xml)}</div><div class="custom-metric-label">Regras com Divergência</div></div>', unsafe_allow_html=True)

        with st.expander("Clique aqui para ver o detalhamento dos erros"):
            st.markdown('<div class="custom-metric-value" style="margin-bottom: 10px;">Clique aqui para ver o detalhamento dos erros</div>', unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("##### Top Regras-Mãe com Mais Falhas")
                regras_mais_frequentes = df_divergencias_xml['ID_Regra'].value_counts().head(10)
                df_regras_chart = pd.DataFrame({'ID_Regra': regras_mais_frequentes.index, 'Contagem': regras_mais_frequentes.values})
                fig_regras = px.bar(df_regras_chart.sort_values(by='Contagem', ascending=True), 
                                    x='Contagem', y='ID_Regra', orientation='h', text='Contagem')
                fig_regras.update_layout(showlegend=False, yaxis_title='', xaxis_title='Quantidade de Divergências')
                st.plotly_chart(fig_regras, use_container_width=True)
            with col_b:
                st.markdown("##### Proporção de Divergências por Produto")
                divergencias_por_produto = df_divergencias_xml[col_produto].value_counts()
                df_produto_chart = pd.DataFrame({'Produto': divergencias_por_produto.index, 'Quantidade': divergencias_por_produto.values})
                fig_donut = px.pie(df_produto_chart, values='Quantidade', names='Produto', hole=.4)
                st.plotly_chart(fig_donut, use_container_width=True)
