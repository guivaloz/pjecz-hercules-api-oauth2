"""
Autoridades, API v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from api.v1.distritos import get_distrito_with_clave
from api.v1.materias import get_materia_with_clave
from lib.authentications import get_current_user
from lib.database import Session, get_db
from lib.exceptions import MyAnyError, MyIsDeletedError, MyNotExistsError, MyNotValidParamError
from lib.fastapi_pagination_custom_page import CustomPage
from lib.safe_string import safe_clave
from models.autoridad import Autoridad
from models.distrito import Distrito
from models.materia import Materia
from models.permiso import Permiso
from schemas.autoridad import AutoridadOut, OneAutoridadOut
from schemas.usuario import UsuarioInDB

autoridades = APIRouter(prefix="/api/v1/autoridades", tags=["autoridades"])


def get_autoridad_with_clave(database: Session, clave: str) -> Autoridad:
    """Consultar una autoridad por su clave"""
    try:
        clave = safe_clave(clave)
    except ValueError:
        raise MyNotValidParamError("No es válida la clave de la autoridad")
    autoridad = database.query(Autoridad).filter(Autoridad.clave == clave).first()
    if autoridad is None:
        raise MyNotExistsError("No existe esa autoridad")
    if autoridad.estatus != "A":
        raise MyIsDeletedError("No es activa ese autoridad, está eliminada")
    return autoridad


@autoridades.get("/{clave}", response_model=OneAutoridadOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
    clave: str,
):
    """Detalle de un autoridad a partir de su ID"""
    if current_user.permissions.get("AUTORIDADES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        autoridad = get_autoridad_with_clave(database, clave)
    except MyAnyError as error:
        return OneAutoridadOut(success=False, message=str(error), errors=[str(error)], data=None)
    return OneAutoridadOut(
        success=True, message="Detalle de una autoridad", errors=[], data=AutoridadOut.model_validate(autoridad)
    )


@autoridades.get("", response_model=CustomPage[AutoridadOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
    distrito_clave: str = None,
    materia_clave: str = None,
    es_jurisdiccional: bool = None,
    es_notaria: bool = None,
):
    """Paginado de autoridades"""
    if current_user.permissions.get("AUTORIDADES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    query = database.query(Autoridad)
    if distrito_clave is not None:
        try:
            distrito = get_distrito_with_clave(database, distrito_clave)
        except MyAnyError as error:
            return CustomPage(success=False, message=str(error), errors=[str(error)], data=None)
        query = query.join(Distrito).filter(Distrito.clave == distrito.clave)
    if materia_clave is not None:
        try:
            materia = get_materia_with_clave(database, materia_clave)
        except MyAnyError as error:
            return CustomPage(success=False, message=str(error), errors=[str(error)], data=None)
        query = query.join(Materia).filter(Materia.clave == materia.clave)
    if es_jurisdiccional is not None:
        query = query.filter(Autoridad.es_jurisdiccional == es_jurisdiccional)
    if es_notaria is not None:
        query = query.filter(Autoridad.es_notaria == es_notaria)
    query = query.filter(Autoridad.estatus == "A").order_by(Autoridad.clave)
    return paginate(query)
