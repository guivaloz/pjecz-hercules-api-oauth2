"""
Autoridades, esquemas de pydantic
"""

from pydantic import BaseModel, ConfigDict

from ..dependencies.schemas_base import OneBaseOut


class AutoridadOut(BaseModel):
    """Esquema para entregar autoridades para paginado"""

    id: int | None = None
    clave: str | None = None
    descripcion: str | None = None
    descripcion_corta: str | None = None
    distrito_id: int | None = None
    distrito_clave: str | None = None
    distrito_nombre_corto: str | None = None
    directorio_edictos: str | None = None
    directorio_glosas: str | None = None
    directorio_listas_de_acuerdos: str | None = None
    directorio_sentencias: str | None = None
    es_extinto: bool | None = None
    es_cemasc: bool | None = None
    es_defensoria: bool | None = None
    es_jurisdiccional: bool | None = None
    es_notaria: bool | None = None
    es_organo_especializado: bool | None = None
    organo_jurisdiccional: str | None = None
    model_config = ConfigDict(from_attributes=True)


class OneAutoridadOut(OneBaseOut):
    """Esquema para entregar una autoridad"""

    data: AutoridadOut | None = None
