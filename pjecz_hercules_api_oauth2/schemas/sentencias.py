"""
Sentencias, esquemas de pydantic
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class SentenciaRAGIn(BaseModel):
    """Esquema para recibir los datos RAG de la sentencia"""

    id: int
    analisis: dict | None
    sintesis: dict | None
    categorias: dict | None


class SentenciaOut(BaseModel):
    """Esquema para entregar sentencias para paginado"""

    id: int
    distrito_clave: str
    distrito_nombre: str
    distrito_nombre_corto: str
    autoridad_clave: str
    autoridad_descripcion: str
    autoridad_descripcion_corta: str
    materia_clave: str
    materia_nombre: str
    materia_tipo_juicio_id: int
    materia_tipo_juicio_descripcion: str
    sentencia: str
    sentencia_fecha: date
    expediente: str
    expediente_anio: int
    expediente_num: int
    fecha: date
    descripcion: str
    es_perspectiva_genero: bool
    archivo: str
    url: str
    rag_fue_analizado_tiempo: datetime | None = None
    rag_fue_sintetizado_tiempo: datetime | None = None
    rag_fue_categorizado_tiempo: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class SentenciaRAGOut(SentenciaOut):
    """Agregar los campos RAG para cuando se entrega una sentencia"""

    rag_analisis: dict | None = None
    rag_sintesis: dict | None = None
    rag_categorias: dict | None = None


class OneSentenciaOut(BaseModel):
    """Esquema para entregar una sentencia"""

    success: bool
    message: str
    data: SentenciaRAGOut | None = None
