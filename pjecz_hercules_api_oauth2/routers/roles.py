"""
Roles, API v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.authentications import get_current_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..models.permiso import Permiso
from ..models.rol import Rol
from ..schemas.rol import RolOut
from ..schemas.usuario import UsuarioInDB

roles = APIRouter(prefix="/api/v1/roles", tags=["sistema"])


@roles.get("", response_model=CustomPage[RolOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de roles"""
    if current_user.permissions.get("ROLES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    query = database.query(Rol).filter(Rol.estatus == "A").order_by(Rol.nombre)
    return paginate(query)
