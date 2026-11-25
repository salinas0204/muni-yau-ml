import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector

# Permitir importar predict.py desde db/ml
ML_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ML_DIR ))
from predict import evaluar_tramite

app = FastAPI(title="API Municipalidad Provincial de Yau")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3307,
    "user": "root",
    "password": "1234",
    "database": "muni_yau_db",
}


class TramiteEntrada(BaseModel):
    dni: str
    nombre_completo: str
    correo: str = ""
    telefono: str = ""
    tipo_tramite: str
    area_asignada: str
    documentos_completos: int
    dias_restantes: int
    retraso_previo: int


@app.post("/api/tramites")
def registrar_tramite(data: TramiteEntrada):
    pred = evaluar_tramite(
        tipo_tramite=data.tipo_tramite,
        area_asignada=data.area_asignada,
        documentos_completos=data.documentos_completos,
        dias_restantes=data.dias_restantes,
        retraso_previo=data.retraso_previo,
    )

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 1. Registrar o actualizar ciudadano
        cursor.execute(
            """
            INSERT INTO ciudadanos (dni, nombre_completo, correo, telefono)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                nombre_completo = VALUES(nombre_completo),
                correo = VALUES(correo),
                telefono = VALUES(telefono)
            """,
            (data.dni, data.nombre_completo, data.correo, data.telefono),
        )
        cursor.execute("SELECT id FROM ciudadanos WHERE dni = %s", (data.dni,))
        ciudadano_id = cursor.fetchone()[0]

        # 2. Registrar trámite con la prioridad calculada por ML
        cursor.execute(
            """
            INSERT INTO tramites (
                ciudadano_id, tipo_tramite, area_asignada,
                documentos_completos, estado, prioridad_ml, score_urgencia
            )
            VALUES (%s, %s, %s, %s, 'Pendiente', %s, %s)
            """,
            (
                ciudadano_id,
                data.tipo_tramite,
                data.area_asignada,
                data.documentos_completos,
                pred["prioridad_ml"],
                pred["score_urgencia"],
            ),
        )
        tramite_id = cursor.lastrowid

        # 3. Guardar notificación automática en historial_notificaciones
        mensaje_notif = (
            f"Trámite #{tramite_id} ({data.tipo_tramite}) registrado. "
            f"Prioridad: {pred['prioridad_ml']} | {pred['alerta']}"
        )
        cursor.execute(
            """
            INSERT INTO historial_notificaciones (tramite_id, canal, mensaje)
            VALUES (%s, 'Sistema Web / SMS', %s)
            """,
            (tramite_id, mensaje_notif),
        )

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "mensaje": "Trámite registrado y evaluado correctamente",
            "tramite_id": tramite_id,
            "evaluacion_ml": pred,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tramites")
def listar_tramites():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                t.id, c.dni, c.nombre_completo, t.tipo_tramite,
                t.area_asignada, t.documentos_completos, t.estado,
                t.prioridad_ml, t.score_urgencia, t.fecha_registro
            FROM tramites t
            JOIN ciudadanos c ON t.ciudadano_id = c.id
            ORDER BY t.score_urgencia DESC, t.fecha_registro DESC
            """
        )
        filas = cursor.fetchall()
        cursor.close()
        conn.close()
        return filas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))