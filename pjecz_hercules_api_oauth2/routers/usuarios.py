"""
Usuarios
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.authentications import get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave, safe_email
from ..models.autoridades import Autoridad
from ..models.permisos import Permiso
from ..models.usuarios import Usuario
from ..schemas.usuarios import OneUsuarioOut, UsuarioInDB, UsuarioOut

usuarios = APIRouter(prefix="/api/v5/usuarios", tags=["sistema"])


@usuarios.get("/{email}", response_model=OneUsuarioOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    email: str,
):
    """Detalle de un usuario a partir de su e-mail"""
    if current_user.permissions.get("USUARIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        email = safe_email(email)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válido el e-mail")
    usuario = database.query(Usuario).filter(Usuario.email == email).first()
    if usuario is None:
        return OneUsuarioOut(success=False, message="No existe ese usuario")
    if usuario.estatus != "A":
        return OneUsuarioOut(success=False, message="No es activo ese usuario, está eliminado")
    return OneUsuarioOut(success=True, message="Detalle de un usuario", data=UsuarioOut.model_validate(usuario))


@usuarios.get("", response_model=CustomPage[UsuarioOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    autoridad_clave: str = None,
):
    """Paginado de usuarios"""
    if current_user.permissions.get("USUARIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(Usuario)
    if autoridad_clave is not None:
        try:
            clave = safe_clave(autoridad_clave)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válido el e-mail")
        consulta = consulta.join(Autoridad).filter(Autoridad.clave == clave).filter(Autoridad.estatus == "A")
    return paginate(consulta.filter(Usuario.estatus == "A").order_by(Usuario.email))
