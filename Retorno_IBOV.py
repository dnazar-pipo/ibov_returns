import streamlit as st
from datetime import date, datetime
from services.services_ibov import generate_graph, calculate_returns_in_periods, returns_between_boundaries, generate_percentile_table_from_returns
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from math import ceil, floor


DATA_INICIAL = date(2000, 1, 1)
DATA_FINAL = date(2023, 12, 12)
DATABASE_URL = 'sqlite:///data/database.sqlite'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(engine)


st.set_page_config(
    page_title="Retornos Historicos IBOV",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    st.header("Análise de Retornos Históricos do IBOV")
    st.divider()

    with Session() as session:
        with st.container():
            col1, col2 = st.columns((1, 1))

            with col1:
                meses = st.slider("Janela de Retorno - Meses", 1, 6, 1, 1)

            with col2:
                datas = st.slider("Janela Analisada (De [ano] a [ano]):", value=[2000, 2023], min_value=2000, max_value=2023)
                DATA_INICIAL = date(int(datas[0]), 1, 1)
                DATA_FINAL = date(int(datas[1]), 12, 31)
                resultado_retornos = calculate_returns_in_periods(local_session=session,
                                                                  data_inicial=DATA_INICIAL,
                                                                  data_final=DATA_FINAL,
                                                                  tamanho_janela_meses=meses)
                
            with col1:
                range_retorno = st.slider("Observações Entre:", value=[-15, 15], min_value=floor(min(resultado_retornos)*100), max_value=ceil(max(resultado_retornos)*100))
                retorno_minimo = range_retorno[0]/100
                retorno_maximo = range_retorno[1]/100
                numero_retornos = returns_between_boundaries(retorno_minimo=retorno_minimo,
                                                                retorno_maximo=retorno_maximo,
                                                                retornos=resultado_retornos)
            with col2:
                with st.container():
                    subcol1, subcol2 = st.columns((1, 1))
                    with subcol1:
                        st.metric("Número de Observações", f"{round(numero_retornos, 2)}/{len(resultado_retornos)}")
                    with subcol2:
                        st.metric("(%) Das Observações", f"{round(numero_retornos/len(resultado_retornos)*100, 2)}%")
            

    with st.container():
        col1, col2 = st.columns((1, 4))

        with col1:
            largura_bins = float(
                    st.slider("Largura Bins (%)", 1.0, 10.0, 2.0, 0.5))/100


    with st.container():
        col1, col2 = st.columns((3, 1))
        with col1: # Histogram:
            graph = generate_graph(meses=meses,
                                largura_bins=largura_bins,
                                retornos=resultado_retornos, altura=350)
            st.bokeh_chart(graph, use_container_width=True)
        with col2: # Information table and metrics:
            fig = generate_percentile_table_from_returns(resultado_retornos)
            st.plotly_chart(fig, use_container_width=True)
        


if __name__ == '__main__':
    main()
