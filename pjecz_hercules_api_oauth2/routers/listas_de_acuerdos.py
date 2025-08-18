"""
Listas de Acuerdos
"""

import locale
from datetime import date, datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import Annotated
from urllib.parse import unquote, urlparse

import pytz
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from fastapi_pagination.ext.sqlalchemy import paginate
from google.cloud import storage
from hashids import Hashids

from ..config.settings import Settings, get_settings
from ..dependencies.authentications import get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave, safe_string
from ..models.autoridades import Autoridad
from ..models.listas_de_acuerdos import ListaDeAcuerdo
from ..models.permisos import Permiso
from ..schemas.listas_de_acuerdos import ListaDeAcuerdoOut, ListaDeAcuerdoRAGOut, OneListaDeAcuerdoOut
from ..schemas.usuarios import UsuarioInDB

LIMITE_DIAS = 365  # Un año

listas_de_acuerdos = APIRouter(prefix="/api/v5/listas_de_acuerdos", tags=["listas de acuerdos"])


@listas_de_acuerdos.get("/listas_de_acuerdos/visualizar/{lista_de_acuerdo_id}")
async def visualizar(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    lista_de_acuerdo_id: int,
):
    """Visualizar el archivo de una lista de acuerdos en un iframe a partir de su ID"""
    if current_user.permissions.get("LISTAS DE ACUERDOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    lista_de_acuerdo = database.query(ListaDeAcuerdo).get(lista_de_acuerdo_id)
    if lista_de_acuerdo is None:
        return OneListaDeAcuerdoOut(success=False, message="No existe esa lista de acuerdos")
    if lista_de_acuerdo.estatus != "A":
        return OneListaDeAcuerdoOut(success=False, message="No es activa esa lista de acuerdos, está eliminada")

    # Validar que la URL del archivo esté definida
    if lista_de_acuerdo.url is None or lista_de_acuerdo.url.strip() == "":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No está definida la URL del archivo")

    # Definir el blob_name a partir de lista_de_acuerdo.url, porque este contiene la ruta completa
    url_descompuesto = urlparse(lista_de_acuerdo.url)  # Descomponer la URL
    url_sin_dominio = url_descompuesto.path[1:]  # Quitar el primer "/"
    blob_name = unquote("/".join(url_sin_dominio.split("/")[1:]))  # Quitar el primer segmento que es el nombre del bucket

    # Obtener el archivo desde Google Cloud Storage
    storage_client = storage.Client()
    try:
        bucket = storage_client.get_bucket(settings.CLOUD_STORAGE_DEPOSITO_LISTAS_DE_ACUERDOS)
        blob = bucket.get_blob(blob_name)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No se pudo accesar al depósito de archivos: {error}",
        )

    # Validar que el blob existe
    if blob is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el archivo {blob_name} en el depósito {settings.CLOUD_STORAGE_DEPOSITO_LISTAS_DE_ACUERDOS}",
        )

    # Descargar el archivo en memoria
    archivo_contenido = BytesIO()
    try:
        archivo_contenido.write(blob.download_as_bytes())
        archivo_contenido.seek(0)  # Volver al inicio del archivo
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No se pudo descargar el archivo desde el depósito: {error}",
        )

    # Definir el nombre del archivo para la respuesta
    autoridad_clave = lista_de_acuerdo.autoridad.clave
    fecha_str = lista_de_acuerdo.fecha.strftime("%Y-%m-%d")
    archivo_nombre = f"lista_de_acuerdos_{autoridad_clave}_{fecha_str}.pdf"

    # Entregar el archivo
    return StreamingResponse(
        content=archivo_contenido,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={archivo_nombre}"},
    )


@listas_de_acuerdos.get("/{lista_de_acuerdo_id}", response_model=OneListaDeAcuerdoOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    lista_de_acuerdo_id: int,
):
    """Detalle de una lista de acuerdos a partir de su ID"""
    if current_user.permissions.get("LISTAS DE ACUERDOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    lista_de_acuerdo = database.query(ListaDeAcuerdo).get(lista_de_acuerdo_id)
    if lista_de_acuerdo is None:
        return OneListaDeAcuerdoOut(success=False, message="No existe esa lista de acuerdos")
    if lista_de_acuerdo.estatus != "A":
        return OneListaDeAcuerdoOut(success=False, message="No es activa esa lista de acuerdos, está eliminada")
    return OneListaDeAcuerdoOut(
        success=True, message="Detalle de una lista de acuerdos", data=ListaDeAcuerdoRAGOut.model_validate(lista_de_acuerdo)
    )


@listas_de_acuerdos.get("", response_model=CustomPage[ListaDeAcuerdoOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    autoridad_clave: str = "",
    fecha: date | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
):
    """Paginado de listas_de_acuerdos"""
    if current_user.permissions.get("LISTAS DE ACUERDOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(ListaDeAcuerdo)
    if autoridad_clave:
        try:
            autoridad_clave = safe_clave(autoridad_clave)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válida la clave")
        consulta = consulta.join(Autoridad).filter(Autoridad.clave == autoridad_clave).filter(Autoridad.estatus == "A")
    if fecha is not None:
        consulta = consulta.filter(ListaDeAcuerdo.fecha == fecha)
    else:
        if fecha_desde is not None:
            consulta = consulta.filter(ListaDeAcuerdo.fecha >= fecha_desde)
        if fecha_hasta is not None:
            consulta = consulta.filter(ListaDeAcuerdo.fecha <= fecha_hasta)
    return paginate(consulta.filter(ListaDeAcuerdo.estatus == "A").order_by(ListaDeAcuerdo.fecha.desc()))


@listas_de_acuerdos.post("", response_model=OneListaDeAcuerdoOut)
async def insertar(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    archivo: UploadFile = File(...),
    autoridad_clave: str = Form(...),
    fecha: str = Form(...),
    descripcion: str = Form(...),
):
    """Insertar una lista de acuerdos"""
    if current_user.permissions.get("LISTAS DE ACUERDOS", 0) < Permiso.CREAR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    # Validar la clave de la autoridad
    try:
        autoridad_clave = safe_clave(autoridad_clave)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válida la clave de la autoridad")
    autoridad = database.query(Autoridad).filter(Autoridad.clave == autoridad_clave).filter(Autoridad.estatus == "A").first()
    if autoridad is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No existe esa autoridad o no está activa")

    # Google App Engine usa tiempo universal, sin esta correccion las fechas de la noche cambian al dia siguiente
    local_tz = pytz.timezone(settings.TZ)
    ahora_utc = datetime.now(pytz.UTC)
    ahora_local = ahora_utc.astimezone(local_tz)

    # Determinar el datetime limite para la fecha al pasado
    fecha_limite = ahora_local + timedelta(days=-LIMITE_DIAS)

    # Validar la fecha
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válida la fecha, debe ser YYYY-MM-DD")
    if not fecha_limite <= datetime(year=fecha_dt.year, month=fecha_dt.month, day=fecha_dt.day, tzinfo=local_tz) <= ahora_local:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válida la fecha porque está fuera del rango")

    # Validar la descripción
    descripcion = safe_string(descripcion)
    if len(descripcion) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válida la descripción, no puede estar vacía")

    # Validar que el archivo sea un PDF
    if archivo.filename is None or not archivo.filename.endswith(".pdf"):
        return OneListaDeAcuerdoOut(success=False, message="El archivo no es un PDF")
    if archivo.content_type != "application/pdf":
        return OneListaDeAcuerdoOut(success=False, message="El archivo no es un PDF")

    # Validar que el archivo no tenga un tamaño nulo
    archivo_pdf_tamanio = int(archivo.size) if archivo.size is not None else 0
    if archivo_pdf_tamanio == 0:
        return OneListaDeAcuerdoOut(success=False, message="El archivo no tiene un tamaño válido")

    # Validar que el archivo no exceda el tamaño máximo permitido de 10MB
    if archivo_pdf_tamanio > 10 * 1024 * 1024:
        return OneListaDeAcuerdoOut(success=False, message="El archivo excede el tamaño máximo permitido")

    # Consultar si existe una lista de acuerdos con la misma fecha y autoridad
    anterior_lista_de_acuerdo = (
        database.query(ListaDeAcuerdo)
        .filter(ListaDeAcuerdo.autoridad_id == autoridad.id)
        .filter(ListaDeAcuerdo.fecha == fecha_dt)
        .filter(ListaDeAcuerdo.estatus == "A")
        .first()
    )

    # Insertar el registro de la lista de acuerdos para que tenga un ID
    nueva_lista_de_acuerdo = ListaDeAcuerdo(
        autoridad_id=autoridad.id,
        fecha=fecha,
        descripcion=descripcion,
        estatus="B",
    )
    database.add(nueva_lista_de_acuerdo)
    database.commit()

    # Cargar el archivo en memoria
    archivo_en_memoria = archivo.file.read()

    # Definir la materia para el nombre del archivo
    materia = safe_string(autoridad.materia.nombre)

    # Definir la cadena de hash para nombre del archivo
    hashids = Hashids(salt=settings.SALT, min_length=8)
    cadena = hashids.encode(nueva_lista_de_acuerdo.id)

    # Definir la fecha para el nombre del archivo
    fecha_str = fecha_dt.strftime("%Y-%m-%d")

    # Definir el nombre del archivo: YYYY-MM-DD-LISTA-DE-ACUERDOS-MATERIA-CADENA.pdf
    archivo_nombre = f"{fecha_str}-LISTA-DE-ACUERDOS-{materia}-{cadena}.pdf"

    # Definir el directorio base para la ruta del archivo
    base_dir = autoridad.directorio_listas_de_acuerdos

    # Definir la ruta del archivo en el bucket: distrito_clave/autoridad_clave/año/mes_nombre/
    locale.setlocale(locale.LC_TIME, "es_MX.utf8")
    anio_str = fecha_dt.strftime("%Y")
    mes_str = fecha_dt.strftime("%B")
    archivo_ruta = str(Path(base_dir, anio_str, mes_str, archivo_nombre))

    # Subir el archivo PDF a Google Cloud Storage
    storage_client = storage.Client()
    try:
        bucket = storage_client.get_bucket(settings.CLOUD_STORAGE_DEPOSITO_LISTAS_DE_ACUERDOS)
        blob = bucket.blob(archivo_ruta)
        blob.upload_from_string(archivo_en_memoria, content_type="application/pdf")
    except Exception as error:
        # Eliminar el registro de la lista de acuerdos porque no se pudo subir el archivo
        nueva_lista_de_acuerdo.delete()
        return OneListaDeAcuerdoOut(
            success=False,
            message=f"No se pudo subir el archivo a Google Cloud Storage: {error}",
        )

    # Actualizar la lista de acuerdos con el nombre del archivo y la URL
    nueva_lista_de_acuerdo.archivo = archivo_nombre
    nueva_lista_de_acuerdo.url = blob.public_url
    database.add(nueva_lista_de_acuerdo)
    database.commit()

    # Si la hubo, esta debe cambiar a estatus "B" (eliminada)
    if anterior_lista_de_acuerdo is not None:
        anterior_lista_de_acuerdo.estatus = "B"
        database.add(anterior_lista_de_acuerdo)
        database.commit()

    # Entregar
    return OneListaDeAcuerdoOut(
        success=True,
        message="Se ha insertado la lista de acuerdos",
        data=ListaDeAcuerdoRAGOut.model_validate(nueva_lista_de_acuerdo),
    )
