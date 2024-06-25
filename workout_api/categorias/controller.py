from uuid import uuid4
from fastapi import APIRouter, status, Body, HTTPException
from pydantic import UUID4
from sqlalchemy.future import select
from fastapi_pagination import add_pagination, Page, LimitOffsetPage
from fastapi_pagination.ext.sqlalchemy import paginate

from workout_api import AtletaModel
from workout_api.categorias.schemas import CategoriaIn, CategoriaOut, CategoriaUpdate
from workout_api.categorias.models import CategoriaModel
from workout_api.contrib.dependencies import DatabaseDependency

router = APIRouter()


@router.post(path='/', summary='Criar nova categoria', status_code=status.HTTP_201_CREATED,
             response_model=CategoriaOut, )
async def post(db_session: DatabaseDependency, categoria_in: CategoriaIn = Body(...)) -> CategoriaOut:
    categoria_out = CategoriaOut(id=uuid4(), **categoria_in.model_dump())
    categoria_model = CategoriaModel(**categoria_out.model_dump())
    db_session.add(categoria_model)
    await db_session.commit()
    return categoria_out


@router.get(path='/', summary='Consultar todas categoria', status_code=status.HTTP_200_OK,
            response_model=LimitOffsetPage[CategoriaOut], )
async def query(db_session: DatabaseDependency) -> Page[CategoriaOut]:
    response = select(
        CategoriaModel.id,
        CategoriaModel.nome
    )
    return await paginate(db_session, response)


@router.get(path='/{id}', summary='Consultar uma categoria pelo ID', status_code=status.HTTP_200_OK,
            response_model=CategoriaOut, )
async def query(id: UUID4, db_session: DatabaseDependency) -> CategoriaOut:
    categoria: CategoriaOut = (await db_session.execute(select(CategoriaModel).filter_by(id=id))).scalars().first()

    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Categoria não encontrada para o id: {id}')
    return categoria


@router.patch(path='/{id}', summary='Editar uma categoria pelo ID', status_code=status.HTTP_200_OK,
              response_model=CategoriaOut, )
async def query(id: UUID4, db_session: DatabaseDependency, categoria_up: CategoriaUpdate = Body(...)) -> CategoriaOut:
    categoria: CategoriaOut = (await db_session.execute(select(CategoriaModel).filter_by(id=id))).scalars().first()

    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Categoria não encontrada para o id: {id}')
    categoria_update = categoria_up.model_dump(exclude_unset=True)

    for key, value in categoria_update.items():
        setattr(categoria, key, value)
    await db_session.commit()
    await db_session.refresh(categoria)

    return categoria


@router.delete(path='/{id}', summary='Excluir uma categoria pelo ID', status_code=status.HTTP_204_NO_CONTENT)
async def query(id: UUID4, db_session: DatabaseDependency) -> None:
    categoria: CategoriaOut = (await db_session.execute(select(CategoriaModel).filter_by(id=id))).scalars().first()

    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Categoria não encontrada para o id: {id}')

    await db_session.delete(categoria)
    await db_session.commit()


add_pagination(router)
