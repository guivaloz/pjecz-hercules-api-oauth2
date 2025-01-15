"""
Distritos, API v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.authentications import get_current_user
from ..dependencies.database import Session, get_db
from ..dependencies.exceptions import MyAnyError, MyIsDeletedError, MyNotExistsError, MyNotValidParamError
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave
from ..models.distrito import Distrito
from ..models.permiso import Permiso
from ..schemas.distrito import DistritoOut, OneDistritoOut
from ..schemas.usuario import UsuarioInDB

distritos = APIRouter(prefix="/api/v1/distritos", tags=["distritos"])


def get_distrito_with_clave(database: Session, clave: str) -> Distrito:
    """Consultar una distrito por su clave"""
    try:
        clave = safe_clave(clave)
    except ValueError:
        raise MyNotValidParamError("No es válida la clave de la distrito")
    distrito = database.query(Distrito).filter(Distrito.clave == clave).first()
    if distrito is None:
        raise MyNotExistsError("No existe esa distrito")
    if distrito.estatus != "A":
        raise MyIsDeletedError("No es activa esa distrito, está eliminada")
    return distrito


@distritos.get("/{clave}", response_model=OneDistritoOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
    clave: str,
):
    """Detalle de un distrito a partir de su ID"""
    if current_user.permissions.get("AUTORIDADES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        distrito = get_distrito_with_clave(database, clave)
    except MyAnyError as error:
        return OneDistritoOut(success=False, message=str(error), errors=[str(error)], data=None)
    return OneDistritoOut(success=True, message="Detalle de un distrito", errors=[], data=DistritoOut.model_validate(distrito))


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
