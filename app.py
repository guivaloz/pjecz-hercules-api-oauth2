"""
PJECZ Hércules API OAuth2
"""

from fastapi import FastAPI

from api.v1.modulos import modulos
from api.v1.permisos import permisos
from api.v1.roles import roles
from api.v1.usuarios import usuarios
from api.v1.usuarios_roles import usuarios_roles


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

    # Entregar
    return app
