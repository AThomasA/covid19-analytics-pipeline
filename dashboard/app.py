import streamlit as st
import pandas as pd
import plotly.express as px 

# Configuração da página
st.set_page_config(page_title="Dashboard COVID-19", layout="wide")

#  Função de carregamento de dados com Cache
@st.cache_data
def load_data():
    # Lê o arquivo que o ETL gerou
    df = pd.read_csv('data/processed/covid_consolidado.csv', parse_dates=['Data'])
    df['Data'] = pd.to_datetime(df['Data'])
    return df

#  Carregar dados
try:
    df = load_data()
except FileNotFoundError:
    st.error("Arquivo  de dados não encontrado. Rode o 'src/etc.py' primeiro!")
    st.stop()

# Sidebar com filtros
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2785/2785819.png", width=50)
st.sidebar.title("Filtros Globais")

# Filtro de Continentes
continentes = sorted(df['Continente'].dropna().unique())
continente_sel = st.sidebar.selectbox("Selecione o Continente:", ["Todos"] + continentes)

if continente_sel != "Todos":
    df_filtered =df[df['Continente'] == continente_sel]
else:
    df_filtered = df
    
# Filtro de País
paises = sorted(df_filtered['País'].unique())
# Brasil como default se estiver na lista
default_idx = paises.index('Brazil') if 'Brazil' in paises else 0
pais_sel = st.sidebar.selectbox("Selecione o País:", paises, index=default_idx)

# Filtrar dataframe final
df_final = df[df['País'] == pais_sel].sort_values('Data')

# Página Principal
st.title(f"Análise COVID19: {pais_sel}")
st.markdown(f"**Continente:** {df_final['Continente'].iloc[0]} | **População:** {int(df_final['População'].iloc[0]):,}")
st.divider()

# Pegando dados mais recentes
ultimo_registro = df_final.iloc[-1]
data_ref = ultimo_registro['Data'].strftime('%d/%m/%Y')

st.header(f"Situação Atual (Ref: {data_ref})")

# KPIs 
col1, col2, col3, col4 = st.columns(4)
col1.metric("Casos Totais", f"{int(ultimo_registro['Casos_Acumulado_dia']):,}")
col2.metric("Mortes Totais", f"{int(ultimo_registro['Mortes_Acumulado_dia']):,}", delta_color="inverse")
col3.metric("Novos Casos (Dia)", f"{int(ultimo_registro['Novos_Casos_dia']):,}")
col4.metric("Letalidade", f"{ultimo_registro['Taxa_Letalidade']:.2f}%")

# Gráficos
st.divider()

# Gráfico 1: Evolução Temporal
st.subheader("Evolução de Casos e Mortes")
tab1, tab2 = st.tabs(["Escala Linear", "Escala Logarítmica"])

with tab1:
    fig = px.line(df_final, x='Data', y=['Casos_Acumulado_dia', 'Mortes_Acumulado_dia'],
                  title=f"Curva de Crescimento - {pais_sel}",
                  labels={'value': 'Quantidade', 'variable': 'Métrica'})
    st.plotly_chart(fig, use_container_width=True)
    
with tab2:
    fig_log = px.line(df_final, x='Data', y=['Casos_Acumulado_dia', 'Mortes_Acumulado_dia'],
                  title=f"Curva de Crescimento (Log) - {pais_sel}",
                  log_y=True)
    st.plotly_chart(fig_log, use_container_width=True)
    
# Gráfico 2: Média Móvel ou Comparativo (Opcional)
st.info("Dica: Use o filtro na barra lateral para explorar outros países.")