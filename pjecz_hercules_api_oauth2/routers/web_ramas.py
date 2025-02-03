"""
Web Ramas
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from ..dependencies.authentications import get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave
from ..models.permisos import Permiso
from ..models.web_ramas import WebRama
from ..schemas.usuarios import UsuarioInDB
from ..schemas.web_ramas import OneWebRamaOut, WebRamaOut

web_ramas = APIRouter(prefix="/api/v5/web_ramas", tags=["sitio web"])


@web_ramas.get("/{clave}", response_model=OneWebRamaOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    clave: str,
):
    """Detalle de una rama web a partir de su clave"""
    if current_user.permissions.get("WEB RAMAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        clave = safe_clave(clave)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válida la clave")
    try:
        web_rama = database.query(WebRama).filter_by(clave=clave).one()
    except (MultipleResultsFound, NoResultFound):
        return OneWebRamaOut(success=False, message="No existe ese rama web")
    if web_rama.estatus != "A":
        return OneWebRamaOut(success=False, message="No está habilitado ese rama web")
    return OneWebRamaOut(success=True, message=f"Detalle de {clave}", data=WebRamaOut.model_validate(web_rama))


@web_ramas.get("", response_model=CustomPage[WebRamaOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de web_ramas"""
    if current_user.permissions.get("WEB RAMAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return paginate(database.query(WebRama).filter_by(estatus="A").order_by(WebRama.clave))
