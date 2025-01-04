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
from schemas.sentencia import OneSentenciaOut, SentenciaOut
from schemas.usuario import UsuarioInDB

sentencias = APIRouter(prefix="/api/v1/sentencias", tags=["materias"])


@sentencias.get("", response_model=CustomPage[SentenciaOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de sentencias"""
    if current_user.permissions.get("SENTENCIAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    query = database.query(Sentencia).filter(Sentencia.estatus == "A").order_by(Sentencia.id)
    return paginate(query)
