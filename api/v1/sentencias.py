"""
Sentencias, API v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from lib.authentications import get_current_user
from lib.database import Session, get_db
from lib.exceptions import MyAnyError, MyIsDeletedError, MyNotExistsError
from lib.fastapi_pagination_custom_page import CustomPage
from models.permiso import Permiso
from models.sentencia import Sentencia
from schemas.sentencia import OneSentenciaOut, SentenciaCompleteOut, SentenciaOut
from schemas.usuario import UsuarioInDB

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
        success=True, message="Detalle de una sentencia", errors=[], data=SentenciaCompleteOut.model_validate(sentencia)
    )


@sentencias.get("", response_model=CustomPage[SentenciaOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de sentencias"""
    if current_user.permissions.get("SENTENCIAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    query = database.query(Sentencia).filter(Sentencia.estatus == "A").order_by(Sentencia.id.desc())
    return paginate(query)
