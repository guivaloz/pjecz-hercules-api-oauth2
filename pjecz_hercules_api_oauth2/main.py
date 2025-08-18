"""
PJECZ Hércules API OAuth2
"""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import add_pagination

from .config.settings import Settings, get_settings
from .dependencies.authentications import TOKEN_EXPIRES_SECONDS, authenticate_user, encode_token
from .dependencies.database import Session, get_db
from .dependencies.exceptions import MyAnyError
from .routers.autoridades import autoridades
from .routers.distritos import distritos
from .routers.edictos import edictos
from .routers.listas_de_acuerdos import listas_de_acuerdos
from .routers.materias import materias
from .routers.materias_tipos_juicios import materias_tipos_juicios
from .routers.modulos import modulos
from .routers.permisos import permisos
from .routers.roles import roles
from .routers.sentencias import sentencias
from .routers.usuarios import usuarios
from .routers.usuarios_roles import usuarios_roles
from .schemas.usuarios import Token

# FastAPI
app = FastAPI(
    title="PJECZ API OAuth2 de Plataforma Web",
    description="Esta API es usada por los sistemas y aplicaciones. No es para cuentas personales.",
    docs_url="/docs",
    redoc_url=None,
)

# CORSMiddleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS.split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["*"],
)

# Rutas
app.include_router(autoridades)
app.include_router(distritos)
app.include_router(edictos)
app.include_router(listas_de_acuerdos)
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
    return {"message": "Bienvenido a Hércules API OAuth2 del Poder Judicial del Estado de Coahuila de Zaragoza"}


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
