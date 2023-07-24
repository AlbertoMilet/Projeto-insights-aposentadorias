import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go


# Lendo base de dados
@st.cache_data
def carregar_dados():
        df = pd.read_excel('Dados_Previdenciarios.xlsx')
        return df

df = carregar_dados()
with st.container():
    st.title("Dashboard Previdenciário")
    # Criar o filtro com o selectbox para selecionar os estados
    selected_uf = st.multiselect("Selecione um estado", df['UF'].unique())

    # Filtrar os dados pelo estado selecionado
    if selected_uf:
        dados_uf = df[df['UF'].isin(selected_uf)]

        # Obter os municípios únicos do estado selecionado
        municipios_estado = dados_uf['Municipio'][dados_uf['UF'].isin(selected_uf)].unique()

        # Adicionar a opção "Todos os Municípios" à lista de municípios
        municipios_estado = ['Todos os Municípios'] + list(municipios_estado)

        # Criar o filtro com o multiselect para selecionar os municípios do estado selecionado
        selected_municipios = st.multiselect("Selecione os municípios", municipios_estado)

        # Verificar se a opção "Todos os Municípios" foi selecionada e filtrar os dados de acordo
        if 'Todos os Municípios' in selected_municipios:
            dados_uf = dados_uf
        elif selected_municipios:
            dados_uf = dados_uf[dados_uf['Municipio'].isin(selected_municipios)]
    else:
        dados_uf = df

    mapa = go.Figure()

    mapa.add_trace(go.Scattermapbox(
        mode='markers+text',
        lon=dados_uf['LONG'],
        lat=dados_uf['LAT'],
        text=dados_uf['Municipio'],
        marker=dict(
            size=3,
            color='blue',
            opacity=0.8
        ),
        textfont=dict(
            family='sans serif',
            size=12,
            color='black'
        )
    ))

    mapa.update_layout(
        mapbox=dict(
            accesstoken='SEU_TOKEN_DO_MAPBOX',
            center=dict(lon=-50, lat=-15),
            style='open-street-map',
            zoom=3
        ),
        margin=dict(l=0, r=0, t=0, b=0))

    mapa.update_layout(height=250)
    st.plotly_chart(mapa)
    st.write('___')




col1, col2, col3 = st.columns(3)
with st.container():
    with col1:

        st.write("Rural x Urbano")
        df_melted = dados_uf[['Rural', 'Urbano']].melt(var_name='Categoria', value_name='Valor')
        pizza = px.pie(df_melted, values='Valor', names='Categoria')
        pizza.update_layout(height=320)  # Ajustar o tamanho do gráfico de pizza
        pizza.update_layout(legend=dict(orientation='h'))  # Colocar a legenda abaixo do gráfico
        st.plotly_chart(pizza, use_container_width=True)


    with col2:

        st.write("Aposentadorias")
        # Calcula as porcentagens das aposentadorias
        porcentagens = dados_uf[['Aposentadorias por idade', 'Aposentadorias por invalidez',
                                'Aposentadorias por tempo de contribuição', 'Pensões por morte',
                                'Auxílios', 'Outros benefícios previdenciários']].sum()
        total = porcentagens.sum()
        porcentagens = porcentagens / total * 100

        rosca = px.pie(names=porcentagens.index, values=porcentagens, hole=0.6)
        rosca.update_traces(textinfo='percent', textposition='outside', insidetextorientation='radial',
                            textfont_size=10, showlegend=True)
        rosca.update_layout(margin=dict(l=20, r=20, t=20, b=20), legend=dict(orientation='h'))  # Posiciona as legendas abaixo do gráfico
        st.plotly_chart(rosca, use_container_width=True)

    with col3:
            with st.container():
                st.write("Benifício sob população")
                cartao = (dados_uf['Total de Aposentadorias'] / df['População no Município em dezembro de 2022 (*)_x']).mean()
                st.subheader(f"{cartao:.2%}")
                st.write('___')
            with st.container():
                st.write("População")
                cartao2 = dados_uf['População no Município em dezembro de 2022 (*)_x'].sum()

                cartao2 = f'{cartao2:_.2f}'

                cartao2 = cartao2.replace(".", ",").replace("_", ".")
                st.subheader(f"{cartao2}")
                st.write('___')

            with st.container():
                st.write("IDEB")
                if 'Pernambuco' in selected_uf and selected_municipio != 'Todos os Municípios':
                    cartao3 = dados_uf['IDEB_PE'].mean()
                else:
                    cartao3 = dados_uf['IDEB'].mean()

                st.subheader(f"{cartao3:.2f}")
    st.write('___')