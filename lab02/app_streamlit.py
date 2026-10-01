"""Лабораторная работа №2, дополнительное задание.

Интерактивный дашборд разведочного анализа набора данных Adult (Census Income).

Запуск:
    conda activate lab1_terminal
    streamlit run app_streamlit.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "adult.csv"
COLUMNS = [
    "age", "workclass", "fnlwgt", "education", "education_num", "marital_status",
    "occupation", "relationship", "race", "sex", "capital_gain", "capital_loss",
    "hours_per_week", "native_country", "income",
]
NUMERIC = ["age", "fnlwgt", "education_num", "capital_gain", "capital_loss", "hours_per_week"]
CATEGORICAL = [c for c in COLUMNS if c not in NUMERIC]
NA_COLUMNS = ["workclass", "occupation", "native_country"]
INCOME_PALETTE = {"<=50K": "tab:blue", ">50K": "tab:orange"}

st.set_page_config(page_title="EDA: Adult Census Income", layout="wide")
sns.set_theme(style="whitegrid")


@st.cache_data
def load_raw() -> pd.DataFrame:
    # Те же параметры чтения, что и в блокноте: пробелы после запятых, пропуски — «?»
    return pd.read_csv(DATA_PATH, header=None, names=COLUMNS,
                       skipinitialspace=True, na_values="?")


@st.cache_data
def clean(raw: pd.DataFrame, na_strategy: str, drop_dups: bool) -> pd.DataFrame:
    df = raw.copy()
    if na_strategy == "Категория Unknown":
        df[NA_COLUMNS] = df[NA_COLUMNS].fillna("Unknown")
    elif na_strategy == "Заполнение модой":
        for col in NA_COLUMNS:
            df[col] = df[col].fillna(df[col].mode()[0])
    elif na_strategy == "Удаление строк":
        df = df.dropna()
    if drop_dups:
        df = df.drop_duplicates()
    df = df.reset_index(drop=True)
    # income оставлен строкой: с категориальным hue seaborn 0.13 + pandas 3 путает цвета
    cat_cols = [c for c in CATEGORICAL if c != "income"]
    df[cat_cols] = df[cat_cols].astype("category")
    df["income_gt50k"] = (df["income"] == ">50K").astype(int)
    return df


def iqr_outliers(df: pd.DataFrame) -> pd.DataFrame:
    num = df[NUMERIC]
    q1, q3 = num.quantile(0.25), num.quantile(0.75)
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    mask = (num < low) | (num > high)
    return pd.DataFrame({"нижняя граница": low, "верхняя граница": high,
                         "выбросов": mask.sum(), "доля, %": (mask.mean() * 100).round(2)})


def multiselect_all(label: str, series: pd.Series) -> list:
    options = sorted(series.dropna().unique().tolist())
    return st.sidebar.multiselect(label, options, default=options)


# ---------------------------------------------------------------- боковая панель
raw = load_raw()

st.sidebar.header("Очистка данных")
na_strategy = st.sidebar.radio(
    "Обработка пропусков (workclass, occupation, native_country)",
    ["Категория Unknown", "Заполнение модой", "Удаление строк", "Оставить NaN"])
drop_dups = st.sidebar.checkbox("Удалить дубликаты", value=True)
data = clean(raw, na_strategy, drop_dups)

st.sidebar.header("Фильтры")
age_range = st.sidebar.slider("Возраст", int(data["age"].min()), int(data["age"].max()),
                              (int(data["age"].min()), int(data["age"].max())))
hours_range = st.sidebar.slider("Часов работы в неделю", int(data["hours_per_week"].min()),
                                int(data["hours_per_week"].max()),
                                (int(data["hours_per_week"].min()), int(data["hours_per_week"].max())))
sex_sel = multiselect_all("Пол", data["sex"])
income_sel = multiselect_all("Доход", data["income"])
workclass_sel = multiselect_all("Вид занятости", data["workclass"])
education_sel = multiselect_all("Образование", data["education"])

mask = (data["age"].between(*age_range)
        & data["hours_per_week"].between(*hours_range)
        & data["sex"].isin(sex_sel)
        & data["income"].isin(income_sel)
        & data["education"].isin(education_sel)
        & (data["workclass"].isin(workclass_sel) | data["workclass"].isna()))
df = data[mask]

# ---------------------------------------------------------------- шапка
st.title("Разведочный анализ: Adult (Census Income)")
st.caption("Лабораторная работа №2 — интерактивная версия анализа набора данных Adult (UCI).")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Строк в исходном файле", f"{len(raw):,}".replace(",", " "))
c2.metric("После очистки", f"{len(data):,}".replace(",", " "), delta=len(data) - len(raw))
c3.metric("После фильтров", f"{len(df):,}".replace(",", " "))
c4.metric("Доля дохода >50K", f"{df['income_gt50k'].mean():.1%}" if len(df) else "—")

if df.empty:
    st.warning("Под выбранные фильтры не попала ни одна строка — ослабьте условия в боковой панели.")
    st.stop()

tab_data, tab_stats, tab_dist, tab_cat, tab_corr = st.tabs(
    ["Данные", "Статистика", "Распределения", "Категории", "Корреляции"])

# ---------------------------------------------------------------- вкладка «Данные»
with tab_data:
    st.subheader("Таблица данных")
    n_show = st.slider("Сколько строк показать", 5, 200, 20, step=5)
    position = st.radio("Какие строки", ["Первые", "Последние", "Случайные"], horizontal=True)
    if position == "Первые":
        st.dataframe(df.head(n_show), width="stretch")
    elif position == "Последние":
        st.dataframe(df.tail(n_show), width="stretch")
    else:
        st.dataframe(df.sample(min(n_show, len(df)), random_state=0), width="stretch")

    st.write(f"Размерность: **{df.shape[0]} строк × {df.shape[1]} столбцов**")
    st.subheader("Структура столбцов")
    info = pd.DataFrame({
        "тип": df.dtypes.astype(str),
        "непустых": df.notna().sum(),
        "пропусков": df.isna().sum(),
        "уникальных": df.nunique(),
    })
    st.dataframe(info, width="stretch")

    st.subheader("Очистка: до и после")
    before_after = pd.DataFrame({
        "исходные данные": [len(raw), int(raw.isna().sum().sum()), int(raw.duplicated().sum())],
        "после очистки": [len(data), int(data[COLUMNS].isna().sum().sum()),
                          int(data[COLUMNS].duplicated().sum())],
    }, index=["строк", "пропусков (NaN)", "дубликатов"])
    st.dataframe(before_after, width="stretch")

# ---------------------------------------------------------------- вкладка «Статистика»
with tab_stats:
    st.subheader("Числовые признаки")
    num = df[NUMERIC]
    st.dataframe(pd.DataFrame({
        "среднее": num.mean(), "медиана": num.median(), "СКО": num.std(),
        "min": num.min(), "Q1": num.quantile(0.25), "Q3": num.quantile(0.75),
        "max": num.max(), "асимметрия": num.skew(),
    }).round(2), width="stretch")

    st.subheader("Категориальные признаки")
    cat = df[CATEGORICAL].describe().T
    cat.columns = ["непустых", "уникальных", "мода", "частота моды"]
    st.dataframe(cat, width="stretch")

# ---------------------------------------------------------------- вкладка «Распределения»
with tab_dist:
    left, right = st.columns([1, 3])
    with left:
        feature = st.selectbox("Числовой признак", NUMERIC, index=0)
        kind = st.radio("Тип графика", ["Гистограмма", "KDE", "Violin", "Boxplot"])
        split = st.checkbox("Разбить по доходу", value=True)
        bins = st.slider("Число интервалов", 10, 100, 40) if kind == "Гистограмма" else None
    hue = "income" if split else None
    palette = INCOME_PALETTE if split else None

    fig, ax = plt.subplots(figsize=(9, 4.8))
    if kind == "Гистограмма":
        sns.histplot(data=df, x=feature, hue=hue, bins=bins, stat="density",
                     common_norm=False, palette=palette, alpha=0.5, ax=ax)
    elif kind == "KDE":
        sns.kdeplot(data=df, x=feature, hue=hue, fill=True, common_norm=False,
                    palette=palette, alpha=0.35, ax=ax)
    elif kind == "Violin":
        sns.violinplot(data=df, x=hue, y=feature, hue=hue, inner="quartile",
                       palette=palette, legend=False, ax=ax)
    else:
        sns.boxplot(data=df, x=hue, y=feature, hue=hue, palette=palette, legend=False,
                    flierprops={"marker": "o", "markersize": 3, "alpha": 0.4}, ax=ax)
    ax.set_title(f"{feature}: {kind.lower()}")
    with right:
        st.pyplot(fig)
    plt.close(fig)

    st.subheader("Выбросы по правилу 1.5·IQR")
    st.dataframe(iqr_outliers(df).sort_values("выбросов", ascending=False),
                 width="stretch")

# ---------------------------------------------------------------- вкладка «Категории»
with tab_cat:
    cat_feature = st.selectbox("Категориальный признак",
                               [c for c in CATEGORICAL if c != "income"], index=1)
    top_n = st.slider("Показать уровней (самых частых)", 3, 41, 12)
    counts = df[cat_feature].value_counts().head(top_n)
    order = counts.index.astype(str).tolist()
    sub = df[df[cat_feature].isin(counts.index)].copy()
    sub[cat_feature] = sub[cat_feature].astype(str)

    col_a, col_b = st.columns(2)
    fig, ax = plt.subplots(figsize=(7, 0.35 * len(order) + 1.5))
    sns.countplot(data=sub, y=cat_feature, hue="income", order=order,
                  palette=INCOME_PALETTE, ax=ax)
    ax.set_title(f"Частоты: {cat_feature}")
    ax.set_ylabel("")
    col_a.pyplot(fig)
    plt.close(fig)

    share = sub.groupby(cat_feature)["income_gt50k"].mean().reindex(order).sort_values()
    fig, ax = plt.subplots(figsize=(7, 0.35 * len(order) + 1.5))
    ax.barh(share.index, share.values, color="tab:orange")
    ax.axvline(df["income_gt50k"].mean(), color="black", ls="--", lw=1, label="в среднем")
    ax.set_xlim(0, 1)
    ax.set_title(f"Доля дохода >50K: {cat_feature}")
    ax.legend(loc="lower right")
    col_b.pyplot(fig)
    plt.close(fig)

    st.dataframe(pd.DataFrame({"число людей": counts,
                               "доля, %": (counts / len(df) * 100).round(2),
                               "доля >50K": share.reindex(order).values.round(3)}),
                 width="stretch")

# ---------------------------------------------------------------- вкладка «Корреляции»
with tab_corr:
    corr_df = df[NUMERIC].copy()
    corr_df["sex_male"] = (df["sex"] == "Male").astype(int)
    corr_df["income_gt50k"] = df["income_gt50k"]
    method = st.radio("Метод корреляции", ["pearson", "spearman"], horizontal=True)
    corr = corr_df.corr(method=method)

    fig, ax = plt.subplots(figsize=(8, 6.5))
    sns.heatmap(corr, mask=np.triu(np.ones_like(corr, dtype=bool), k=1), annot=True,
                fmt=".2f", cmap="coolwarm", center=0, vmin=-1, vmax=1, square=True,
                linewidths=0.5, ax=ax)
    ax.grid(False)
    ax.set_title(f"Матрица корреляции ({method})")
    heat_col, _ = st.columns([3, 2])
    heat_col.pyplot(fig)
    plt.close(fig)

    st.subheader("Диаграмма рассеяния")
    s1, s2, s3 = st.columns(3)
    x = s1.selectbox("Ось X", NUMERIC, index=0)
    y = s2.selectbox("Ось Y", NUMERIC, index=5)
    n_points = s3.slider("Точек (случайная выборка)", 500, 10000, 3000, step=500)
    sample = df.sample(min(n_points, len(df)), random_state=42)

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.scatterplot(data=sample, x=x, y=y, hue="income", palette=INCOME_PALETTE,
                    s=14, alpha=0.5, ax=ax)
    ax.set_title(f"{x} vs {y}: r = {corr.loc[x, y]:.2f}")
    st.pyplot(fig)
    plt.close(fig)
