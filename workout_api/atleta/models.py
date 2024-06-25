from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Float, ForeignKey
from workout_api.contrib.models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship

class AtletaModel(BaseModel):
    __tablename__ = 'atletas'

    pk_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(50), primary_key=False)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, primary_key=False)
    idade: Mapped[int] = mapped_column(Integer, primary_key=False)
    peso: Mapped[float] = mapped_column(Float, primary_key=False)
    altura: Mapped[str] = mapped_column(String(4), primary_key=False)
    sexo: Mapped[str] = mapped_column(String(1), primary_key=False)
    created_at: Mapped[datetime] = mapped_column(DateTime,nullable=False)
    categoria_id: Mapped[int] = mapped_column(ForeignKey('categorias.pk_id'))
    centro_treinamento_id: Mapped[int] = mapped_column(ForeignKey('centro_treinamento.pk_id'))

    categoria: Mapped['CategoriaModel'] = relationship(back_populates='atleta', lazy='selectin')
    centro_treinamento: Mapped['CentroTreinamentoModel'] = relationship(back_populates='atleta', lazy='selectin')
