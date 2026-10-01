# Машинное обучение и анализ данных — лабораторные работы

Репозиторий с лабораторными работами по курсу машинного обучения и анализа данных.
Каждая работа оформлена как блокнот Jupyter (`.ipynb`), сохранённый **вместе с результатами
вычислений и графиками** — то есть открывается для просмотра прямо на GitHub, без запуска.

## Среда выполнения

| Компонент | Значение |
|---|---|
| Дистрибутив | Anaconda Distribution (Anaconda3-2026.07-1, Windows x64) |
| Python | 3.12 |
| Основные библиотеки | `numpy`, `pandas`, `matplotlib`, `seaborn`, `scikit-learn` |
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
└── lab01/                        — ЛР №1. Настройка среды и виртуальные окружения
    ├── lab01_anaconda.ipynb      — части 1 и 3: Anaconda, окружения, эксперимент на данных
    ├── lab01_colab.ipynb         — часть 2: Google Colab, аппаратные ускорители (GPU/TPU)
    ├── make_report.py            — сборка отчёта .docx из блокнотов
    ├── data/                     — наборы данных, использованные в работе
    │   ├── iris.csv              — Fisher's Iris, 150 объектов
    │   └── titanic.csv           — Titanic, 891 объект
    ├── images/                   — скриншоты графического интерфейса
    └── logs/                     — протоколы работы с conda в терминале
        ├── conda_create_lab1_terminal.log
        ├── conda_list_lab1_terminal.txt
        └── conda_env_list.txt
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

## Воспроизведение окружения

Создание окружения со всеми необходимыми пакетами:

```bat
conda create -n lab1_terminal python=3.12 numpy pandas matplotlib seaborn scikit-learn jupyter notebook ipykernel -y
conda activate lab1_terminal
python -m ipykernel install --user --name lab1_terminal --display-name "Python (lab1_terminal)"
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
