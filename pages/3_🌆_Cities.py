# Libraries
import pandas as pd
import folium
import plotly_express as px
import inflection
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image
import altair as alt

st.set_page_config(page_title='Visão Cidades', page_icon='🌆', layout='wide')

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

# Limpando a base de dados
def clean_datafram(dataframe):
    df1 = dataframe.copy()
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
    # retirando culinária Drinks Only e Mineira da base
    df1 = df1.drop(df1[(df1["cuisines"] == "Drinks Only")].index)
    df1 = df1.drop(df1[(df1["cuisines"] == "Mineira")].index)

    return df1

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
df1 = clean_datafram(df1)

# =====================================
# Barra Lateral
# =====================================
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
st.header('🌆 Visão Cidades')

with st.container():
    city_with_more_restaurants = (df1.loc[:, ['city', 'country_name', 'restaurant_id']]
                                  .groupby(['country_name', 'city'])
                                  .count()
                                  .sort_values(['restaurant_id', 'city'], ascending=[False, True])
                                  .reset_index()
                                  )
    st.markdown('<h5 style= "text-align: center">TOP 10 cidades com mais restaurantes</h5>', unsafe_allow_html=True)

    # Gráfico com Biblioteca Plotly
    fig = px.bar(
        city_with_more_restaurants.head(10),
        x='city',
        y='restaurant_id',
        text_auto='.0f',
        color='country_name',
        labels={
            'city': 'Cidade',
            'restaurant_id': 'Quantidade de Restaurantes',
            'country_name': 'País'
        }
    )
    st.plotly_chart(fig, use_container_width=True, theme=None)

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        city_restaurants_above_4 = (df1.loc[df1['aggregate_rating'] >= 4, ['restaurant_id', 'city', 'country_name']]
                                        .groupby(['country_name','city'])
                                        .count()
                                        .sort_values(['restaurant_id', 'city'], ascending=[False, True])
                                        .reset_index()
                                        )
        
        st.markdown('<h5 style= "text-align: center">TOP 10 cidades: Restaurantes com avaliação média acima de 4</h5>', unsafe_allow_html=True)
        
        # Gráfico com Biblioteca Plotly
        fig = px.bar(
        city_restaurants_above_4.head(10),
        x='city',
        y='restaurant_id',
        text_auto='.0f',
        color='country_name',
        labels={
            'city': 'Cidade',
            'restaurant_id': 'Quantidade de Restaurantes',
            'country_name': 'País'
        }
    )
        st.plotly_chart(fig, use_container_width=True, theme=None)

    with col2:
        city_restaurants_below_2_5 = (df1.loc[df1['aggregate_rating'] <= 2.5, ['restaurant_id', 'city', 'country_name']]
                                        .groupby(['country_name','city'])
                                        .count()
                                        .sort_values(['restaurant_id', 'city'], ascending=[False, True])
                                        .reset_index()
                                        )
        st.markdown('<h5 style= "text-align: center"> TOP 10 cidades: Restaurantes com avaliação média abaixo de 2.5</h5>', unsafe_allow_html=True)

        # Gráfico com Biblioteca Plotly
        fig = px.bar(
        city_restaurants_below_2_5.head(10),
        x='city',
        y='restaurant_id',
        text_auto='.0f',
        color='country_name',
        labels={
            'city': 'Cidade',
            'restaurant_id': 'Quantidade de Restaurantes',
            'country_name': 'País'
        }
    )
        st.plotly_chart(fig, use_container_width=True, theme=None)

with st.container():
    city_types_of_cuisine = (df1.loc[:, ['city', 'country_name', 'cuisines']]
                                  .groupby(['country_name', 'city'])
                                  .nunique()
                                  .sort_values(['cuisines', 'country_name'], ascending=[False, True])
                                  .reset_index()
                                  )
    
    st.markdown('<h5 style= "text-align: center">Top 10 cidades com maior variedade de culinárias</h5>', unsafe_allow_html=True)
    
# Gráfico com Biblioteca Plotly
    fig = px.bar(
        city_types_of_cuisine.head(10),
        x='city',
        y='cuisines',
        text_auto='.0f',
        color='country_name',
        labels={
            'city': 'Cidade',
            'cuisines': 'Quantidade de Culinárias',
            'country_name': 'País'
        }
    )
    st.plotly_chart(fig, use_container_width=True, theme=None)
