from uuid import uuid4
from fastapi import APIRouter, status, Body, HTTPException
from pydantic import UUID4
from sqlalchemy.future import select

from workout_api.centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut, CentroTreinamentoUpdate
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.contrib.dependencies import DatabaseDependency
from fastapi_pagination import add_pagination, Page, LimitOffsetPage
from fastapi_pagination.ext.sqlalchemy import paginate

router = APIRouter()


@router.post(path='/', summary='Cadastrar um centro de treinamento', status_code=status.HTTP_201_CREATED, response_model=CentroTreinamentoOut,)
async def post(db_session: DatabaseDependency, centro_treinamento_in: CentroTreinamentoIn = Body(...)) -> CentroTreinamentoOut:
    centro_treinamento_out = CentroTreinamentoOut(id=uuid4(), **centro_treinamento_in.model_dump())
    centro_treinamento_model = CentroTreinamentoModel(**centro_treinamento_out.model_dump())
    db_session.add(centro_treinamento_model)
    await db_session.commit()
    return centro_treinamento_out


@router.get(path='/', summary='Consultar todos centro de treinamento', status_code=status.HTTP_200_OK, response_model=LimitOffsetPage[CentroTreinamentoOut],)
async def query(db_session: DatabaseDependency) -> Page[CentroTreinamentoOut]:
    response = select(
        CentroTreinamentoModel.id,
        CentroTreinamentoModel.nome,
        CentroTreinamentoModel.endereco,
        CentroTreinamentoModel.proprietario
    )
    return await paginate(db_session, response)


@router.get(path='/{id}', summary='Consultar um centro de treinamento pelo ID', status_code=status.HTTP_200_OK, response_model=CentroTreinamentoOut,)
async def query_id(id: UUID4, db_session: DatabaseDependency) -> CentroTreinamentoOut:
    centro_treinamento: CentroTreinamentoOut = (await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))).scalars().first()

    if not centro_treinamento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Centro de treinamento não encontrada para o id: {id}')
    return centro_treinamento


@router.patch(path='/{id}', summary='Editar um centro de treinamento pelo ID', status_code=status.HTTP_200_OK,
              response_model=CentroTreinamentoOut, )
async def query(id: UUID4, db_session: DatabaseDependency, centro_treinamento_up: CentroTreinamentoUpdate = Body(...)) -> CentroTreinamentoOut:
    centro_treinamento: CentroTreinamentoOut = (await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))).scalars().first()

    if not centro_treinamento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Centro de treinamento não encontrada para o id: {id}')
    centro_treinamento_update = centro_treinamento_up.model_dump(exclude_unset=True)

    for key, value in centro_treinamento_update.items():
        setattr(centro_treinamento, key, value)
    await db_session.commit()
    await db_session.refresh(centro_treinamento)

    return centro_treinamento


@router.delete(path='/{id}', summary='Excluir um centro de treinamento pelo ID', status_code=status.HTTP_204_NO_CONTENT)
async def query(id: UUID4, db_session: DatabaseDependency) -> None:
    centro_treinamento: CentroTreinamentoOut = (await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))).scalars().first()

    if not centro_treinamento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Categoria não encontrada para o id: {id}')

    await db_session.delete(centro_treinamento)
    await db_session.commit()

add_pagination(router)
