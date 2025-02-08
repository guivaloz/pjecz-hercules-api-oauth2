"""
Listas de Acuerdos, esquemas de pydantic
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from ..dependencies.schemas_base import OneBaseOut


class ListaDeAcuerdoRAGIn(BaseModel):
    """Esquema para recibir los datos RAG de la lista de acuerdos"""

    id: int
    analisis: dict | None
    sintesis: dict | None
    categorias: dict | None


class ListaDeAcuerdoOut(BaseModel):
    """Esquema para entregar listas de acuerdos para paginado"""

    id: int
    distrito_clave: str
    distrito_nombre: str
    distrito_nombre_corto: str
    autoridad_clave: str
    autoridad_descripcion: str
    autoridad_descripcion_corta: str
    fecha: date
    descripcion: str
    archivo: str
    url: str
    rag_fue_analizado_tiempo: datetime | None = None
    rag_fue_sintetizado_tiempo: datetime | None = None
    rag_fue_categorizado_tiempo: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class ListaDeAcuerdoRAGOut(ListaDeAcuerdoOut):
    """Agregar los campos RAG para cuando se entrega una lista de acuerdos"""

    rag_analisis: dict | None = None
    rag_sintesis: dict | None = None
    rag_categorias: dict | None = None


class OneListaDeAcuerdoOut(OneBaseOut):
    """Esquema para entregar una lista de acuerdos"""

    data: ListaDeAcuerdoRAGOut | None = None
