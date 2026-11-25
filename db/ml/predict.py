import pandas as pd
from pathlib import Path
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


def construir_modelo():
    base_dir = Path(__file__).resolve().parent
    csv_path = base_dir / "tramites_historicos.csv"
    df = pd.read_csv(csv_path)

    X = df[
        [
            "tipo_tramite",
            "area_asignada",
            "documentos_completos",
            "dias_restantes",
            "retraso_previo",
        ]
    ]
    y = df["prioridad"]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore"),
                ["tipo_tramite", "area_asignada"],
            ),
            (
                "num",
                "passthrough",
                ["documentos_completos", "dias_restantes", "retraso_previo"],
            ),
        ]
    )

    modelo = Pipeline(
        steps=[
            ("prep", preprocessor),
            ("clf", DecisionTreeClassifier(random_state=42)),
        ]
    )

    modelo.fit(X, y)
    return modelo


def evaluar_tramite(
    tipo_tramite: str,
    area_asignada: str,
    documentos_completos: int,
    dias_restantes: int,
    retraso_previo: int,
):
    modelo = construir_modelo()

    entrada = pd.DataFrame(
        [
            {
                "tipo_tramite": tipo_tramite,
                "area_asignada": area_asignada,
                "documentos_completos": documentos_completos,
                "dias_restantes": dias_restantes,
                "retraso_previo": retraso_previo,
            }
        ]
    )

    prioridad = modelo.predict(entrada)[0]

    # Cálculo de score de urgencia (0 a 100) y alerta documental/plazo
    score = 40
    if prioridad == "Alta":
        score += 30
    elif prioridad == "Media":
        score += 15

    if documentos_completos == 0:
        score += 15
    if dias_restantes <= 2:
        score += 10
    if retraso_previo == 1:
        score += 5

    score = min(score, 100)

    alertas = []
    if documentos_completos == 0:
        alertas.append("Documentos incompletos")
    if dias_restantes <= 2:
        alertas.append("Plazo por vencer")
    if retraso_previo == 1:
        alertas.append("Antecedente de retraso")

    alerta_texto = " | ".join(alertas) if alertas else "Sin alertas"

    return {
        "prioridad_ml": prioridad,
        "score_urgencia": score,
        "alerta": alerta_texto,
    }


if __name__ == "__main__":
    resultado = evaluar_tramite(
        tipo_tramite="Subdivision de Predios",
        area_asignada="Catastro y Obras",
        documentos_completos=0,
        dias_restantes=3,
        retraso_previo=1,
    )
    print("Resultado de predicción:", resultado)