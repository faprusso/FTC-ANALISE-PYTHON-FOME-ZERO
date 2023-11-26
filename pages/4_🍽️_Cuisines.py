# Libraries
import pandas as pd
import folium
import plotly_express as px
import inflection
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image
import altair as alt
from st_aggrid import AgGrid

st.set_page_config(page_title='Visão Restaurantes', page_icon='🍔', layout='wide')

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

def rest_per_cuisine(pos):
    ## Top 10 cuisines -> baseado na melhor avaliação média e quantidade de votos
    top_cuisines = (df1.loc[:, ['cuisines','restaurant_name', 'aggregate_rating', 'votes', 'average_cost_for_two' ]]
                        .groupby(['cuisines'])
                        .mean('aggregate_rating')
                        .sort_values(['aggregate_rating', 'votes'], ascending=[False,False])
                        .reset_index()
                        )

    ## Top restaurantes por cuisine
    cols = ['restaurant_id', 'restaurant_name', 'country_name', 'city', 'cuisines', 'aggregate_rating', 'votes', 'average_cost_for_two', 'currency' ]
    best_restaurants_per_cuisine = (df1.loc[:, cols]
                        .groupby(['restaurant_id', 'restaurant_name', 'cuisines', 'country_name', 'city', 'aggregate_rating', 'votes', 'average_cost_for_two', 'currency'])
                        .mean()
                        .sort_values(['aggregate_rating', 'votes', 'restaurant_id'], ascending=[False,False,True])
                        .reset_index()
                        )

    top_1_restaurant_per_cuisine = best_restaurants_per_cuisine.loc[best_restaurants_per_cuisine['cuisines'] == top_cuisines['cuisines'][pos], :]

    return top_1_restaurant_per_cuisine

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

# slider para seleção de quantidade de países
qty_select = st.sidebar.slider(
    'Selecione a quantidade de restaurantes que deseja visualizar', 1, 20, 10
)

# criando lista de tipos de culinária
cuisines_types = list(df1['cuisines'].unique())

# select de cuisines
cuisines_select = st.sidebar.multiselect(
    'Escolha quais tipos de culinária deseja visualizar',
    cuisines_types,
    default=cuisines_types
)
# Aplicação dos filtros
linhas_selecionadas = df1['cuisines'].isin(cuisines_select)
df1 = df1.loc[linhas_selecionadas, :]



# =====================================
# Layout no Streamlit
# =====================================
st.header('🍽️ Visão Restaurantes')

st.markdown('## Os Melhores Restaurantes dos Principais tipos de Culinária')
with st.container():
    col1, col2, col3, col4, col5 = st.columns(5, gap='small')
    with col1:
        rest_1 = rest_per_cuisine(0)

        col1.metric(
            label=f'Culinária: {rest_1.iloc[0,2]}',
            value=f'{rest_1.iloc[0,5]}/5.0',
            help=f"""
            Restaurante: {rest_1.iloc[0,1]}\n
            País: {rest_1.iloc[0,3]}\n
            Cidade: {rest_1.iloc[0,4]}\n
            Média de prato para dois: {rest_1.iloc[0,7]} ({rest_1.iloc[0,8]})
            """
        )
    with col2:
        rest_2 = rest_per_cuisine(1)

        col2.metric(
            label=f'Culinária: {rest_2.iloc[0,2]}',
            value=f'{rest_2.iloc[0,5]}/5.0',
            help=f"""
            Restaurante: {rest_2.iloc[0,1]}\n
            País: {rest_2.iloc[0,3]}\n
            Cidade: {rest_2.iloc[0,4]}\n
            Média de prato para dois: {rest_2.iloc[0,7]} ({rest_2.iloc[0,8]})
            """
        ) 
    with col3:
        rest_3 = rest_per_cuisine(2)

        col3.metric(
            label=f'Culinária: {rest_3.iloc[0,2]}',
            value=f'{rest_3.iloc[0,5]}/5.0',
            help=f"""
            Restaurante: {rest_3.iloc[0,1]}\n
            País: {rest_3.iloc[0,3]}\n
            Cidade: {rest_3.iloc[0,4]}\n
            Média de prato para dois: {rest_3.iloc[0,7]} ({rest_3.iloc[0,8]})
            """
        )
    with col4:
        rest_4 = rest_per_cuisine(3)

        col4.metric(
            label=f'Culinária: {rest_4.iloc[0,2]}',
            value=f'{rest_4.iloc[0,5]}/5.0',
            help=f"""
            Restaurante: {rest_4.iloc[0,1]}\n
            País: {rest_4.iloc[0,3]}\n
            Cidade: {rest_4.iloc[0,4]}\n
            Média de prato para dois: {rest_4.iloc[0,7]} ({rest_4.iloc[0,8]})
            """
        )
    with col5:
        rest_5 = rest_per_cuisine(4)

        col5.metric(
            label=f'Culinária: {rest_5.iloc[0,2]}',
            value=f'{rest_5.iloc[0,5]}/5.0',
            help=f"""
            Restaurante: {rest_5.iloc[0,1]}\n
            País: {rest_5.iloc[0,3]}\n
            Cidade: {rest_5.iloc[0,4]}\n
            Média de prato para dois: {rest_5.iloc[0,7]} ({rest_5.iloc[0,8]})
            """
        )    


with st.container():
    st.markdown(f'## Top {qty_select} restaurantes')
    col = ['restaurant_id', 'restaurant_name', 'country_name', 'city', 'cuisines', 'aggregate_rating', 'votes', 'average_cost_for_two' ]
    top_ten_restaurants = (df1.loc[:, col]
                       .groupby(['restaurant_id', 'restaurant_name', 'cuisines', 'country_name', 'city', 'aggregate_rating', 'votes', 'average_cost_for_two'])
                       .mean()
                       .sort_values(['aggregate_rating', 'votes', 'restaurant_id'], ascending=[False,False,True])
                       .reset_index()
                       )
    
    # st.dataframe(top_ten_restaurants.head(qty_select), height=400)

    AgGrid(top_ten_restaurants.head(qty_select))

with st.container():
    col1, col2 = st.columns(2)

    with col1: 
        col = ['cuisines', 'aggregate_rating', 'votes', 'average_cost_for_two' ]
        top_ten_cuisines = (df1.loc[:, col]
                       .groupby('cuisines')
                       .mean('aggregate_rating')
                       .sort_values(['aggregate_rating', 'votes'], ascending=[False,False])
                       .reset_index()
                       )
        
        fig = px.bar(
            top_ten_cuisines.head(qty_select),
            x='cuisines',
            y='aggregate_rating',
            text_auto='.2f',
            title=f'TOP {qty_select} melhores Tipos de Culinária',
            labels = {
                'cuisines': 'Tipos de Culinária',
                'aggregate_rating': 'Avaliação média'
            }
        )
        st.plotly_chart(fig, use_container_width=True, theme=None)

    with col2: 
        worst_cuisines = (df1.loc[:, col]
                       .groupby('cuisines')
                       .mean('aggregate_rating')
                       .sort_values(['aggregate_rating', 'votes'], ascending=[True,False])
                       .reset_index()
                       )
        
        fig = px.bar(
            worst_cuisines.head(qty_select),
            x='cuisines',
            y='aggregate_rating',
            text_auto='.2f',
            title=f'TOP {qty_select} piores Tipos de Culinária',
            labels = {
                'cuisines': 'Tipos de Culinária',
                'aggregate_rating': 'Avaliação média'
            }
        )
        st.plotly_chart(fig, use_container_width=True, theme=None)