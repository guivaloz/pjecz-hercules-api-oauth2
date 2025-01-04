"""
Materias, API v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from lib.authentications import get_current_user
from lib.database import Session, get_db
from lib.exceptions import MyAnyError, MyIsDeletedError, MyNotExistsError
from lib.fastapi_pagination_custom_page import CustomPage
from models.materia import Materia
from models.permiso import Permiso
from schemas.materia import MateriaOut, OneMateriaOut
from schemas.usuario import UsuarioInDB

materias = APIRouter(prefix="/api/v1/materias", tags=["materias"])


@materias.get("", response_model=CustomPage[MateriaOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de materias"""
    if current_user.permissions.get("MATERIAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    query = database.query(Materia).filter(Materia.estatus == "A").order_by(Materia.id)
    return paginate(query)
