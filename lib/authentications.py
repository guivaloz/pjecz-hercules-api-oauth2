"""
Authentications
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from config.settings import Settings, get_settings
from lib.database import Session, get_db
from lib.exceptions import MyAnyError, MyAuthenticationError, MyIsDeletedError, MyNotExistsError, MyNotValidParamError
from lib.safe_string import safe_email
from models.usuario import Usuario
from schemas.usuario import UsuarioInDB

PASSWORD_REGEXP = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,24}$"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_usuario_with_email(database: Session, usuario_email: str) -> UsuarioInDB:
    """Consultar un usuario por su email"""
    try:
        email = safe_email(usuario_email)
    except ValueError as error:
        raise MyNotValidParamError("El email no es válido") from error
    usuario = database.query(Usuario).filter_by(email=email).first()
    if usuario is None:
        raise MyNotExistsError("No existe ese usuario")
    if usuario.estatus != "A":
        raise MyIsDeletedError("No es activo ese usuario, está eliminado")
    datos = {
        "id": usuario.id,
        "email": usuario.email,
        "nombres": usuario.nombres,
        "apellido_paterno": usuario.apellido_paterno,
        "apellido_materno": usuario.apellido_materno,
        "puesto": usuario.puesto,
        "username": usuario.email,
        "permissions": usuario.permissions,
        "hashed_password": usuario.contrasena,
        "disabled": usuario.estatus != "A",
    }
    return UsuarioInDB(**datos)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Validar la contraseña"""
    if hashed_password == "":
        raise MyNotValidParamError("No tiene definida su contraseña")
    if re.match(PASSWORD_REGEXP, plain_password) is None:
        raise MyNotValidParamError("La contraseña no es valida")
    pwd_context = CryptContext(schemes=["pbkdf2_sha256", "des_crypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(email: str, password: str, database: Session = Depends(get_db)) -> UsuarioInDB:
    """Autentificar al usuario"""
    try:
        usuario = get_usuario_with_email(database, email)
    except MyAnyError as error:
        raise error
    if not verify_password(password, usuario.hashed_password):
        raise MyAuthenticationError("La contraseña es incorrecta")
    return usuario


async def create_access_token(
    settings: Annotated[Settings, Depends(get_settings)],
    data: dict,
    expires_delta: timedelta,
):
    """Crear un token"""
    payload = {
        "username": data["username"],
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    return jwt.encode(
        payload=payload,
        key=settings.secret_key,
        algorithm="HS256",
    )


async def get_current_user(
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    token: str,
) -> UsuarioInDB:
    """Obtener el usuario a partir del token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.secret_key,
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError as error:
        raise credentials_exception
    username: str = payload.get("username")
    usuario = get_usuario_with_email(database, username)
    return usuario


async def get_current_active_user(
    current_user: UsuarioInDB = Depends(get_current_user),
) -> UsuarioInDB:
    """Obtener el usuario activo"""
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No está autorizado porque su cuenta está deshabilitada",
        )
    return current_user
