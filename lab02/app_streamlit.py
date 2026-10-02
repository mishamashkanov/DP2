"""ЛР №2, дополнительное задание: интерактивный дашборд EDA для набора Adult.

Запуск:  streamlit run app_streamlit.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "adult.csv"
COLUMNS = ["age", "workclass", "fnlwgt", "education", "education_num", "marital_status",
           "occupation", "relationship", "race", "sex", "capital_gain", "capital_loss",
           "hours_per_week", "native_country", "income"]
NUMERIC = ["age", "fnlwgt", "education_num", "capital_gain", "capital_loss", "hours_per_week"]

st.set_page_config(page_title="EDA: Adult", layout="wide")
sns.set_theme(style="whitegrid")


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH, header=None, names=COLUMNS,
                       skipinitialspace=True, na_values="?")


raw = load_data()

# --- Очистка данных
st.sidebar.header("Очистка данных")
na_method = st.sidebar.radio("Пропуски", ["Заполнить модой", "Удалить строки", "Не обрабатывать"])
drop_dups = st.sidebar.checkbox("Удалить дубликаты", value=True)

data = raw.copy()
if na_method == "Заполнить модой":
    for col in ["workclass", "occupation", "native_country"]:
        data[col] = data[col].fillna(data[col].mode()[0])
elif na_method == "Удалить строки":
    data = data.dropna()
if drop_dups:
    data = data.drop_duplicates()

# --- Фильтры
st.sidebar.header("Фильтры")
age = st.sidebar.slider("Возраст", 17, 90, (17, 90))
sex = st.sidebar.multiselect("Пол", ["Male", "Female"], default=["Male", "Female"])
income = st.sidebar.multiselect("Доход", ["<=50K", ">50K"], default=["<=50K", ">50K"])
education = st.sidebar.multiselect("Образование (пусто — все)", sorted(data["education"].unique()))

df = data[data["age"].between(*age) & data["sex"].isin(sex) & data["income"].isin(income)]
if education:
    df = df[df["education"].isin(education)]

st.title("Разведочный анализ набора Adult")
st.write(f"Исходно строк: **{len(raw)}**, после очистки: **{len(data)}**, после фильтров: **{len(df)}**")
if df.empty:
    st.warning("Нет строк под выбранные фильтры.")
    st.stop()

tab_data, tab_dist, tab_corr = st.tabs(["Данные", "Распределения", "Корреляции"])

with tab_data:
    n = st.slider("Сколько строк показать", 5, 100, 10)
    st.dataframe(df.head(n))
    st.write("Пропуски по столбцам:")
    st.dataframe(df.isna().sum().rename("пропусков"))
    st.write("Описательные статистики:")
    st.dataframe(df.describe().T)

with tab_dist:
    col = st.selectbox("Признак", NUMERIC)
    kind = st.radio("Тип графика", ["histplot", "kdeplot", "violinplot", "boxplot"], horizontal=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    if kind == "histplot":
        sns.histplot(df[col], bins=40, ax=ax)
    elif kind == "kdeplot":
        sns.kdeplot(df[col], fill=True, ax=ax)
    elif kind == "violinplot":
        sns.violinplot(y=df[col], inner="quartile", ax=ax)
    else:
        sns.boxplot(y=df[col], ax=ax)
    st.pyplot(fig)

    q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
    iqr = q3 - q1
    outliers = df[(df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)]
    st.write(f"Выбросов по правилу 1.5·IQR: **{len(outliers)}** ({len(outliers) / len(df):.1%})")

with tab_corr:
    corr = df[NUMERIC].corr()
    fig, ax = plt.subplots(figsize=(7, 5.5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, ax=ax)
    st.pyplot(fig)

    x = st.selectbox("Ось X", NUMERIC, index=2)
    y = st.selectbox("Ось Y", NUMERIC, index=5)
    sample = df.sample(min(3000, len(df)), random_state=42)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.scatterplot(data=sample, x=x, y=y, s=12, alpha=0.5, ax=ax)
    ax.set_title(f"r = {corr.loc[x, y]:.2f}")
    st.pyplot(fig)
