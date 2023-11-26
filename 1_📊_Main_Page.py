# Libraries
import pandas as pd
import folium
import plotly_express as px
import inflection
import streamlit as st
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
from PIL import Image

st.set_page_config(page_title='Visão Geral', page_icon='📊', layout='wide')

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

# Logo Fome Zero na barra lateral
image_path = 'food_delivery.png'
image = Image.open(image_path)

col1, col2 = st.sidebar.columns(2, gap='small')

with col1: 
    col1.image(image, width=120)

with col2:
   col2.markdown(' ')
   col2.markdown(' ')
   col2.markdown(' ')
   col2.markdown(' ')
   col2.markdown('## Fome Zero')

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
st.header('Fome Zero')
st.markdown('## O melhor lugar para encontrar seu novo restaurante favorito!')
st.markdown('#### Temos as seguintes marcas dentro da nossa plataforma:')

with st.container():
    col1, col2, col3, col4, col5 = st.columns(5, gap='small')

    with col1:
        unique_restaurants = df1.loc[:, 'restaurant_id'].count()
        col1.metric('Restaurantes Cadastrados', unique_restaurants)
    with col2:
        unique_countries = df1['country_code'].nunique()
        col2.metric('Países cadastrados', unique_countries)
    with col3:
        unique_cities = len(df1['city'].unique())
        col3.metric('Cidades Cadastradas', unique_cities)
    with col4:
        sum_votes = format(df1.loc[:, 'votes'].sum(), ',d')
        col4.metric('Avaliações feitas', sum_votes.replace(',','.'))
    with col5:
        unique_cuisines = df1['cuisines'].nunique()
        col5.metric('Tipos de Culinária', unique_cuisines)

with st.container():
    # df_aux = (df1.loc[:, ['city', 'country_name', 'longitude', 'latitude', 'cuisines', 'currency', 'aggregate_rating', 'restaurant_name', 'average_cost_for_two']]
    #       .groupby(['country_name', 'city'])
    #       .mean('aggregate_rating')
    #       .reset_index()
    #       )
    # map = folium.Map()

    # for index, location_info in df_aux.iterrows():
    #     folium.Marker([
    #         location_info['latitude'],
    #         location_info['longitude']
    #     ], popup= location_info[['country_name','city', 'aggregate_rating', 'average_cost_for_two']]).add_to(map)

    # folium_static(map, width=1024, height=600)

    def create_map(dataframe):
        f = folium.Figure(width=1920, height=1080)

        m = folium.Map(max_bounds=True).add_to(f)

        marker_cluster = MarkerCluster().add_to(m)

        for _, line in dataframe.iterrows():

            name = line["restaurant_name"]
            price_for_two = line["average_cost_for_two"]
            cuisine = line["cuisines"]
            currency = line["currency"]
            rating = line["aggregate_rating"]
            color = f'{line["color_name"]}'

            html = "<p><strong>{}</strong></p>"
            html += "<p>Price: {},00 ({}) para dois"
            html += "<br />Type: {}"
            html += "<br />Aggragate Rating: {}/5.0"
            html = html.format(name, price_for_two, currency, cuisine, rating)

            popup = folium.Popup(
                folium.Html(html, script=True),
                max_width=500,
            )

            folium.Marker(
                [line["latitude"], line["longitude"]],
                popup=popup,
                icon=folium.Icon(color=color, icon="home", prefix="fa"),
            ).add_to(marker_cluster)

        folium_static(m, width=1024, height=768)

    st.markdown('### Nossos restaurantes pelo mundo:')
    create_map(df1)

