from sqlalchemy import create_engine
from models.models import Benchmark, TipoBenchmark
from models.base import Base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import time
from datetime import datetime

engine = create_engine('sqlite:///data/database.sqlite')
Session = sessionmaker(engine)
session = Session()



def criar_todos():
    t = time.time()
    Base.metadata.create_all(engine)
    print(f"Tabelas criadas em {round(time.time() - t, 4)} segundos")

def importar_ibov():

    def convert_to_date(x):
        try:
            x = datetime.strptime(x, "%d/%m/%Y").date()
        except ValueError:
            x = None
        return x

    t = time.time()
    df = pd.read_csv(r'C:\Users\DaniloNazar\OneDrive - Pipo Capital\Desktop\benchmarks.csv', converters={"Date": lambda x: convert_to_date(x)})
    df.dropna(inplace=True, subset=['Close'])

    ibovs = []
    for index, row in df.iterrows():
        new_ibov = Benchmark(
            benchmark = TipoBenchmark.IBOV,
            data = row['Date'],
            valor = row['Close']
        )
        ibovs.append(new_ibov)
    
    session.query(Benchmark).filter(Benchmark.benchmark == TipoBenchmark.IBOV).delete()
    session.add_all(ibovs)
    session.commit()
    print(f"Dados hostoricos do IBOV importados em {round(time.time() - t, 4)} segundos")


if __name__ == '__main__':
    criar_todos()
    importar_ibov()