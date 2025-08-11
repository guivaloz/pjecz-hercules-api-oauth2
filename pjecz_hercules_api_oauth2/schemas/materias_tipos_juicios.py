"""
Materias Tipos de Juicios, esquemas de pydantic
"""

from pydantic import BaseModel, ConfigDict


class MateriaTipoJuicioOut(BaseModel):
    """Esquema para entregar tipos de juicios"""

    id: int
    materia_clave: str
    materia_nombre: str
    descripcion: str
    model_config = ConfigDict(from_attributes=True)


class OneMateriaTipoJuicioOut(BaseModel):
    """Esquema para entregar un tipo de juicio"""

    success: bool
    message: str
    data: MateriaTipoJuicioOut | None = None
