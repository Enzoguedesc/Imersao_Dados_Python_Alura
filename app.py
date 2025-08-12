import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
# O layout "wide" permite que os gráficos e tabelas usem toda a largura disponível.
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊", 
    layout="wide",
)

# --- Carregamento dos dados ---
# Lê o arquivo CSV diretamente de um repositório GitHub.
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# --- Barra Lateral (Filtros) ---
# Adiciona um cabeçalho na barra lateral para os filtros.
st.sidebar.header("🔍 Filtros")

# Filtro de Ano
# Obtém os anos únicos do dataframe, ordena-os e cria um filtro de múltipla seleção.
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro de Senioridade
# Obtém as senioridades únicas do dataframe, ordena-as e cria um filtro de múltipla seleção.
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por Tipo de Contrato
# Obtém os tipos de contrato únicos do dataframe, ordena-os e cria um filtro de múltipla seleção.
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtro por Tamanho da Empresa
# Obtém os tamanhos de empresa únicos do dataframe, ordena-os e cria um filtro de múltipla seleção.
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# --- Conteúdo Principal ---
# Título e descrição do dashboard
st.title("🎲 Dashboard de Análise de Salários na Área de Dados") 
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
# Exibe as principais métricas como salário médio, salário máximo, total de registros e cargo mais frequente.
st.subheader("Métricas gerais (Salário anual em USD)")

# Cálculo das métricas
if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""

# Exibição das métricas em colunas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

# --- Análises Visuais com Plotly ---
# Adiciona uma seção para gráficos e cria quatro gráficos diferentes em duas linhas.
st.subheader("Gráficos") #Subtítulo para a seção de gráficos

col_graf1, col_graf2 = st.columns(2) # Cria duas colunas um do lado do outro

# Gráficos que mostra o top 10 cargos por salário médio.
with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index() # Agrupa por cargo, calcula a média salarial, seleciona os 10 maiores e ordena
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        ) # Cria o gráfico de barras horizontais
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'}) # Centraliza o título e ordena o eixo y
        st.plotly_chart(grafico_cargos, use_container_width=True) # Exibe o gráfico na aplicação Streamlit
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")


# Gráfico de histograma mostrando a distribuição dos salários anuais
with col_graf2:
    if not df_filtrado.empty: # Verifica se o dataframe filtrado não está vazio
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

# Gráfico de rosca mostrando a proporção dos tipos de trabalho (remoto, híbrido, presencial)
with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")


# Gráfico de mapa mundi mostrando o salário médio de Data Scientists por país
with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# --- Tabela de Dados Detalhados ---
# Exibe o dataframe filtrado em uma tabela interativa.
st.markdown("---")
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado) # Exibe o dataframe filtrado como uma tabela interativa