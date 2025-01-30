"""
Materias
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from ..dependencies.authentications import get_current_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave
from ..models.materia import Materia
from ..models.permiso import Permiso
from ..schemas.materia import MateriaOut, OneMateriaOut
from ..schemas.usuario import UsuarioInDB

materias = APIRouter(prefix="/api/v1/materias", tags=["materias"])


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
        clave = safe_clave(clave)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válida la clave de la materia")
    try:
        materia = database.query(Materia).filter(Materia.clave == clave).one()
    except (MultipleResultsFound, NoResultFound):
        return OneMateriaOut(success=False, message="No existe esa materia")
    if materia.estatus != "A":
        return OneMateriaOut(success=False, message="No es activa esa materia, está eliminada")
    return OneMateriaOut(success=True, message="Detalle de un materia", data=MateriaOut.model_validate(materia))


@materias.get("", response_model=CustomPage[MateriaOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de materias"""
    if current_user.permissions.get("MATERIAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return paginate(database.query(Materia).filter_by(estatus="A").order_by(Materia.clave))
