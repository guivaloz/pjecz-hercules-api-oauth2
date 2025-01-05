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
from schemas.usuario import Token, UsuarioInDB

ALGORITHM = "HS256"
PASSWORD_REGEXP = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,24}$"
TOKEN_EXPIRES_SECONDS = 3600  # 1 hora

# Autentificar con OAuth2 y solicitar token en @app.post("/token", response_model=Token)
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


def authenticate_user(username: str, password: str, database: Session = Depends(get_db)) -> UsuarioInDB:
    """Autentificar al usuario"""
    try:
        usuario = get_usuario_with_email(database, username)
    except MyAnyError as error:
        raise error
    if not verify_password(password, usuario.hashed_password):
        raise MyAuthenticationError("La contraseña es incorrecta")
    return usuario


def encode_token(settings: Settings, usuario: UsuarioInDB) -> str:
    """Crear el token"""
    expiration_dt = datetime.now(timezone.utc) + timedelta(seconds=TOKEN_EXPIRES_SECONDS)
    expires_at = expiration_dt.timestamp()
    payload = {"username": usuario.email, "expires_at": expires_at}
    return jwt.encode(payload=payload, key=settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str, settings: Settings) -> dict:
    """Decodificar el token"""
    try:
        payload = jwt.decode(jwt=token, key=settings.secret_key, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError as error:
        raise MyAuthenticationError("No es válido el token") from error
    if "expires_at" not in payload or payload["expires_at"] < datetime.now(timezone.utc).timestamp():
        raise MyAuthenticationError("Ha caducado el token")
    return payload


async def get_current_user(
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> UsuarioInDB:
    """Obtener el usuario a partir del token"""
    try:
        decoded_token = decode_token(token, settings)
        usuario = get_usuario_with_email(database, decoded_token["username"])
    except MyAnyError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return usuario
