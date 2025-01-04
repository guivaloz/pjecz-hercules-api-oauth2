"""
PJECZ Hércules API OAuth2
"""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from api.v1.modulos import modulos
from api.v1.permisos import permisos
from api.v1.roles import roles
from api.v1.usuarios import usuarios
from api.v1.usuarios_roles import usuarios_roles
from config.settings import Settings, get_settings
from lib.authentications import TOKEN_EXPIRES_SECONDS, authenticate_user, encode_token
from lib.database import Session, get_db
from lib.exceptions import MyAnyError
from schemas.usuario import Token


def create_app() -> FastAPI:
    """Crear la aplicación"""

    # FastAPI
    app = FastAPI(
        title="PJECZ Hércules API Oauth2",
        description="API para trabajar con la base de datos Plataforma Web con autentificación OAuth2",
        docs_url="/docs",
        redoc_url=None,
    )

    # End-points
    app.include_router(modulos)
    app.include_router(permisos)
    app.include_router(roles)
    app.include_router(usuarios)
    app.include_router(usuarios_roles)

    @app.get("/")
    async def root():
        """Mensaje de bienvenida"""
        return {"message": "API para trabajar con la base de datos Plataforma Web con autentificación OAuth2"}

    @app.post("/token", response_model=Token)
    async def login(
        database: Annotated[Session, Depends(get_db)],
        settings: Annotated[Settings, Depends(get_settings)],
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    ) -> Token:
        """Login para enviar el formulario OAuth2PasswordRequestForm y entregar el token"""
        try:
            usuario = authenticate_user(username=form_data.username, password=form_data.password, database=database)
        except MyAnyError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(error),
                headers={"WWW-Authenticate": "Bearer"},
            )
        return Token(
            access_token=encode_token(settings=settings, usuario=usuario),
            expires_in=TOKEN_EXPIRES_SECONDS,
            token_type="bearer",
            username=usuario.email,
        )

    # Entregar
    return app
