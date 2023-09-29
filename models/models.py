
from sqlalchemy import Column, Integer, Date, Float, Enum as SQLEnum
from enum import Enum
from models.base import Base


class TipoBenchmark(Enum):
    IBOV = 'IBOV'
    CDI = 'CDI'


class Benchmark(Base):
    __tablename__ = 'benchmarks'

    id = Column(Integer, primary_key=True)
    benchmark = Column(SQLEnum(TipoBenchmark))
    data = Column(Date)
    valor = Column(Float)
