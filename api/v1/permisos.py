"""
Permisos, API v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from lib.authentications import get_current_user
from lib.database import Session, get_db
from lib.fastapi_pagination_custom_page import CustomPage
from models.permiso import Permiso
from schemas.permiso import PermisoOut
from schemas.usuario import UsuarioInDB

permisos = APIRouter(prefix="/api/v1/permisos", tags=["sistema"])


@permisos.get("", response_model=CustomPage[PermisoOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de permisos"""
    if current_user.permissions.get("PERMISOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    query = database.query(Permiso).filter(Permiso.estatus == "A").order_by(Permiso.id)
    return paginate(query)
