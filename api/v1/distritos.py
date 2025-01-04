"""
Distritos, API v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from lib.authentications import get_current_user
from lib.database import Session, get_db
from lib.exceptions import MyAnyError, MyIsDeletedError, MyNotExistsError
from lib.fastapi_pagination_custom_page import CustomPage
from models.distrito import Distrito
from models.permiso import Permiso
from schemas.distrito import DistritoOut, OneDistritoOut
from schemas.usuario import UsuarioInDB

distritos = APIRouter(prefix="/api/v1/distritos", tags=["materias"])


@distritos.get("", response_model=CustomPage[DistritoOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de distritos"""
    if current_user.permissions.get("DISTRITOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    query = database.query(Distrito).filter(Distrito.estatus == "A").order_by(Distrito.id)
    return paginate(query)
