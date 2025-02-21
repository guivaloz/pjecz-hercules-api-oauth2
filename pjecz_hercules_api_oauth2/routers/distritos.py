"""
Distritos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from ..dependencies.authentications import get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave
from ..models.distritos import Distrito
from ..models.permisos import Permiso
from ..schemas.distritos import DistritoOut, OneDistritoOut
from ..schemas.usuarios import UsuarioInDB

distritos = APIRouter(prefix="/api/v5/distritos", tags=["distritos"])


@distritos.get("/{clave}", response_model=OneDistritoOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    clave: str,
):
    """Detalle de un distrito a partir de su ID"""
    if current_user.permissions.get("AUTORIDADES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        clave = safe_clave(clave)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válida la clave")
    try:
        distrito = database.query(Distrito).filter(Distrito.clave == clave).one()
    except (MultipleResultsFound, NoResultFound):
        return OneDistritoOut(success=False, message="No existe distrito")
    if distrito.estatus != "A":
        return OneDistritoOut(success=False, message="No es activo ese distrito, está eliminado")
    return OneDistritoOut(success=True, message="Detalle de un distrito", data=DistritoOut.model_validate(distrito))


@distritos.get("", response_model=CustomPage[DistritoOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    es_distrito: bool = None,
    es_jurisdiccional: bool = None,
):
    """Paginado de distritos"""
    if current_user.permissions.get("DISTRITOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(Distrito)
    if es_distrito is not None:
        consulta = consulta.filter_by(es_distrito=es_distrito)
    if es_jurisdiccional is not None:
        consulta = consulta.filter_by(es_jurisdiccional=es_jurisdiccional)
    return paginate(consulta.filter_by(estatus="A").order_by(Distrito.clave))
