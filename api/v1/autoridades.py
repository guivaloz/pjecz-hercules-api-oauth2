"""
Autoridades, API v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from lib.authentications import get_current_user
from lib.database import Session, get_db
from lib.exceptions import MyAnyError, MyIsDeletedError, MyNotExistsError
from lib.fastapi_pagination_custom_page import CustomPage
from models.autoridad import Autoridad
from models.permiso import Permiso
from schemas.autoridad import AutoridadOut, OneAutoridadOut
from schemas.usuario import UsuarioInDB

autoridades = APIRouter(prefix="/api/v1/autoridades", tags=["materias"])


@autoridades.get("", response_model=CustomPage[AutoridadOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de autoridades"""
    if current_user.permissions.get("AUTORIDADES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    query = database.query(Autoridad).filter(Autoridad.estatus == "A").order_by(Autoridad.clave)
    return paginate(query)
