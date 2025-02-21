# Import python packages
import requests
import pandas as pd
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be", name_on_order)

# Conexión a Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Obtener datos desde Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convertir a Pandas DataFrame
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)

st.stop()  # (Verifica los datos antes de continuar)

# Convertir nombres de frutas a una lista para `st.multiselect()`
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),  # Cambio aquí
    max_selections=5
)

if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Cambio aquí para mejorar formato

    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].values

        if search_on.size > 0 and pd.notna(search_on[0]):  # Validar si hay datos
            search_value = search_on[0]

            st.subheader(f"{fruit_chosen} Nutrition Information")
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_value}")

            if smoothiefroot_response.status_code == 200:
                st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
            else:
                st.warning(f"Could not fetch data for {fruit_chosen}.")
        else:
            st.warning(f"No search data available for {fruit_chosen}.")

    # Insertar pedido en la base de datos
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

# Prueba de solicitud externa con una fruta específica
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")

if smoothiefroot_response.status_code == 200:
    st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
else:
    st.error("Could not fetch watermelon data.")
