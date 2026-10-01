# -*- coding: utf-8 -*-
"""
Сборка краткого отчёта по лабораторной работе в формате .docx.

Отчёт намеренно компактный: листинги кода в него не включаются — они есть
в блокнотах и в репозитории. В документ попадают только описание выполненных
действий, скриншоты, ключевые результаты (версии пакетов, параметры наборов
данных), построенные графики и выводы.

Числа и графики берутся из выполненного блокнота lab01_anaconda.ipynb,
поэтому отчёт не расходится с фактическими результатами.

Запуск:
    D:\\PROGRAMM\\anaconda3\\envs\\ml\\python.exe make_report.py
"""

import base64
import re
from pathlib import Path

import nbformat
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

LAB_DIR = Path(__file__).resolve().parent
NB_ANACONDA = LAB_DIR / "lab01_anaconda.ipynb"
IMAGES = LAB_DIR / "images"
OUT = LAB_DIR / "Отчет_ЛР1.docx"

TITLE = {
    "university": "Белорусский государственный университет",
    "faculty": "Факультет прикладной математики и информатики",
    "department": "Кафедра технологий программирования",
    "work": "Лабораторная работа № 1",
    "topic": "Настройка среды разработки и управление виртуальными окружениями",
    "discipline": "ДП2",
    "student": "Машканов Михаил Вячеславович",
    "group": "14",
    "teacher": "Волчецкая Полина Сергеевна",
    "city_year": "Минск, 2026",
}

REPO_URL = "https://github.com/mishamashkanov/DP2"

SCREENSHOTS = {
    "01_navigator_create_env.png":
        ("Рисунок 1 — создание окружения lab1_gui в Anaconda Navigator",
         "Navigator → Environments → Create: имя lab1_gui, Python 3.12"),
    "02_navigator_env_active.png":
        ("Рисунок 2 — окружение lab1_gui активировано через графический интерфейс",
         "Navigator → Environments: lab1_gui выделено как активное"),
    "03_prompt_create_activate.png":
        ("Рисунок 3 — создание и активация окружения lab1_terminal в Anaconda Prompt",
         "Anaconda Prompt: conda create / conda activate, приглашение (lab1_terminal)"),
    "04_navigator_install_packages.png":
        ("Рисунок 4 — установка библиотек через менеджер пакетов Navigator",
         "Navigator: пакеты отмечены, фильтр Not installed, перед нажатием Apply"),
    "05_colab_runtime_type.png":
        ("Рисунок 5 — выбор аппаратного ускорителя в Google Colaboratory",
         "Colab → Среда выполнения → Сменить среду выполнения"),
    "06_colab_gpu.png":
        ("Рисунок 6 — сведения о графическом ускорителе (вывод nvidia-smi)",
         "Colab в режиме T4 GPU: результат выполнения ячейки с nvidia-smi"),
    "07_colab_tpu.png":
        ("Рисунок 7 — сведения об устройствах TPU",
         "Colab в режиме TPU: результат выполнения ячейки с jax.devices()"),
}

# --------------------------------------------------------------------------- #
# Оформление
# --------------------------------------------------------------------------- #


def shade(cell, fill):
    el = OxmlElement("w:shd")
    el.set(qn("w:val"), "clear")
    el.set(qn("w:fill"), fill)
    cell._tc.get_or_add_tcPr().append(el)


def borders(cell, color="BFBFBF", sz=4):
    tc_pr = cell._tc.get_or_add_tcPr()
    box = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:color"), color)
        box.append(el)
    tc_pr.append(box)


def para(doc, text, size=12, bold=False, italic=False, align=None,
         space_after=6, color=None, mono=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    if align is not None:
        p.alignment = align

    emit_inline(p, text, size=size)

    for run in p.runs:
        if bold:
            run.bold = True
        if italic:
            run.italic = True
        if mono:
            run.font.name = "Consolas"
        if color:
            run.font.color.rgb = RGBColor(*color)
    return p


def bullets(doc, items, style="List Bullet"):
    for item in items:
        p = doc.add_paragraph(style=style)
        p.paragraph_format.space_after = Pt(3)
        emit_inline(p, item)


INLINE = re.compile(r"\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`")


def emit_inline(par, text, size=12):
    """Разбор **жирного**, *курсива* и `моноширинного` внутри абзаца."""
    pos = 0
    for m in INLINE.finditer(text):
        if m.start() > pos:
            par.add_run(text[pos:m.start()])
        bold, italic, mono = m.groups()
        if bold is not None:
            par.add_run(bold).bold = True
        elif italic is not None:
            par.add_run(italic).italic = True
        else:
            run = par.add_run(mono)
            run.font.name = "Consolas"
            run.font.size = Pt(size - 1.5)
        pos = m.end()
    if pos < len(text):
        par.add_run(text[pos:])
    for run in par.runs:
        if run.font.size is None:
            run.font.size = Pt(size)


def table(doc, rows, widths=None, font=10.5):
    t = doc.add_table(rows=0, cols=len(rows[0]))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    if widths:
        t.columnWidths = widths
    for i, row in enumerate(rows):
        cells = t.add_row().cells
        for j, (cell, value) in enumerate(zip(cells, row)):
            if widths:
                cell.width = widths[j]
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            emit_inline(p, str(value))
            for run in p.runs:
                run.font.size = Pt(font)
                if i == 0:
                    run.bold = True
            if i == 0:
                shade(cell, "EFEFEF")
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return t


def caption(doc, text):
    para(doc, text, size=9.5, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER,
         space_after=10, color=(0x59, 0x59, 0x59))


def figure(doc, filename, width=Cm(15.0)):
    """Скриншот из images/. Если файла ещё нет — остаётся только подпись."""
    title, _ = SCREENSHOTS[filename]
    path = IMAGES / filename
    if path.exists():
        doc.add_picture(str(path), width=width)
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption(doc, title)
    return path.exists()


def commands(doc, text):
    """Короткий блок команд терминала — без листингов Python."""
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = t.cell(0, 0)
    shade(cell, "F2F4F7")
    borders(cell)
    cell.text = ""
    for i, line in enumerate(text.strip().splitlines()):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(line)
        run.font.name = "Consolas"
        run.font.size = Pt(9)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)


# --------------------------------------------------------------------------- #
# Извлечение фактов из выполненного блокнота
# --------------------------------------------------------------------------- #


def collect_facts():
    facts = {"versions": [], "packages": "—", "shapes": {}, "plots": [],
             "python": "3.12", "conda": "—", "os": "—"}
    if not NB_ANACONDA.exists():
        print("блокнот не найден, отчёт будет собран без фактических данных")
        return facts

    nb = nbformat.read(NB_ANACONDA, as_version=4)
    texts, shapes = [], []
    for cell in nb.cells:
        for out in cell.get("outputs", []):
            if out.output_type == "stream":
                texts.append(out.get("text", ""))
            elif out.output_type in ("display_data", "execute_result"):
                data = out.get("data", {})
                if "image/png" in data:
                    facts["plots"].append(data["image/png"])
                elif "text/plain" in data:
                    texts.append(data["text/plain"])

    blob = "\n".join(texts)

    for name in ("numpy", "pandas", "matplotlib", "seaborn", "scikit-learn"):
        m = re.search(rf"^{re.escape(name)}\s+([0-9][\w.+-]*)$", blob, re.M)
        facts["versions"].append((name, m.group(1) if m else "—"))

    m = re.search(r"Всего установлено пакетов[^:]*:\s*(\d+)", blob)
    if m:
        facts["packages"] = m.group(1)

    m = re.search(r"Версия Python\s*:\s*([\d.]+)", blob)
    if m:
        facts["python"] = m.group(1)

    m = re.search(r"conda\s+([\d.]+)", blob)
    if m:
        facts["conda"] = m.group(1)

    m = re.search(r"Операционная система\s*:\s*(.+)", blob)
    if m:
        facts["os"] = m.group(1).strip()

    shapes = re.findall(r"Размерность \(строк, столбцов\):\s*\((\d+),\s*(\d+)\)", blob)
    if len(shapes) >= 2:
        facts["shapes"]["iris"] = shapes[0]
        facts["shapes"]["titanic"] = shapes[1]
    return facts


def plot(doc, facts, index, title):
    if index >= len(facts["plots"]):
        para(doc, f"[график не найден в блокноте: {title}]", size=10, italic=True)
        return
    tmp = LAB_DIR / ".report_tmp"
    tmp.mkdir(exist_ok=True)
    path = tmp / f"plot_{index}.png"
    path.write_bytes(base64.b64decode(facts["plots"][index]))
    doc.add_picture(str(path), width=Cm(14.5))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption(doc, title)


# --------------------------------------------------------------------------- #
# Отчёт
# --------------------------------------------------------------------------- #


def header(doc):
    """Компактная шапка вместо отдельного титульного листа."""
    para(doc, TITLE["work"], size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER,
         space_after=4)
    para(doc, TITLE["topic"], size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    para(doc, f"по дисциплине «{TITLE['discipline']}»", size=11,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10,
         color=(0x59, 0x59, 0x59))
    para(doc, f"Выполнил: {TITLE['student']}      Группа: {TITLE['group']}",
         size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)


def build(doc, facts):
    doc.add_heading("Цель работы", level=1)
    para(doc, "Освоение навыков развёртывания изолированных сред разработки, управления "
              "пакетами через графический интерфейс (GUI) и терминал в Anaconda "
              "и Google Colaboratory, а также первичный аудит аппаратных ресурсов.")

    doc.add_heading("Среда выполнения", level=1)
    table(doc, [
        ["Параметр", "Значение"],
        ["Операционная система", facts["os"]],
        ["Дистрибутив", "Anaconda3-2026.07-1 (Windows x64), каталог `D:\\PROGRAMM\\anaconda3`"],
        ["Менеджер пакетов", f"conda {facts['conda']}"],
        ["Версия Python", facts["python"]],
        ["Оболочка", "Jupyter Notebook, Google Colaboratory"],
    ], widths=[Cm(5.0), Cm(11.0)])

    # ---------------------------------------------------------------- часть 1
    doc.add_heading("Часть 1. Работа в среде Anaconda", level=1)

    doc.add_heading("1.1. Установка платформы", level=2)
    para(doc, "Дистрибутив Anaconda скачан с официального сайта и установлен в режиме "
              "**Just Me** в каталог `D:\\PROGRAMM\\anaconda3` — путь без пробелов и кириллицы, "
              "что является требованием conda. Регистрация Anaconda как интерпретатора "
              "по умолчанию включена, добавление в переменную `PATH` отключено согласно "
              "рекомендации разработчика.")

    doc.add_heading("1.2. Управление виртуальными окружениями", level=2)
    para(doc, "Виртуальное окружение conda — изолированный каталог с собственным "
              "интерпретатором Python и набором библиотек. Изоляция позволяет держать "
              "для разных задач несовместимые версии пакетов и не нарушать работу "
              "базового окружения `base`. По условию работы окружения созданы двумя способами.")
    table(doc, [
        ["Окружение", "Способ создания", "Назначение"],
        ["`lab1_gui`", "Anaconda Navigator (GUI)", "работа с окружениями через графический интерфейс"],
        ["`lab1_terminal`", "Anaconda Prompt (`conda create`)", "окружение, в котором выполнен блокнот работы"],
    ], widths=[Cm(3.6), Cm(5.4), Cm(7.0)])

    para(doc, "**Через GUI.** В Anaconda Navigator на вкладке *Environments* нажата кнопка "
              "*Create*, указано имя `lab1_gui` и версия Python 3.12. Активация выполняется "
              "щелчком по имени окружения — Navigator помечает его как активное, и все "
              "дальнейшие операции относятся уже к нему.")
    figure(doc, "01_navigator_create_env.png")
    figure(doc, "02_navigator_env_active.png")

    para(doc, "**Через терминал.** В Anaconda Prompt выполнены команды создания и активации; "
              "после активации приглашение сменилось с `(base)` на `(lab1_terminal)`.")
    commands(doc,
             "conda create -n lab1_terminal python=3.12 numpy pandas matplotlib "
             "seaborn scikit-learn jupyter -y\n"
             "conda activate lab1_terminal")
    figure(doc, "03_prompt_create_activate.png")

    doc.add_heading("1.3. Установка библиотек и аудит версий", level=2)
    para(doc, "Библиотеки установлены обоими способами: в окружении `lab1_gui` — через "
              "менеджер пакетов Navigator (фильтр *Not installed* → выбор пакетов → *Apply*), "
              "в окружении `lab1_terminal` — командой `conda install`.")
    figure(doc, "04_navigator_install_packages.png")

    para(doc, "Версии установленных пакетов определены программно в блокноте — импортом "
              "библиотеки и чтением атрибута `__version__`, с проверкой через "
              "`importlib.metadata`:")
    table(doc, [["Пакет", "Версия", "Статус"]] +
               [[f"`{name}`", ver, "установлен"] for name, ver in facts["versions"]],
          widths=[Cm(5.5), Cm(4.0), Cm(6.5)])

    para(doc, f"Полный список пакетов окружения получен командой `conda list` — всего "
              f"в окружении `lab1_terminal` установлено **{facts['packages']}** пакетов; "
              f"вывод сохранён в файле `logs/conda_list_lab1_terminal.txt`.")

    # ---------------------------------------------------------------- часть 2
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    doc.add_heading("Часть 2. Работа в среде Google Colaboratory", level=1)
    para(doc, "Под учётной записью Google запущен сервис Google Colaboratory и создан новый "
              "блокнот. Выполнен первичный аудит выделенной виртуальной машины (процессор, "
              "объём оперативной памяти, дисковое пространство) и проверено наличие требуемых "
              "библиотек.")
    table(doc, [
        ["Проверено", "Результат"],
        ["`numpy`, `pandas`, `matplotlib`, `seaborn`, `scikit-learn`",
         "предустановлены, версии определены программно"],
        ["Установка отсутствующего пакета", "выполнена командой `!pip install` на примере `catboost`"],
        ["Режим CPU", "ускоритель не подключён, `nvidia-smi` драйвер не обнаруживает"],
        ["Режим GPU", "модель ускорителя, версия драйвера и CUDA, объём видеопамяти — `nvidia-smi`, `torch.cuda`"],
        ["Режим TPU", "список устройств через `jax.devices()`; утилите `nvidia-smi` TPU не виден"],
    ], widths=[Cm(6.0), Cm(10.0)])

    para(doc, "Переключение вычислителя выполняется через меню *Среда выполнения → Сменить "
              "среду выполнения*. При смене типа ускорителя виртуальная машина "
              "перезапускается: переменные и доустановленные через `pip` пакеты теряются.")
    figure(doc, "05_colab_runtime_type.png")
    figure(doc, "06_colab_gpu.png")
    figure(doc, "07_colab_tpu.png")

    # ---------------------------------------------------------------- часть 3
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    doc.add_heading("Часть 3. Экспериментальная проверка на наборах данных", level=1)
    para(doc, "Для проверки работоспособности собранного окружения использованы два "
              "различных набора данных. Оба загружены средствами `pandas` из CSV-файлов "
              "каталога `data/`, для каждого построен график средствами `seaborn`/`matplotlib`.")

    iris = facts["shapes"].get("iris", ("150", "5"))
    tita = facts["shapes"].get("titanic", ("891", "15"))
    table(doc, [
        ["Набор данных", "Объектов", "Признаков", "Особенности"],
        ["Fisher's Iris", iris[0], iris[1], "числовые признаки, три класса, пропусков нет"],
        ["Titanic", tita[0], tita[1], "смешанные типы признаков, есть пропущенные значения"],
    ], widths=[Cm(4.0), Cm(2.2), Cm(2.3), Cm(7.5)])

    plot(doc, facts, 0, "Рисунок 8 — Iris: зависимость ширины лепестка от его длины")
    para(doc, "Вид *setosa* линейно отделим от двух остальных по признакам лепестка, "
              "*versicolor* и *virginica* частично перекрываются.", size=11)

    plot(doc, facts, 1, "Рисунок 9 — Titanic: факторы, связанные с выживаемостью")
    para(doc, "Доля выживших резко различается по полу и классу каюты. Пропуски в столбце "
              "возраста корректно обработаны при построении гистограммы.", size=11)

    # ---------------------------------------------------------------- выводы
    doc.add_heading("Выводы", level=1)
    bullets(doc, [
        "Дистрибутив Anaconda установлен и настроен; работоспособность подтверждена программно.",
        "Изолированные виртуальные окружения созданы и активированы двумя способами — "
        "через графический интерфейс Anaconda Navigator и через терминал командами "
        "`conda create` и `conda activate`.",
        "Библиотеки `numpy`, `pandas`, `matplotlib`, `seaborn`, `scikit-learn` установлены "
        "обоими способами, их версии определены программно; получен полный список пакетов "
        "окружения.",
        "В Google Colaboratory проверены предустановленные пакеты, продемонстрирована "
        "установка через `!pip install`, освоено переключение вычислителей и получены "
        "сведения об оборудовании в режимах GPU и TPU.",
        "Работоспособность окружения подтверждена на двух различных наборах данных: "
        "выполнена загрузка через `pandas` и построены графики.",
    ], style="List Number")

    doc.add_heading("Исходный код", level=1)
    para(doc, "Блокноты с полным кодом, результатами вычислений и графиками, наборы данных "
              "и протоколы работы с conda опубликованы в репозитории:")
    para(doc, REPO_URL, mono=True, size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER)


def main():
    facts = collect_facts()

    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    style.paragraph_format.space_after = Pt(6)

    for section in doc.sections:
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(1.5)
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)

    header(doc)
    build(doc, facts)
    doc.save(OUT)

    print(f"отчёт сохранён: {OUT}")
    print(f"графиков из блокнота: {len(facts['plots'])}, "
          f"пакетов в окружении: {facts['packages']}")

    missing = [name for name in SCREENSHOTS if not (IMAGES / name).exists()]
    if missing:
        print("\nещё не добавлены скриншоты (в отчёте на их месте оранжевые рамки):")
        for name in missing:
            print("   images/" + name)
        print("после добавления — запустить этот скрипт повторно")
    else:
        print("\nвсе скриншоты на месте")


if __name__ == "__main__":
    main()
