"""
Edictos, esquemas de pydantic
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class EdictoRAGIn(BaseModel):
    """Esquema para recibir los datos RAG del edicto"""

    id: int
    analisis: dict | None
    sintesis: dict | None
    categorias: dict | None


class EdictoOut(BaseModel):
    """Esquema para entregar edictos para paginado"""

    id: int
    creado: datetime
    distrito_clave: str
    distrito_nombre: str
    autoridad_clave: str
    autoridad_descripcion: str
    fecha: date
    descripcion: str
    expediente: str
    numero_publicacion: str
    archivo: str
    url: str
    es_declaracion_de_ausencia: bool = False
    rag_fue_analizado_tiempo: datetime | None = None
    rag_fue_sintetizado_tiempo: datetime | None = None
    rag_fue_categorizado_tiempo: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class EdictoRAGOut(EdictoOut):
    """Agregar los campos RAG para cuando se entrega un edicto"""

    rag_analisis: dict | None = None
    rag_sintesis: dict | None = None
    rag_categorias: dict | None = None


class OneEdictoOut(BaseModel):
    """Esquema para entregar un edicto"""

    success: bool
    message: str
    data: EdictoRAGOut | None = None
