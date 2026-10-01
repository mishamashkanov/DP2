#лабораторные работы

Репозиторий с лабораторными работами по курсу машинного обучения и анализа данных.
Каждая работа оформлена как блокнот Jupyter (`.ipynb`), сохранённый **вместе с результатами
вычислений и графиками** — то есть открывается для просмотра прямо на GitHub, без запуска.

## Среда выполнения

| Компонент | Значение |
|---|---|
| Дистрибутив | Anaconda Distribution (Anaconda3-2026.07-1, Windows x64) |
| Python | 3.12 |
| Основные библиотеки | `numpy`, `pandas`, `matplotlib`, `seaborn`, `scikit-learn`, `scipy`, `streamlit` |
| Локальная среда | Anaconda Jupyter Notebook (изолированные окружения conda) |
| Облачная среда | Google Colaboratory |

Работы выполняются преимущественно в **Anaconda Jupyter Notebook**; часть работ —
в **Google Colab** (такие блокноты помечены суффиксом `_colab`).

## Структура репозитория

```
.
├── README.md                     — описание проекта (этот файл)
├── .gitignore                    — исключения для Git
├── start-jupyter.bat             — запуск Jupyter Notebook в окружении проекта
│
├── lab01/                        — ЛР №1. Настройка среды и виртуальные окружения
│   ├── lab01_anaconda.ipynb      — части 1 и 3: Anaconda, окружения, эксперимент на данных
│   ├── lab01_colab.ipynb         — часть 2: Google Colab, аппаратные ускорители (GPU/TPU)
│   ├── make_report.py            — сборка отчёта .docx из блокнотов
│   ├── data/                     — наборы данных, использованные в работе
│   │   ├── iris.csv              — Fisher's Iris, 150 объектов
│   │   └── titanic.csv           — Titanic, 891 объект
│   ├── images/                   — скриншоты графического интерфейса
│   └── logs/                     — протоколы работы с conda в терминале
│       ├── conda_create_lab1_terminal.log
│       ├── conda_list_lab1_terminal.txt
│       └── conda_env_list.txt
│
└── lab02/                        — ЛР №2. Разведочный анализ данных (EDA)
    ├── lab02_eda.ipynb           — EDA двух наборов данных: аудит, очистка, распределения, выбросы, корреляции
    ├── app_streamlit.py          — доп. задание: интерактивный дашборд Streamlit (набор Adult)
    ├── data/                     — наборы данных, использованные в работе
    │   ├── winequality-red.csv   — Wine Quality (red), 1599 объектов, UCI
    │   └── adult.csv             — Adult (Census Income), 32561 объект, UCI
    ├── images/                   — скриншоты дашборда Streamlit
    └── logs/
        └── conda_install_streamlit.log — протокол установки streamlit через терминал
```

Единый принцип организации: **одна лабораторная работа — один каталог** `labNN/`,
внутри которого лежат блокноты, использованные наборы данных (`data/`), вспомогательные
изображения (`images/`) и текстовые протоколы (`logs/`).

## Лабораторные работы

### ЛР №1. Настройка среды разработки и управление виртуальными окружениями

**Цель:** освоение развёртывания изолированных сред разработки, управления пакетами через
графический интерфейс и терминал в Anaconda и Google Colaboratory, первичный аудит
аппаратных ресурсов.

| Часть | Содержание | Блокнот |
|---|---|---|
| 1 | Установка Anaconda; создание и активация окружений через GUI (Navigator) и терминал (`conda create` / `conda activate`); установка библиотек обоими способами; программный аудит версий; полный список пакетов | [`lab01/lab01_anaconda.ipynb`](lab01/lab01_anaconda.ipynb) |
| 2 | Google Colab: проверка предустановленных пакетов, `!pip install`, переключение вычислителей CPU/GPU/TPU, вывод сведений об оборудовании (`nvidia-smi`, `torch.cuda`, `jax`, `torch_xla`) | [`lab01/lab01_colab.ipynb`](lab01/lab01_colab.ipynb) |
| 3 | Экспериментальная проверка окружения на двух наборах данных: загрузка через `pandas` и построение графиков | [`lab01/lab01_anaconda.ipynb`](lab01/lab01_anaconda.ipynb) |

**Использованные наборы данных:** Fisher's Iris (150 объектов, 4 числовых признака,
3 класса) и Titanic (891 объект, смешанные типы признаков, пропущенные значения).

**Созданные виртуальные окружения:**

| Окружение | Способ создания | Назначение |
|---|---|---|
| `lab1_gui` | Anaconda Navigator (графический интерфейс) | демонстрация работы с окружениями через GUI |
| `lab1_terminal` | Anaconda Prompt, `conda create` | окружение, в котором выполнен блокнот работы |

### ЛР №2. Разведочный анализ данных

**Цель:** изучение основных методов разведочного анализа данных, выявление скрытых
закономерностей, поиск аномалий, визуализация распределений признаков и подготовка данных
к последующему моделированию.

**Среда:** Anaconda Jupyter Notebook, окружение `lab1_terminal`.

| Часть | Содержание | Файл |
|---|---|---|
| 1 | Подбор двух новых наборов данных (UCI): числовой Wine Quality и смешанный Adult с категориальными признаками | [`lab02/lab02_eda.ipynb`](lab02/lab02_eda.ipynb) |
| 2 | Для каждого набора: первичный аудит (`head`/`tail`, размерность, `.info()`, проверка типов); описательные статистики; обработка пропусков и дубликатов; гистограммы, KDE, violin, ECDF, boxplot; выбросы по правилу IQR; матрица корреляции и heatmap; scatterplot и pairplot; аналитические выводы | [`lab02/lab02_eda.ipynb`](lab02/lab02_eda.ipynb) |
| 3 | Доп. задание: дашборд Streamlit для набора Adult — выбор способа очистки, фильтры, выбор признаков и типов графиков, динамические таблицы | [`lab02/app_streamlit.py`](lab02/app_streamlit.py) |

**Использованные наборы данных:**

| Набор | Объектов × признаков | Особенности | Результаты очистки |
|---|---|---|---|
| [Wine Quality (red)](https://archive.ics.uci.edu/dataset/186/wine+quality) | 1599 × 12 | все признаки числовые, целевой `quality` — порядковый (3…8) | пропусков нет; удалено 240 дубликатов |
| [Adult (Census Income)](https://archive.ics.uci.edu/dataset/2/adult) | 32561 × 15 | 9 категориальных признаков, пропуски закодированы `?` | пропуски → категория `Unknown` / мода; удалено 24 дубликата |

Запуск дашборда:

```bat
conda activate lab1_terminal
cd lab02
streamlit run app_streamlit.py
```

## Воспроизведение окружения

Создание окружения со всеми необходимыми пакетами:

```bat
conda create -n lab1_terminal python=3.12 numpy pandas matplotlib seaborn scikit-learn jupyter notebook ipykernel -y
conda activate lab1_terminal
python -m ipykernel install --user --name lab1_terminal --display-name "Python (lab1_terminal)"

:: для дополнительного задания ЛР №2 (дашборд)
conda install streamlit -y
```

Запуск Jupyter Notebook в каталоге репозитория — файл `start-jupyter.bat`
(либо вручную: `conda activate lab1_terminal && jupyter notebook`).

Блокноты с суффиксом `_colab` открываются в Google Colaboratory:
**File → Upload notebook** либо напрямую с GitHub через
**File → Open notebook → GitHub**.

## Отчёт для защиты

Отчёт в формате `.docx` собирается из блокнотов автоматически — текст, код, вывод ячеек
и графики берутся из выполненных блокнотов, скриншоты подхватываются из каталога `images/`:

```bat
cd lab01
python make_report.py
```

Скрипту нужен пакет `python-docx` (`pip install python-docx`). Готовые `Отчет_*.docx`
и `.pdf` в репозиторий не добавляются: они полностью воспроизводятся из блокнотов.
