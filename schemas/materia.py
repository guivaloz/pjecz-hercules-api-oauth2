"""
Materias, esquemas de pydantic
"""

from pydantic import BaseModel, ConfigDict

from lib.schemas_base import OneBaseOut


class MateriaOut(BaseModel):
    """Esquema para entregar materias"""

    id: int | None = None
    clave: str | None = None
    nombre: str | None = None
    descripcion: str | None = None
    en_sentencias: bool | None = None
    model_config = ConfigDict(from_attributes=True)


class OneMateriaOut(OneBaseOut):
    """Esquema para entregar una materia"""

    data: MateriaOut | None = None
