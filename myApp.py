import streamlit as st
import pandas as pd

c = st.container()


st.title("counter")
if 'count' not in st.session_state:
    st.session_state.count = 0

inc_value = 1

def increment_counter(inc_value):
    st.session_state.count += inc_value

increment = st.button('Increment', on_click=increment_counter, args=(inc_value, ))

st.write('Count = ', st.session_state.count)

with st.container():
    col1, col2, col3 = st.columns(3)
    col1.metric("Temperature", "70 °F", "1.2 °F")
    col2.metric("Wind", "9 mph", "-8%")
    col3.metric("Humidity", "86%", "4%")

with st.container():
    st.title("D3")
