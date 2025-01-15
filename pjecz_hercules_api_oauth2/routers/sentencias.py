"""
Sentencias, API v1
"""

from datetime import date, datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.authentications import get_current_user
from ..dependencies.database import Session, get_db
from ..dependencies.exceptions import MyAnyError, MyIsDeletedError, MyNotExistsError
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..models.autoridad import Autoridad
from ..models.permiso import Permiso
from ..models.sentencia import Sentencia
from ..schemas.sentencia import OneSentenciaOut, SentenciaCompleteOut, SentenciaOut, SentenciaRAGIn
from ..schemas.usuario import UsuarioInDB
from .autoridades import get_autoridad_with_clave

sentencias = APIRouter(prefix="/api/v1/sentencias", tags=["sentencias"])


def get_sentencia(database: Session, sentencia_id: int) -> Sentencia:
    """Consultar una sentencia por su ID"""
    sentencia = database.query(Sentencia).get(sentencia_id)
    if sentencia is None:
        raise MyNotExistsError("No existe esa sentencia")
    if sentencia.estatus != "A":
        raise MyIsDeletedError("No es activa ese sentencia, está eliminada")
    return sentencia


@sentencias.get("/{sentencia_id}", response_model=OneSentenciaOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
    sentencia_id: int,
):
    """Detalle de una sentencia a partir de su ID"""
    if current_user.permissions.get("SENTENCIAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        sentencia = get_sentencia(database, sentencia_id)
    except MyAnyError as error:
        return OneSentenciaOut(success=False, message=str(error), errors=[str(error)], data=None)
    return OneSentenciaOut(
        success=True,
        message="Detalle de una sentencia",
        errors=[],
        data=SentenciaCompleteOut.model_validate(sentencia),
    )


@sentencias.get("", response_model=CustomPage[SentenciaOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
    autoridad_clave: str = None,
    creado: date = None,
    creado_desde: date = None,
    creado_hasta: date = None,
):
    """Paginado de sentencias"""
    if current_user.permissions.get("SENTENCIAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    query = database.query(Sentencia)
    if autoridad_clave is not None:
        try:
            autoridad = get_autoridad_with_clave(database, autoridad_clave)
        except MyAnyError as error:
            return CustomPage(success=False, message=str(error), errors=[str(error)], data=None)
        query = query.join(Autoridad).filter(Autoridad.clave == autoridad.clave)
    if creado is not None:
        query = query.filter(Sentencia.creado >= datetime(creado.year, creado.month, creado.day, 0, 0, 0))
        query = query.filter(Sentencia.creado <= datetime(creado.year, creado.month, creado.day, 23, 59, 59))
    else:
        if creado_desde is not None:
            query = query.filter(Sentencia.creado >= datetime(creado_desde.year, creado_desde.month, creado_desde.day, 0, 0, 0))
        if creado_hasta is not None:
            query = query.filter(
                Sentencia.creado <= datetime(creado_hasta.year, creado_hasta.month, creado_hasta.day, 23, 59, 59)
            )
    query = query.filter(Sentencia.estatus == "A").order_by(Sentencia.id)
    return paginate(query)


@sentencias.put("/rag", response_model=OneSentenciaOut)
async def actualizar_rag(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
    rag: SentenciaRAGIn,
):
    """Actualizar Retrieval-Augmented Generation (RAG) de una sentencia"""
    if current_user.permissions.get("SENTENCIAS", 0) < Permiso.MODIFICAR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    sentencia = get_sentencia(database, rag.id)
    hay_cambios = False
    if rag.analisis is not None and sentencia.rag_analisis != rag.analisis:
        sentencia.rag_analisis = rag.analisis
        sentencia.rag_fue_analizado_tiempo = datetime.now(tz=timezone.utc)
        hay_cambios = True
    if rag.sintesis is not None and sentencia.rag_sintesis != rag.sintesis:
        sentencia.rag_sintesis = rag.sintesis
        sentencia.rag_fue_sintetizado_tiempo = datetime.now(tz=timezone.utc)
        hay_cambios = True
    if rag.categorias is not None and sentencia.rag_categorias != rag.categorias:
        sentencia.rag_categorias = rag.categorias
        sentencia.rag_fue_categorizado_tiempo = datetime.now(tz=timezone.utc)
        hay_cambios = True
    if hay_cambios is False:
        return OneSentenciaOut(
            success=False,
            message="No hay cambios en las columnas RAG de la sentencia",
            errors=[],
            data=SentenciaCompleteOut.model_validate(sentencia),
        )
    database.add(sentencia)
    database.commit()
    return OneSentenciaOut(
        success=True,
        message="Se actualizó la sentencia",
        errors=[],
        data=SentenciaCompleteOut.model_validate(sentencia),
    )
