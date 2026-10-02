"""ЛР №3, дополнительное задание: симулятор прогноза продаж по бюджетам на рекламу.

Модель обучается и сохраняется в блокноте lab03_linear_regression.ipynb (эксперимент В).

Запуск:  streamlit run app_streamlit.py
"""
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

BASE = Path(__file__).parent
FEATURES = ["TV", "radio", "newspaper"]

st.set_page_config(page_title="Прогноз продаж", layout="wide")


@st.cache_resource
def load_model():
    return joblib.load(BASE / "advertising_model.joblib")


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(BASE / "data" / "Advertising.csv", index_col=0)


model = load_model()
data = load_data()

# --- Ввод бюджетов
st.sidebar.header("Бюджеты на рекламу, тыс. $")
budget = {f: st.sidebar.slider(f, 0.0, float(np.ceil(data[f].max())), float(data[f].median()), 0.5)
          for f in FEATURES}

x = pd.DataFrame([budget])
prediction = model.predict(x)[0]

st.title("Прогноз продаж по затратам на рекламу")
terms = " + ".join(f"{w:.4f}·{f}" for f, w in zip(FEATURES, model.coef_))
st.markdown(f"Уравнение регрессии: **sales = {model.intercept_:.4f} + {terms}**")
st.metric("Прогноз продаж, тыс. единиц", f"{prediction:.2f}")

# --- График: прогноз в зависимости от бюджета выбранного канала при остальных фиксированных
channel = st.radio("Канал по оси X", FEATURES, horizontal=True)
grid = pd.DataFrame({f: np.full(100, budget[f]) for f in FEATURES})
grid[channel] = np.linspace(0, data[channel].max(), 100)

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.scatter(data[channel], data["sales"], s=15, alpha=0.4, label="исходные данные")
ax.plot(grid[channel], model.predict(grid), color="tab:red", lw=2,
        label="прогноз при текущих бюджетах остальных каналов")
ax.scatter(budget[channel], prediction, color="black", s=120, zorder=3, label="текущий прогноз")
ax.set_xlabel(f"{channel}, тыс. $")
ax.set_ylabel("sales, тыс. единиц")
ax.legend()
st.pyplot(fig)
