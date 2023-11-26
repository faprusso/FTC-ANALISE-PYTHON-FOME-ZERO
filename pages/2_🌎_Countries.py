# Libraries
import pandas as pd
import folium
import plotly_express as px
import inflection
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image
import altair as alt

st.set_page_config(page_title='Visão Países', page_icon='🌎', layout='wide')

# ---------------------------
# Funções
# ---------------------------
def rename_columns(dataframe):
    df1 = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df1.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df1.columns = cols_new
    return df1
# Preenchimento do nome dos países
def country_name(country_id):
    return countries[country_id]

# renomear o nome das cores
def color_name(color_code):
    return colors[color_code]

# Criando o tipo de categoria de comida
def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

# função que traz o agrupamento de Países em função do parâmetro recebido
def overall_metrics(country_or_city, calculate_column, op, asc):
   if op == 'nunique':
      groupby_sorting = ( df1.loc[:, [country_or_city, calculate_column ]]
                        .groupby(country_or_city)
                        .nunique()
                        .sort_values(calculate_column, ascending=asc)
                        .reset_index()
                        )
      return groupby_sorting
   elif op == 'sum':
      groupby_sorting = ( df1.loc[:, [country_or_city, calculate_column ]]
                        .groupby(country_or_city)
                        .sum()
                        .sort_values(calculate_column, ascending=asc)
                        .reset_index()
                        )
      return groupby_sorting
   elif op == 'mean':
      groupby_sorting = ( df1.loc[:, [country_or_city, calculate_column ]]
                        .groupby(country_or_city)
                        .mean()
                        .sort_values(calculate_column, ascending=asc)
                        .reset_index()
                        )
      return groupby_sorting

# função para automatizar a criação de label para os gráficos do altair
def label_text(fig, column):
       text =  fig.mark_text(
            align='center',
            baseline='middle',
            fontSize=13,
            fontWeight=600,
            opacity=0.7,
            color='#424256',
            text='foo-baz',
            dy=-6).encode(
                text=f'{column}:Q')
       return text

# ---------------------------
# Dicionários
# ---------------------------
# Nome dos países
countries = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",
}

#Nome das cores
colors = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
"FFBA00": "red",
"CBCBC8": "darkred",
"FF7800": "darkred",
}

# --------------------------- Início da estrutura lógica do código ---------------------------

# ---------------------------
# Import Dataset
# ---------------------------
df = pd.read_csv('zomato.csv')
df1 = df.copy()

# ---------------------------
# Limpando dados
# ---------------------------

# Retirando as 15 linhas com NaN
df1 = df1.dropna()
# Retirando as linhas com informação duplicada
df1 = df1.drop_duplicates()

# Transformando os tipos de Cuisine em apenas 1 elemento
df1.loc[df1['Cuisines'].notnull(), 'Cuisines'] = df1.loc[df1['Cuisines'].notnull(), 'Cuisines'].apply( lambda x: x.split(",")[0])

# Tirando as letas maiúsculas e espaços dos títulos das colunas e adicionando o underline
df1 = rename_columns(df1)

# Criando a coluna country_name pela função country_name
df1['country_name'] = df1['country_code'].apply( lambda x: country_name(x))

# Criando a coluna cor pelo código da cor na coluna 'rating_color'
df1['color_name'] = df1['rating_color'].apply( lambda x: color_name(x))

# Criando o tipo de categoria de comida pela coluna 'price_range'
df1['rating_text'] = df1['price_range'].apply( lambda x: create_price_tye(x))

# =====================================
# Barra Lateral
# =====================================
st.sidebar.markdown("""---""")
# Logo Fome Zero na barra lateral
image_path = 'food_delivery.png'
image = Image.open(image_path)

# st.sidebar.image(image, width=150)
st.sidebar.markdown('## Fome Zero')
st.sidebar.markdown('### Filtros')

# criando a lista de países
country_names = list(df1['country_name'].unique())

# select de países
country_select = st.sidebar.multiselect(
    'Escolha quais países deseja visualizar os dados dos restaurantes',
    country_names,
    default = country_names)

# Aplicação dos filtros
linhas_selecionadas = df1['country_name'].isin(country_select)
df1 = df1.loc[linhas_selecionadas, :]

# =====================================
# Layout no Streamlit
# =====================================
st.header('🌎 Visão Países')

with st.container():
    country_with_more_restaurants = overall_metrics('country_name', 'restaurant_id', 'nunique', False)
    st.markdown('<h5 style= "text-align: center">Quantidade de restaurantes registrados por país</h5>', unsafe_allow_html=True)

    # Gráfico com Biblioteca Altair
    # fig = (
    #     alt.Chart(country_with_more_restaurants)
    #     .mark_bar()
    #     .encode(
    #         alt.X('country_name', title='Países', sort = alt.EncodingSortField(field='restaurant_id', order='descending')),
    #         alt.Y('restaurant_id', title='Quantidade de Restaurantes')
    #     )
    # )

    # st.altair_chart(fig + label_text(fig, 'restaurant_id'), use_container_width=True)

    # Gráfico com Biblioteca Plotly
    fig = px.bar(
        country_with_more_restaurants,
        x='country_name',
        y='restaurant_id',
        text_auto='.0f',
        labels={
            'country_name': 'Países',
            'restaurant_id': 'Quantidade de Restaurantes'
        }
    )
    st.plotly_chart(fig, use_container_width=True, theme=None)

with st.container():
    country_with_more_cities = overall_metrics('country_name', 'city', 'nunique', False)
    st.markdown('<h5 style= "text-align: center">Quantidade de cidades registrados por país</h5>', unsafe_allow_html=True)

    # Gráfico com Biblioteca Altair
    # fig = (
    #     alt.Chart(country_with_more_cities)
    #     .mark_bar()
    #     .encode(
    #         alt.X('country_name', title='Países', sort = alt.EncodingSortField(field= 'city', order='descending')), 
    #         alt.Y('city', title='Quantidade de Cidades')
    #         )
    # )
    # st.altair_chart(fig + label_text(fig, 'city'),use_container_width=True)

    # Gráfico com Biblioteca Plotly
    fig = px.bar(
        country_with_more_cities,
        x='country_name',
        y='city',
        text_auto='.0f',
        labels={
            'country_name': 'Países',
            'city': 'Quantidade de Cidades'
        }
    )
    st.plotly_chart(fig, use_container_width=True, theme=None)

with st.container():
    country_dif_cuisines = overall_metrics('country_name', 'cuisines', 'nunique', False)
    st.markdown('<h5 style= "text-align: center">Tipos de culinária por país</h5>', unsafe_allow_html=True)

    # Gráfico com Biblioteca Altair
    # fig = (
    #     alt.Chart(country_dif_cuisines)
    #     .mark_bar()
    #     .encode(
    #         alt.X('country_name', title='Países', sort = alt.EncodingSortField(field= 'cuisines', order='descending')), 
    #         alt.Y('cuisines', title='Quantidade de Culinárias')
    #         )
    # )
    # st.altair_chart(fig + label_text(fig, 'cuisines'),use_container_width=True)

    # Gráfico com Biblioteca Plotly
    fig = px.bar(
        country_dif_cuisines,
        x='country_name',
        y='cuisines',
        text_auto='.0f',
        labels={
            'country_name': 'Países',
            'cuisines': 'Quantidade de Culinárias'
        }
    )
    st.plotly_chart(fig, use_container_width=True, theme=None)

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        country_with_more_ratings = round((df1.loc[df1['votes'] != 0, ['votes', 'country_name']]
                                     .groupby('country_name')
                                     .mean()
                                     .sort_values('votes', ascending=False)
                                     .reset_index()
                                     ),0)

        st.markdown('<h5 style= "text-align: center">Quantidade de avaliações médias por país</h5>', unsafe_allow_html=True)

        # Gráfico com Biblioteca Altair
        # fig = (
        #     alt.Chart(country_with_more_ratings)
        #     .mark_bar()
        #     .encode(
        #         alt.X('country_name', title='Países', sort = alt.EncodingSortField(field= 'votes', order= 'descending')),
        #         alt.Y('votes', title='Quantidade de Avaliações')
        #     )
        # )
        # st.altair_chart(fig + label_text(fig, 'votes'), use_container_width=True)

        # Gráfico com Biblioteca Plotly
        fig = px.bar(
            country_with_more_ratings,
            x='country_name',
            y='votes',
            text_auto='.0f',
            labels={
                'country_name': 'Países',
                'votes': 'Quantidade de Avaliações'
            }
        )
        st.plotly_chart(fig, use_container_width=True, theme=None)
    with col2:
        country_avg_rating = round(overall_metrics('country_name', 'aggregate_rating', 'mean', False),2)
        st.markdown('<h5 style= "text-align: center">Nota média dos restaurantes por país</h5>', unsafe_allow_html=True)

        # Gráfico com Biblioteca Altair
        # fig = (
        #     alt.Chart(country_avg_rating)
        #     .mark_bar()
        #     .encode(
        #         alt.X('country_name', title='Países', sort = alt.EncodingSortField(field= 'aggregate_rating', order= 'descending')),
        #         alt.Y('aggregate_rating', title='Nota Média')
        #     )
        # )
        # st.altair_chart(fig + label_text(fig, 'aggregate_rating'), use_container_width=True)

        # Gráfico com Biblioteca Plotly
        fig = px.bar(
            country_avg_rating,
            x='country_name',
            y='aggregate_rating',
            text_auto='.1f',
            labels={
                'country_name': 'Países',
                'aggregate_rating': 'Nota Média'
            }
        )
        st.plotly_chart(fig, use_container_width=True, theme=None)
with st.container():
    # country_avg_cost_for_two = round(overall_metrics('country_name', 'average_cost_for_two', 'mean', False),2)
    st.markdown('<h5 style= "text-align: center">Preço médio de um prato por país</h5>', unsafe_allow_html=True)

    country_avg_cost_for_two = (df1.loc[:, [ 'country_name', 'average_cost_for_two', 'currency']]
                                  .groupby(['country_name', 'currency'])
                                  .mean()
                                  .sort_values('average_cost_for_two', ascending=False)
                                  .reset_index()
                                  )


    # Gráfico com Biblioteca Altair
    # fig = (
    #     alt.Chart(country_avg_cost_for_two)
    #     .mark_bar()
    #     .encode(
    #         alt.X('country_name', title='Países', sort = '-y'),
    #         alt.Y('average_cost_for_two', title='Preço para duas pessoas')
    #         )
    #     )
    # st.altair_chart(fig + label_text(fig, 'average_cost_for_two'), use_container_width=True)

    # Gráfico com Biblioteca Plotly
    fig = px.bar(
            country_avg_cost_for_two,
            x='country_name',
            y='average_cost_for_two',
            text_auto='.0f',
            color='currency',
            labels={
                'country_name': 'Países',
                'average_cost_for_two': 'Preço para duas pessoas',
                'currency': 'Moeda'
            }
        )
    st.plotly_chart(fig, use_container_width=True, theme=None)


