"""
Web Páginas, modelos
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..dependencies.database import Base
from ..dependencies.universal_mixin import UniversalMixin


class WebPagina(Base, UniversalMixin):
    """WebPagina"""

    ESTADOS = {
        "BORRADOR": "BORRADOR",
        "PUBLICAR": "PUBLICAR",
        "ARCHIVAR": "ARCHIVAR",
    }

    # Nombre de la tabla
    __tablename__ = "web_paginas"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Clave foránea
    web_rama_id: Mapped[int] = mapped_column(ForeignKey("web_ramas.id"))
    web_rama: Mapped["WebRama"] = relationship(back_populates="web_paginas")

    # Columnas
    clave: Mapped[str] = mapped_column(String(16), unique=True)
    titulo: Mapped[str] = mapped_column(String(256))
    resumen: Mapped[Optional[str]] = mapped_column(String(1024))
    ruta: Mapped[str] = mapped_column(String(256))
    fecha_modificacion: Mapped[date]
    responsable: Mapped[Optional[str]] = mapped_column(String(256))
    etiquetas: Mapped[Optional[str]] = mapped_column(String(256))
    vista_previa: Mapped[Optional[str]] = mapped_column(String(256))
    contenido: Mapped[str] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(Enum(*ESTADOS, name="web_paginas_estados", native_enum=False), index=True)
    tiempo_publicar: Mapped[Optional[datetime]]
    tiempo_archivar: Mapped[Optional[datetime]]

    def __repr__(self):
        """Representación"""
        return f"<WebPagina clave {self.clave}>"
