"""
PJECZ Hércules API OAuth2
"""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import add_pagination

from .dependencies.authentications import TOKEN_EXPIRES_SECONDS, authenticate_user, encode_token
from .dependencies.database import Session, get_db
from .dependencies.exceptions import MyAnyError
from .routers.autoridades import autoridades
from .routers.distritos import distritos
from .routers.materias import materias
from .routers.materias_tipos_juicios import materias_tipos_juicios
from .routers.modulos import modulos
from .routers.permisos import permisos
from .routers.roles import roles
from .routers.sentencias import sentencias
from .routers.usuarios import usuarios
from .routers.usuarios_roles import usuarios_roles
from .schemas.usuario import Token
from .settings import Settings, get_settings

# FastAPI
app = FastAPI(
    title="PJECZ Hércules API Oauth2",
    description="API para trabajar con la base de datos Plataforma Web con autentificación OAuth2",
    docs_url="/docs",
    redoc_url=None,
)

# Rutas
app.include_router(autoridades)
app.include_router(distritos)
app.include_router(materias)
app.include_router(materias_tipos_juicios)
app.include_router(modulos)
app.include_router(permisos)
app.include_router(roles)
app.include_router(sentencias)
app.include_router(usuarios)
app.include_router(usuarios_roles)

# Paginación
add_pagination(app)


@app.get("/")
async def root() -> dict:
    """Mensaje de bienvenida"""
    return {"message": "API para trabajar con la base de datos Plataforma Web con autentificación OAuth2"}


@app.post("/token", response_model=Token)
async def login(
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Login para recibir el formulario OAuth2PasswordRequestForm y entregar el token"""
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
