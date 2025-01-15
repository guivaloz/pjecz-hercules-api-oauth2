"""
Materias Tipos de Juicios, API v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.authentications import get_current_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..models.materia_tipo_juicio import MateriaTipoJuicio
from ..models.permiso import Permiso
from ..schemas.materia_tipo_juicio import MateriaTipoJuicioOut
from ..schemas.usuario import UsuarioInDB

materias_tipos_juicios = APIRouter(prefix="/api/v1/materias_tipos_juicios", tags=["materias"])


@materias_tipos_juicios.get("", response_model=CustomPage[MateriaTipoJuicioOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de materias_tipos_juicios"""
    if current_user.permissions.get("MATERIAS TIPOS JUICIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    query = database.query(MateriaTipoJuicio).filter(MateriaTipoJuicio.estatus == "A").order_by(MateriaTipoJuicio.id)
    return paginate(query)
