"""
Usuarios-Roles, API v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from lib.authentications import get_current_user
from lib.database import Session, get_db
from lib.fastapi_pagination_custom_page import CustomPage
from models.permiso import Permiso
from models.usuario_rol import UsuarioRol
from schemas.usuario import UsuarioInDB
from schemas.usuario_rol import UsuarioRolOut

usuarios_roles = APIRouter(prefix="/api/v1/usuarios_roles", tags=["sistema"])


@usuarios_roles.get("", response_model=CustomPage[UsuarioRolOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de usuarios_roles"""
    if current_user.permissions.get("USUARIOS ROLES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    query = database.query(UsuarioRol).filter(UsuarioRol.estatus == "A").order_by(UsuarioRol.id)
    return paginate(query)
