import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})


fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

st.header('Hello Streamlit')
st.subheader('Streamlit: bla bla bla')

st.write(fig)

