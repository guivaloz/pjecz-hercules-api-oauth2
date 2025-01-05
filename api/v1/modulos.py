"""
Modulos, API v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from lib.authentications import get_current_user
from lib.database import Session, get_db
from lib.fastapi_pagination_custom_page import CustomPage
from models.modulo import Modulo
from models.permiso import Permiso
from schemas.modulo import ModuloOut
from schemas.usuario import UsuarioInDB

modulos = APIRouter(prefix="/api/v1/modulos", tags=["sistema"])


@modulos.get("", response_model=CustomPage[ModuloOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de modulos"""
    if current_user.permissions.get("MODULOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    query = database.query(Modulo).filter(Modulo.estatus == "A").order_by(Modulo.nombre)
    return paginate(query)
