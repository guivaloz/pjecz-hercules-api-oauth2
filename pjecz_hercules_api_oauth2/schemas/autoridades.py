"""
Autoridades, esquemas de pydantic
"""

from pydantic import BaseModel, ConfigDict


class AutoridadOut(BaseModel):
    """Esquema para entregar autoridades para paginado"""

    clave: str
    descripcion: str
    distrito_clave: str
    materia_clave: str
    materia_nombre: str
    directorio_edictos: str
    directorio_glosas: str
    directorio_listas_de_acuerdos: str
    directorio_sentencias: str
    es_extinto: bool
    es_cemasc: bool
    es_defensoria: bool
    es_jurisdiccional: bool
    es_notaria: bool
    es_organo_especializado: bool
    organo_jurisdiccional: str
    model_config = ConfigDict(from_attributes=True)


class OneAutoridadOut(BaseModel):
    """Esquema para entregar una autoridad"""

    success: bool
    message: str
    data: AutoridadOut | None = None
