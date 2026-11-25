import pandas as pd
from pathlib import Path
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parent
csv_path = BASE_DIR / "tramites_historicos.csv"

df = pd.read_csv(csv_path)

X = df[["tipo_tramite", "area_asignada", "documentos_completos", "dias_restantes", "retraso_previo"]]
y = df["prioridad"]

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["tipo_tramite", "area_asignada"]),
        ("num", "passthrough", ["documentos_completos", "dias_restantes", "retraso_previo"]),
    ]
)

modelo = Pipeline(
    steps=[
        ("prep", preprocessor),
        ("clf", DecisionTreeClassifier(random_state=42)),
    ]
)

modelo.fit(X, y)

# Prueba rápida con un trámite nuevo de la Municipalidad de Yau
nuevo_tramite = pd.DataFrame(
    [
        {
            "tipo_tramite": "Licencia de Funcionamiento",
            "area_asignada": "Desarrollo Economico",
            "documentos_completos": 0,
            "dias_restantes": 2,
            "retraso_previo": 1,
        }
    ]
)

pred = modelo.predict(nuevo_tramite)[0]
alerta = "ALERTA: Documentos incompletos o plazo crítico" if (0 == 0 or 2 <= 2) else "Sin alerta"
print("Prioridad predicha:", pred, "|", alerta)