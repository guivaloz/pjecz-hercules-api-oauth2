"""
Materias, API v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.authentications import get_current_user
from ..dependencies.database import Session, get_db
from ..dependencies.exceptions import MyAnyError, MyIsDeletedError, MyNotExistsError, MyNotValidParamError
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave
from ..models.materia import Materia
from ..models.permiso import Permiso
from ..schemas.materia import MateriaOut, OneMateriaOut
from ..schemas.usuario import UsuarioInDB

materias = APIRouter(prefix="/api/v1/materias", tags=["materias"])


def get_materia_with_clave(database: Session, clave: str) -> Materia:
    """Consultar una materia por su clave"""
    try:
        clave = safe_clave(clave)
    except ValueError:
        raise MyNotValidParamError("No es válida la clave de la materia")
    materia = database.query(Materia).filter(Materia.clave == clave).first()
    if materia is None:
        raise MyNotExistsError("No existe esa materia")
    if materia.estatus != "A":
        raise MyIsDeletedError("No es activa esa materia, está eliminada")
    return materia


@materias.get("/{clave}", response_model=OneMateriaOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
    clave: str,
):
    """Detalle de un materia a partir de su ID"""
    if current_user.permissions.get("MATERIAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        materia = get_materia_with_clave(database, clave)
    except MyAnyError as error:
        return OneMateriaOut(success=False, message=str(error), errors=[str(error)], data=None)
    return OneMateriaOut(success=True, message="Detalle de un materia", errors=[], data=MateriaOut.model_validate(materia))


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
