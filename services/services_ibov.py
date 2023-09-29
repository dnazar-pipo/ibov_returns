from datetime import date
from models.models import Benchmark, TipoBenchmark
from sqlalchemy import and_, asc
from sqlalchemy.orm import Session
from bokeh.plotting import figure
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.figure_factory as ff


def retrieve_ibov_data(local_session: Session, data_inicial: date, data_final: date):
    results = (local_session.query(Benchmark)
               .filter(
                   and_(
                       Benchmark.benchmark == TipoBenchmark.IBOV,
                       Benchmark.data >= data_inicial,
                       Benchmark.data <= data_final
                   )
    ).order_by(asc(Benchmark.data)).all())
    return results


def calculate_returns_in_periods(local_session: Session, data_inicial: date, data_final: date, tamanho_janela_meses: int):
    dados_ibov_periodo = retrieve_ibov_data(
        local_session=local_session, data_inicial=data_inicial, data_final=data_final)

    NUMERO_DIAS_UTEIS = tamanho_janela_meses * 21
    passagens = len(dados_ibov_periodo) // NUMERO_DIAS_UTEIS

    retornos_janelas = []
    for passagem in range(passagens):
        start_value = dados_ibov_periodo[NUMERO_DIAS_UTEIS * passagem].valor
        end_value = dados_ibov_periodo[NUMERO_DIAS_UTEIS *
                                       (passagem + 1) - 1].valor

        retorno = (end_value / start_value) - 1
        retornos_janelas.append(retorno)

    return retornos_janelas


def round_off_rating(number, largura=.05):
    resto = number % largura if number < 0 else (number + largura) % largura
    if number < 0:
        return round(number - resto, 3)
    else:
        return round(number + largura - resto, 3)


def generate_graph(meses: int,
                   largura_bins: float,
                   retornos: list,
                   altura: int = 400):

    p = figure(width=700,
               height=altura,
               title=f"Distribuição Retorno IBOV - {meses} meses", toolbar_location=None)

    banda_min = round_off_rating(min(retornos), largura_bins)
    banda_max = round_off_rating(max(retornos), largura_bins)
    n_bins = int((banda_max-banda_min)/largura_bins) + 1

    bins = np.linspace(banda_min, banda_max, n_bins)
    hist, edges = np.histogram(retornos, density=False, bins=bins)
    p.quad(top=hist, bottom=0,
           left=edges[:-1], right=edges[1:], fill_color="skyblue", line_color="white")

    # Plotting Normal Curve:
    # retornos = np.array(retornos)
    # mu, sigma = retornos.mean(), retornos.std()
    # x = bins
    # pdf = 1/(sigma * np.sqrt(2*np.pi)) * np.exp(-(x-mu)**2 / (2*sigma**2))
    # p.line(x, pdf, line_color='navy', line_width=2)

    p.y_range.start = 0
    p.xaxis.axis_label = "Retorno Percentual IBOV"
    p.yaxis.axis_label = "(%) De Observações"
    return p


def returns_between_boundaries(retorno_minimo: float, retorno_maximo: float, retornos: list):
    criteria = [r for r in retornos if (
        r >= retorno_minimo and r <= retorno_maximo)]
    return len(criteria)


def calculate_percentiles(retornos: list):
    PERCENTILES = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    p = np.percentile(a=retornos, q=PERCENTILES)
    table = [['Min', f"{round(p[0]*100, 2)}%"],
             ['10%', f"{round(p[1]*100, 2)}%"],
             ['20%', f"{round(p[2]*100, 2)}%"],
             ['30%', f"{round(p[3]*100, 2)}%"],
             ['40%', f"{round(p[4]*100, 2)}%"],
             ['50%', f"{round(p[5]*100, 2)}%"],
             ['60%', f"{round(p[6]*100, 2)}%"],
             ['70%', f"{round(p[7]*100, 2)}%"],
             ['80%', f"{round(p[8]*100, 2)}%"],
             ['90%', f"{round(p[9]*100, 2)}%"],
             ['Max', f"{round(p[10]*100, 2)}%"]]
    df = pd.DataFrame(table, columns=['Percentis', 'Retorno (%)'])
    return df


def create_percentile_table(df):
    fig = go.Figure(
        data=[go.Table(
            header=dict(values=list(df.columns),
                        fill_color='#2B1634',
                        font_color='white',
                        align='center'),
            cells=dict(values=df.transpose().values.tolist(),
                        fill_color='black',
                        font_color='white',
                        height=30,
                        align='center'))])
    
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    
    # fig =  ff.create_table(df, height_constant=22)
    return fig


def generate_percentile_table_from_returns(retornos: list):
    df = calculate_percentiles(retornos)
    fig = create_percentile_table(df)
    return fig
