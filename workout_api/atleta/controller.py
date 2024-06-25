from datetime import datetime
from uuid import uuid4

from fastapi_pagination import add_pagination, Page, LimitOffsetPage
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import UUID4
from fastapi import APIRouter, status, Body, HTTPException, Query
from sqlalchemy import select
from typing import Optional
from workout_api import CategoriaModel, CentroTreinamentoModel
from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate, AtletaGetAllOut
from workout_api.contrib.dependencies import DatabaseDependency
from workout_api.atleta.models import AtletaModel

router = APIRouter()


@router.post(path='/', summary='Criar novo atleta', status_code=status.HTTP_201_CREATED, response_model=AtletaOut)
async def post(db_session: DatabaseDependency, atleta_in: AtletaIn = Body(...)) -> AtletaOut:
    categoria_name = atleta_in.categoria.nome
    centro_treinamento_name = atleta_in.centro_treinamento.nome

    categoria = (await db_session.execute(select(CategoriaModel).filter_by(nome=categoria_name))).scalars().first()
    centro_treinamento = (await db_session.execute(
        select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_name))).scalars().first()

    if not categoria:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'A categoria {categoria_name} não foi encontrada')

    if not centro_treinamento:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'O centro de treinamento {centro_treinamento_name} não foi encontrado')
    try:
        atleta_out = AtletaOut(id=uuid4(), created_at=datetime.utcnow(), **atleta_in.model_dump())
        atleta_model = AtletaModel(**atleta_out.model_dump(exclude={'categoria', 'centro_treinamento'}))

        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id

        db_session.add(atleta_model)
        await db_session.commit()
    except Exception:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,
                            detail=f'Já existe um atleta cadastrado com o cpf: {atleta_in.cpf}')
    return atleta_out


@router.get(path='/', summary='Consultar todos os atletas', status_code=status.HTTP_200_OK,
            response_model=LimitOffsetPage[AtletaGetAllOut], )
async def query(db_session: DatabaseDependency) -> Page[AtletaGetAllOut]:
    response = select(
        AtletaModel.id,
        AtletaModel.nome,
        CategoriaModel.nome.label('categoria'),
        CentroTreinamentoModel.nome.label('centro_treinamento')
    ).join(AtletaModel.categoria).join(AtletaModel.centro_treinamento)
    return await paginate(db_session, response)


@router.get(path='/{id}', summary='Consultar um atleta pelo ID', status_code=status.HTTP_200_OK,
            response_model=AtletaOut, )
async def query(id: UUID4, db_session: DatabaseDependency, nome: Optional[str] = Query(None),
                cpf: Optional[str] = Query(None)) -> AtletaOut:
    filters = [AtletaModel.id == id]
    if nome:
        filters.append(AtletaModel.nome == nome)
    if cpf:
        filters.append(AtletaModel.cpf == cpf)

    atleta: AtletaOut = (await db_session.execute(select(AtletaModel).filter(*filters))).scalars().first()

    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Atleta não encontrado para o id: {id}, nome: {nome}, e CPF {cpf}')

    return atleta


@router.patch(path='/{id}', summary='Editar um atleta pelo ID', status_code=status.HTTP_200_OK,
              response_model=AtletaOut, )
async def query(id: UUID4, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)) -> AtletaOut:
    atleta: AtletaOut = (await db_session.execute(select(AtletaModel).filter_by(id=id))).scalars().first()

    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Atleta não encontrada para o id: {id}')
    atleta_update = atleta_up.model_dump(exclude_unset=True)

    for key, value in atleta_update.items():
        setattr(atleta, key, value)
    await db_session.commit()
    await db_session.refresh(atleta)

    return atleta


@router.delete(path='/{id}', summary='Excluir um atleta pelo ID', status_code=status.HTTP_204_NO_CONTENT)
async def query(id: UUID4, db_session: DatabaseDependency) -> None:
    atleta: AtletaOut = (await db_session.execute(select(AtletaModel).filter_by(id=id))).scalars().first()

    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Atleta não encontrada para o id: {id}')

    await db_session.delete(atleta)
    await db_session.commit()

add_pagination(router)
