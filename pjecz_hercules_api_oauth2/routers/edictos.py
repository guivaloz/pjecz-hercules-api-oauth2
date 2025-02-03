"""
Edictos
"""

from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.authentications import get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave
from ..models.autoridades import Autoridad
from ..models.edictos import Edicto
from ..models.permisos import Permiso
from ..schemas.edictos import EdictoOut, EdictoRAGOut, OneEdictoOut
from ..schemas.usuarios import UsuarioInDB

edictos = APIRouter(prefix="/api/v5/edictos", tags=["edictos"])


@edictos.get("/{edicto_id}", response_model=OneEdictoOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    edicto_id: int,
):
    """Detalle de una edicto a partir de su ID"""
    if current_user.permissions.get("EDICTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    edicto = database.query(Edicto).get(edicto_id)
    if edicto is None:
        return OneEdictoOut(success=False, message="No existe esa edicto")
    if edicto.estatus != "A":
        return OneEdictoOut(success=False, message="No es activa esa edicto, está eliminada")
    return OneEdictoOut(success=True, message="Detalle de una edicto", data=EdictoRAGOut.model_validate(edicto))


@edictos.get("", response_model=CustomPage[EdictoOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    autoridad_clave: str = None,
    creado: date = None,
    creado_desde: date = None,
    creado_hasta: date = None,
):
    """Paginado de edictos"""
    if current_user.permissions.get("EDICTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(Edicto)
    if autoridad_clave is not None:
        try:
            autoridad_clave = safe_clave(autoridad_clave)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válida la clave")
        consulta = consulta.join(Autoridad).filter(Autoridad.clave == autoridad_clave).filter(Autoridad.estatus == "A")
    if creado is not None:
        consulta = consulta.filter(Edicto.creado >= datetime(creado.year, creado.month, creado.day, 0, 0, 0))
        consulta = consulta.filter(Edicto.creado <= datetime(creado.year, creado.month, creado.day, 23, 59, 59))
    else:
        if creado_desde is not None:
            consulta = consulta.filter(
                Edicto.creado >= datetime(creado_desde.year, creado_desde.month, creado_desde.day, 0, 0, 0)
            )
        if creado_hasta is not None:
            consulta = consulta.filter(
                Edicto.creado <= datetime(creado_hasta.year, creado_hasta.month, creado_hasta.day, 23, 59, 59)
            )
    return paginate(consulta.filter(Edicto.estatus == "A").order_by(Edicto.id.desc()))
