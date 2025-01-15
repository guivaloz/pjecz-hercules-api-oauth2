"""
Materias Tipos de Juicios, esquemas de pydantic
"""

from pydantic import BaseModel, ConfigDict

from ..dependencies.schemas_base import OneBaseOut


class MateriaTipoJuicioOut(BaseModel):
    """Esquema para entregar tipos de juicios"""

    id: int | None = None
    materia_id: int | None = None
    materia_clave: str | None = None
    materia_nombre: str | None = None
    descripcion: str | None = None
    model_config = ConfigDict(from_attributes=True)


class OneMateriaTipoJuicioOut(OneBaseOut):
    """Esquema para entregar un tipo de juicio"""

    data: MateriaTipoJuicioOut | None = None
