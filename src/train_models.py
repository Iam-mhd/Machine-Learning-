# src/train_models.py

from pathlib import Path
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline

# Détection automatique de la racine du projet
BASE = Path(__file__).resolve().parent.parent

# 1. Chargement des données
df = pd.read_csv(BASE / "data" / "heart_disease.csv")
X = df.drop("target", axis=1)
y = df["target"]

# 2. Train/Test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# 3. Pré‑traitement
cat_cols = ["cp","restecg","slope","ca","thal","sex","fbs","exang"]
num_cols = ["age","trestbps","chol","thalach","oldpeak"]

preprocessor = ColumnTransformer([
    ("num", StandardScaler(), num_cols),
    ("cat", OneHotEncoder(drop="first", sparse_output=False), cat_cols)
])

# 4. Pipeline complet
pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression(max_iter=1000))
])

# 5. Entraînement
pipeline.fit(X_train, y_train)

# 6. Sérialisation
output_path = BASE / "backend" / "models" / "heart_pipeline_lr.pkl"
joblib.dump(pipeline, output_path)
print(f"Pipeline enregistré dans {output_path}")
# 7. Sauvegarde des données d'entraînement et de test
X_train.to_csv(BASE / "data" / "X_train.csv", index=False)
y_train.to_csv(BASE / "data" / "y_train.csv", index=False)          