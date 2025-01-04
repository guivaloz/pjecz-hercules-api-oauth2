"""
PJECZ Hércules API OAuth2
"""
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from api.v1.modulos import modulos
from api.v1.permisos import permisos
from api.v1.roles import roles
from api.v1.usuarios import usuarios
from api.v1.usuarios_roles import usuarios_roles
from lib.authentications import authenticate_user, create_access_token
from lib.database import Session, get_db
from lib.exceptions import MyAnyError
from schemas.usuario import Token


def create_app() -> FastAPI:
    """Crear la aplicación"""

    # FastAPI
    app = FastAPI(
        title="PJECZ Hércules API Oauth2",
        description="API para trabajar con Plataforma Web con autentificación OAuth2",
        docs_url="/docs",
        redoc_url=None,
    )

    # End-points
    app.include_router(modulos)
    app.include_router(permisos)
    app.include_router(roles)
    app.include_router(usuarios)
    app.include_router(usuarios_roles)

    @app.get("/", include_in_schema=False)
    async def root():
        """Mensaje de bienvenida"""
        return {"message": "Bienvenido a PJECZ Hércules API Oauth2"}

    @app.post("/token", response_model=Token)
    async def obtener_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        database: Annotated[Session, Depends(get_db)],
    ):
        """Entregar el token"""
        try:
            usuario = authenticate_user(email=form_data.username, password=form_data.password, database=database)
        except MyAnyError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(error),
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(
            data={"sub": usuario.email},
            expires_delta=timedelta(minutes=60),
        )
        datos = {
            "access_token": access_token,
            "token_type": "bearer",
            "username": usuario.username,
        }
        return Token(**datos)

    # Entregar
    return app
