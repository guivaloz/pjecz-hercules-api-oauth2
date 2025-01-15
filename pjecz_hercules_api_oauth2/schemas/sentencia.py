"""
Sentencias, esquemas de pydantic
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from ..dependencies.schemas_base import OneBaseOut


class SentenciaRAGIn(BaseModel):
    """Esquema para recibir una actualización de la sentencia"""

    id: int
    analisis: dict | None
    sintesis: dict | None
    categorias: dict | None


class SentenciaOut(BaseModel):
    """Esquema para entregar sentencias para paginado"""

    id: int | None = None
    distrito_clave: str | None = None
    autoridad_clave: str | None = None
    materia_nombre: str | None = None
    materia_tipo_juicio_descripcion: str | None = None
    sentencia: str | None = None
    sentencia_fecha: date | None = None
    expediente: str | None = None
    expediente_anio: int | None = None
    expediente_num: int | None = None
    fecha: date | None = None
    descripcion: str | None = None
    es_perspectiva_genero: bool | None = None
    rag_fue_analizado_tiempo: datetime | None = None
    rag_fue_sintetizado_tiempo: datetime | None = None
    rag_fue_categorizado_tiempo: datetime | None = None
    archivo: str | None = None
    url: str | None = None
    model_config = ConfigDict(from_attributes=True)


class SentenciaCompleteOut(SentenciaOut):
    """Esquema para entregar una sentencia en detalle"""

    distrito_id: int | None = None
    distrito_nombre: str | None = None
    distrito_nombre_corto: str | None = None
    autoridad_id: int | None = None
    autoridad_descripcion: str | None = None
    autoridad_descripcion_corta: str | None = None
    materia_id: int | None = None
    materia_tipo_juicio_id: int | None = None
    rag_analisis: dict | None = None
    rag_sintesis: dict | None = None
    rag_categorias: dict | None = None


class OneSentenciaOut(OneBaseOut):
    """Esquema para entregar una sentencia"""

    data: SentenciaCompleteOut | None = None
