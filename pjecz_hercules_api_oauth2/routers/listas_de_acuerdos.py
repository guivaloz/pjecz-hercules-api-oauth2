"""
Listas de Acuerdos
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
from ..models.listas_de_acuerdos import ListaDeAcuerdo
from ..models.permisos import Permiso
from ..schemas.listas_de_acuerdos import ListaDeAcuerdoOut, ListaDeAcuerdoRAGOut, OneListaDeAcuerdoOut
from ..schemas.usuarios import UsuarioInDB

listas_de_acuerdos = APIRouter(prefix="/api/v5/listas_de_acuerdos", tags=["listas de acuerdos"])


@listas_de_acuerdos.get("/{lista_de_acuerdo_id}", response_model=OneListaDeAcuerdoOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    lista_de_acuerdo_id: int,
):
    """Detalle de una lista de acuerdos a partir de su ID"""
    if current_user.permissions.get("LISTAS DE ACUERDOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    lista_de_acuerdo = database.query(ListaDeAcuerdo).get(lista_de_acuerdo_id)
    if lista_de_acuerdo is None:
        return OneListaDeAcuerdoOut(success=False, message="No existe esa lista de acuerdos")
    if lista_de_acuerdo.estatus != "A":
        return OneListaDeAcuerdoOut(success=False, message="No es activa esa lista de acuerdos, está eliminada")
    return OneListaDeAcuerdoOut(
        success=True, message="Detalle de una lista de acuerdos", data=ListaDeAcuerdoRAGOut.model_validate(lista_de_acuerdo)
    )


@listas_de_acuerdos.get("", response_model=CustomPage[ListaDeAcuerdoOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    autoridad_clave: str = None,
    creado: date = None,
    creado_desde: date = None,
    creado_hasta: date = None,
):
    """Paginado de listas_de_acuerdos"""
    if current_user.permissions.get("LISTAS DE ACUERDOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(ListaDeAcuerdo)
    if autoridad_clave is not None:
        try:
            autoridad_clave = safe_clave(autoridad_clave)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válida la clave")
        consulta = consulta.join(Autoridad).filter(Autoridad.clave == autoridad_clave).filter(Autoridad.estatus == "A")
    if creado is not None:
        consulta = consulta.filter(ListaDeAcuerdo.creado >= datetime(creado.year, creado.month, creado.day, 0, 0, 0))
        consulta = consulta.filter(ListaDeAcuerdo.creado <= datetime(creado.year, creado.month, creado.day, 23, 59, 59))
    else:
        if creado_desde is not None:
            consulta = consulta.filter(
                ListaDeAcuerdo.creado >= datetime(creado_desde.year, creado_desde.month, creado_desde.day, 0, 0, 0)
            )
        if creado_hasta is not None:
            consulta = consulta.filter(
                ListaDeAcuerdo.creado <= datetime(creado_hasta.year, creado_hasta.month, creado_hasta.day, 23, 59, 59)
            )
    return paginate(consulta.filter(ListaDeAcuerdo.estatus == "A").order_by(ListaDeAcuerdo.id.desc()))
