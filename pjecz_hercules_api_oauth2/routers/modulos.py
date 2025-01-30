"""
Modulos, API v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.authentications import get_current_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..models.modulos import Modulo
from ..models.permisos import Permiso
from ..schemas.modulo import ModuloOut
from ..schemas.usuario import UsuarioInDB

modulos = APIRouter(prefix="/api/v5/modulos", tags=["sistema"])


@modulos.get("", response_model=CustomPage[ModuloOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de modulos"""
    if current_user.permissions.get("MODULOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return paginate(database.query(Modulo).filter_by(estatus="A").order_by(Modulo.nombre))
