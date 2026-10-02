"""ЛР №4, дополнительное задание: интерактивное сравнение классификаторов.

Лучшие модели (GridSearchCV) и выборки сохраняются в блокноте lab04_classification.ipynb.

Запуск:  streamlit run app_streamlit.py
"""
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from sklearn.base import clone
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score, classification_report,
                             f1_score, precision_score, recall_score)

BASE = Path(__file__).parent

st.set_page_config(page_title="Классификаторы", layout="wide")


@st.cache_resource
def load_bundle():
    return joblib.load(BASE / "models.joblib")


def hyperparams(name, p):
    # Элементы управления для основных гиперпараметров; начальные значения — найденные GridSearchCV
    if name == "kNN":
        return {"n_neighbors": st.sidebar.slider("n_neighbors", 1, 50, p["n_neighbors"]),
                "weights": st.sidebar.selectbox("weights", ["uniform", "distance"],
                                                ["uniform", "distance"].index(p["weights"])),
                "p": st.sidebar.radio("p (1 — манхэттенская, 2 — евклидова)", [1, 2], [1, 2].index(p["p"]))}
    if name == "Decision Tree":
        return {"max_depth": st.sidebar.slider("max_depth", 1, 20, p["max_depth"] or 20),
                "min_samples_leaf": st.sidebar.slider("min_samples_leaf", 1, 50, p["min_samples_leaf"]),
                "criterion": st.sidebar.selectbox("criterion", ["gini", "entropy"],
                                                  ["gini", "entropy"].index(p["criterion"]))}
    if name == "SVM":
        kernels = ["linear", "rbf", "poly"]
        return {"kernel": st.sidebar.selectbox("kernel", kernels, kernels.index(p["kernel"])),
                "C": st.sidebar.select_slider("C", [0.01, 0.1, 1.0, 10.0, 100.0], float(p["C"]))}
    layers = {"(32,)": (32,), "(64,)": (64,), "(64, 32)": (64, 32), "(128, 64)": (128, 64)}
    return {"hidden_layer_sizes": layers[st.sidebar.selectbox("hidden_layer_sizes", list(layers),
                                                               list(layers.values()).index(p["hidden_layer_sizes"]))],
            "activation": st.sidebar.selectbox("activation", ["relu", "tanh"],
                                               ["relu", "tanh"].index(p["activation"])),
            "alpha": st.sidebar.select_slider("alpha", [1e-4, 1e-3, 1e-2, 0.1, 1.0, 10.0], float(p["alpha"]))}


bundle = load_bundle()

st.sidebar.header("Настройки")
dataset = st.sidebar.selectbox("Набор данных", list(bundle))
models = bundle[dataset]["models"]
name = st.sidebar.selectbox("Классификатор", list(models))
X_train, X_test, y_train, y_test = bundle[dataset]["split"]
labels = bundle[dataset]["labels"]

st.sidebar.subheader("Гиперпараметры")
best = models[name]
params = hyperparams(name, best.named_steps["clf"].get_params())

# Переобучение пайплайна (предобработка + модель) с выбранными гиперпараметрами
model = clone(best).set_params(**{f"clf__{k}": v for k, v in params.items()})
with st.spinner("Обучение модели..."):
    model.fit(X_train, y_train)
pred = model.predict(X_test)

st.title(f"{name} — {dataset}")
metrics = pd.DataFrame({
    "Текущие параметры": [accuracy_score(y_test, pred), precision_score(y_test, pred, average="macro"),
                          recall_score(y_test, pred, average="macro"), f1_score(y_test, pred, average="macro")],
}, index=["Accuracy", "Precision (macro)", "Recall (macro)", "F1-score (macro)"])
best_pred = best.predict(X_test)
metrics["Лучшие (GridSearchCV)"] = [accuracy_score(y_test, best_pred),
                                    precision_score(y_test, best_pred, average="macro"),
                                    recall_score(y_test, best_pred, average="macro"),
                                    f1_score(y_test, best_pred, average="macro")]

col1, col2 = st.columns(2)
with col1:
    st.subheader("Матрица неточностей (тест)")
    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay.from_predictions(y_test, pred, display_labels=labels,
                                            cmap="Blues", colorbar=False, ax=ax)
    st.pyplot(fig)
with col2:
    st.subheader("Метрики на тестовой выборке")
    st.dataframe(metrics.style.format("{:.4f}"))
    st.subheader("Classification report")
    report = classification_report(y_test, pred, target_names=labels, output_dict=True)
    st.dataframe(pd.DataFrame(report).T.style.format("{:.4f}"))
