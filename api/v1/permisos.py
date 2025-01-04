"""
Permisos v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from lib.authentications import get_current_active_user
from lib.database import Session, get_db
from lib.exceptions import MyAnyError, MyIsDeletedError, MyNotExistsError
from models.permiso import Permiso
from schemas.permiso import OnePermisoOut
from schemas.usuario import UsuarioInDB

permisos = APIRouter(prefix="/api/v1/permisos", tags=["sistema"])


def get_permiso(database: Session, permiso_id: int) -> Permiso:
    """Consultar un permiso por su ID"""
    permiso = database.query(Permiso).get(permiso_id)
    if permiso is None:
        raise MyNotExistsError("No existe ese permiso")
    if permiso.estatus != "A":
        raise MyIsDeletedError("No es activo ese permiso, está eliminado")
    return permiso


@permisos.get("/{permiso_id}", response_model=OnePermisoOut)
async def detalle_permiso(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    permiso_id: int,
):
    """Detalle de un permiso a partir de su ID"""
    if current_user.permissions.get("PERMISOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        permiso = get_permiso(database, permiso_id)
    except MyAnyError as error:
        return OnePermisoOut(success=False, message=str(error))
    return OnePermisoOut.model_validate(permiso)
