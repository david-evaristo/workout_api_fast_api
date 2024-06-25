from sqlalchemy import Integer, String
from workout_api.contrib.models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CentroTreinamentoModel(BaseModel):
    __tablename__ = 'centro_treinamento'

    pk_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(50), unique=True, primary_key=False)
    endereco: Mapped[str] = mapped_column(String(60), primary_key=False)
    proprietario: Mapped[str] = mapped_column(String(30), primary_key=False)
    atleta: Mapped['AtletaModel'] = relationship(back_populates='centro_treinamento')
