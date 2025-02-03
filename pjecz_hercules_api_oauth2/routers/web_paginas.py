"""
Web Páginas
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
from ..models.web_paginas import WebPagina
from ..models.web_ramas import WebRama
from ..schemas.usuarios import UsuarioInDB
from ..schemas.web_paginas import OneWebPaginaOut, WebPaginaOut

web_paginas = APIRouter(prefix="/api/v5/web_paginas", tags=["sitio web"])


@web_paginas.get("/{clave}", response_model=OneWebPaginaOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    clave: str,
):
    """Detalle de una página web a partir de su clave"""
    if current_user.permissions.get("WEB PAGINAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        clave = safe_clave(clave)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válida la clave")
    try:
        web_pagina = database.query(WebPagina).filter_by(clave=clave).one()
    except (MultipleResultsFound, NoResultFound):
        return OneWebPaginaOut(success=False, message="No existe esa página web")
    if web_pagina.estatus != "A":
        return OneWebPaginaOut(success=False, message="No está habilitada esa página web")
    return OneWebPaginaOut(success=True, message=f"Detalle de {clave}", data=WebPaginaOut.model_validate(web_pagina))


@web_paginas.get("", response_model=CustomPage[WebPaginaOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    web_rama_clave: str = None,
):
    """Paginado de páginas web"""
    if current_user.permissions.get("WEB PAGINAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(WebPagina)
    if web_rama_clave is not None:
        try:
            web_rama_clave = safe_clave(web_rama_clave)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válida la clave")
        consulta = consulta.join(WebRama).filter(WebRama.clave == web_rama_clave).filter(WebRama.estatus == "A")
    return paginate(consulta.filter(WebPagina.estatus == "A").order_by(WebPagina.clave))
