import re
from enum import unique
import pandas as pd
import json
import os
from typing import Dict, Any, List, Optional


def parse_delivery_time(value):
    if not isinstance(value, str):
        return 0

    days = 0
    hours = 0

    match_days = re.search(r"(\d+)\s*д", value)
    match_hours = re.search(r"(\d+)\s*ч", value)

    if match_days:
        days = int(match_days.group(1))
    if match_hours:
        hours = int(match_hours.group(1))

    return days * 24 + hours


def main_info(sheet_dict):
    profit = 0
    orders = 0
    rate_sum = 0
    rate_count = 0
    delivery_sum = 0
    delivery_count = 0

    for df in sheet_dict.values():
        if "Выкупили на сумму, ₽" in df:
            profit += pd.to_numeric(df["Выкупили на сумму, ₽"], errors="coerce").sum(skipna=True)

        if "Заказали, шт" in df:
            orders += pd.to_numeric(df["Заказали, шт"], errors="coerce").sum(skipna=True)

        if "Рейтинг карточки" in df:
            rate_series = pd.to_numeric(df["Рейтинг карточки"], errors="coerce")
            rate_sum += rate_series.sum(skipna=True)
            rate_count += rate_series.count()

        if "Среднее время доставки" in df:
            times = df["Среднее время доставки"].dropna().apply(parse_delivery_time)
            delivery_sum += times.sum()
            delivery_count += times.count()

    rate_result = round(rate_sum / rate_count, 1) if rate_count else 0
    avg_delivery_hours = delivery_sum / delivery_count if delivery_count else 0
    delivery_str = f"{int(avg_delivery_hours // 24)}д {int(avg_delivery_hours % 24)}ч"

    return {
        "profit": int(profit),
        "orders": int(orders),
        "rate": rate_result,
        "delivery_time": delivery_str
    }



def main_analytic(sheet_dict):
    chart_sales = []
    chart_profit = []
    chart_names = []

    for sheet_name, df in sheet_dict.items():
        total_sales = 0
        total_profit = 0

        if "Выкупили, шт" in df.columns:
            total_sales = pd.to_numeric(df["Выкупили, шт"], errors="coerce").sum(skipna=True)

        if "Выкупили на сумму, ₽" in df.columns:
            total_profit = pd.to_numeric(df["Выкупили на сумму, ₽"], errors="coerce").sum(skipna=True)

        chart_names.append(sheet_name)
        chart_sales.append(int(total_sales))
        chart_profit.append(int(total_profit))

    return {
        "chart_sales": chart_sales,
        "chart_profit": chart_profit,
        "chart_names": chart_names
    }



def remove_elements(lst):
    elements_to_remove = {"TEAM", "FON", "NABOR", "ROD", "VES", "KD"}
    return [item for item in lst if item not in elements_to_remove]


def parsing(art):
    if pd.isna(art):
        return None
    splitted_art = str(art).split('-')
    splitted_art = remove_elements(splitted_art)
    num = {
        "AKR": 4, "BOX": 1, "AD": 2, "BANK": 1, "NGT": 1, "MTL": 2, "OJV": 6, "3D": 1, "PASP": 2,
        "STUD": 2, "CART": 2, "RM": 2, "BAN": 1, "CHEV": 2, "POP": 2, "KL": 2, "GIT": 2, "EGD": 2,
        "ZNP": 2, "3DS": 1, "MGNT": 2, "VKL": 2, "ADK": 2, "ÀÄ": 2, "1": 2, "ÍÃÒ": 1, "ÈÍÒ": 1,
        "INT": 1, "1P": 2, "SCHBOX": 1, "SHPR": 2, "ZKL": 2, "PLST": 3, "PRST": 2, "PRMGNT": 2,
        "PLMGNT": 2, "PIAN": 2, "PARK": 2, "OTKR": 2, "MGNTR": 2, "DIMPLST": 3, "DIMGNT": 2, "AKROD": 3
    }
    if "OJV" in splitted_art:
        return splitted_art[6] if len(splitted_art) > 6 else None
    elif "RM" in splitted_art:
        return splitted_art[2] if len(splitted_art) > 2 else None
    elif "AKROD" in splitted_art and "3MM" in splitted_art:
        return splitted_art[4] if len(splitted_art) > 4 else None
    else:
        key = splitted_art[0] if splitted_art else None
        index = num.get(key, None)
        n = ["ORACAL", "WHITE", "ORAGUARD", "30cm", "POSTER", "ORANGE"]
        if index is not None and len(splitted_art) > index:
            if splitted_art[index].isdigit() or splitted_art[index] in n or "cm" in splitted_art[index]:
                return None
            return splitted_art[index]
        else:
            return None


# Для дизайнера по месяцам
def designer_sum(sheet_dict: Dict[str, pd.DataFrame], designer: str) -> List[float]:
    value_profit = []
    value_not_profit = []
    for sheet_name, df in sheet_dict.items():

        if df is None or df.empty:
            value_profit.append(0)
            continue

        if "Артикул продавца" not in df.columns:
            value_profit.append(0)
            continue

        if df is None or df.empty:
            value_not_profit.append(0)
            continue

        if "Артикул продавца" not in df.columns:
            value_not_profit.append(0)
            continue

        df["Инициалы дизайнера"] = df["Артикул продавца"].apply(parsing)

        grouped_profit = df.groupby("Инициалы дизайнера")[["Выкупили на сумму, ₽"]].sum()
        grouped_not_profit = df.groupby("Инициалы дизайнера")[["Заказали на сумму, ₽"]].sum()

        if designer:
            val_profit = float(grouped_profit.loc[designer]["Выкупили на сумму, ₽"])
            val_not_profit = float(grouped_not_profit.loc[designer]["Заказали на сумму, ₽"])

        else:
            val = 0

        value_profit.append(val_profit)
        value_not_profit.append(val_not_profit)
    return [value_profit, value_not_profit]

# Для всех дизайнеров в листе/месяце
def designers_sum(sheet_dict: Dict[str, pd.DataFrame]) -> List[List[float]]:
    print("функция запустилась")
    values = []
    value_profit = []
    value_not_profit = []
    i = 0
    for sheet_name, df in sheet_dict.items():
        if df is None or df.empty or "Артикул продавца" not in df.columns:
            values.append(0)
            continue
        print("Идёт")
        df['Инициалы дизайнера'] = df["Артикул продавца"].apply(parsing)
        grouped_profit = df.groupby("Инициалы дизайнера")[["Выкупили на сумму, ₽"]].sum()
        grouped_not_profit = df.groupby("Инициалы дизайнера")[["Заказали на сумму, ₽"]].sum()

        summa = grouped_profit["Выкупили на сумму, ₽"].sum()
        value_profit.append(float(summa))
        summa = grouped_not_profit["Заказали на сумму, ₽"].sum()
        value_not_profit.append(float(summa))
        print("Всё еще идёт?")

    values = [value_profit, value_not_profit]
    return values


# Для всех категорий в листе/месяце
def categories_sum(sheet_dict: Dict[str, pd.DataFrame]) -> List[List[float]]:
    value_profit = []
    value_not_profit = []

    for sheet_name, df in sheet_dict.items():
        if df is None or df.empty or "Предмет" not in df.columns:
            value_profit.append(0)
            value_not_profit.append(0)
            continue

        grouped = df.groupby("Предмет")[["Выкупили на сумму, ₽", "Заказали на сумму, ₽"]].sum()
        profit = grouped["Выкупили на сумму, ₽"].sum()
        not_profit = grouped["Заказали на сумму, ₽"].sum()

        value_profit.append(float(profit))
        value_not_profit.append(float(not_profit))

    return [value_profit, value_not_profit]


# По одной категории по месяцам
def category_sum(sheet_dict: Dict[str, pd.DataFrame], category: str) -> List[List[float]]:
    value_profit = []
    value_not_profit = []

    for sheet_name, df in sheet_dict.items():
        if df is None or df.empty or "Предмет" not in df.columns:
            value_profit.append(0)
            value_not_profit.append(0)
            continue

        grouped = df.groupby("Предмет")[["Выкупили на сумму, ₽", "Заказали на сумму, ₽"]].sum()

        if category in grouped.index:
            val_profit = float(grouped.loc[category]["Выкупили на сумму, ₽"])
            val_not_profit = float(grouped.loc[category]["Заказали на сумму, ₽"])
        else:
            val_profit = 0
            val_not_profit = 0

        value_profit.append(val_profit)
        value_not_profit.append(val_not_profit)

    return [value_profit, value_not_profit]



# По одному артикулу по месяцам
def good_sum(sheet_dict: Dict[str, pd.DataFrame], article: Any) -> List[List[float]]:
    value_profit = []
    value_not_profit = []

    for sheet_name, df in sheet_dict.items():
        if df is None or df.empty or "Артикул продавца" not in df.columns:
            value_profit.append(0)
            value_not_profit.append(0)
            continue

        filtered = df[df["Артикул продавца"] == article]

        profit = float(filtered["Выкупили на сумму, ₽"].sum()) if not filtered.empty else 0
        not_profit = float(filtered["Заказали на сумму, ₽"].sum()) if not filtered.empty else 0

        value_profit.append(profit)
        value_not_profit.append(not_profit)

    return [value_profit, value_not_profit]




# По всем артикулам в листе/месяце
def goods_sum(sheet_dict: Dict[str, pd.DataFrame]) -> List[List[float]]:
    value_profit = []
    value_not_profit = []

    for sheet_name, df in sheet_dict.items():
        if df is None or df.empty or "Артикул продавца" not in df.columns:
            value_profit.append(0)
            value_not_profit.append(0)
            continue

        profit = float(df["Выкупили на сумму, ₽"].sum())
        not_profit = float(df["Заказали на сумму, ₽"].sum())

        value_profit.append(profit)
        value_not_profit.append(not_profit)

    return [value_profit, value_not_profit]


def load_stopwords(path):
    words = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            words.update(word.lower() for word in line.split())
    return words

def extract_keywords(name, stopwords):
    return tuple(sorted(set(str(name).lower().split()) - stopwords))

def process_sheet(df, stopwords, info):
    df = df.dropna(subset=["Название", "Заказали, шт"])
    df["keywords"] = (
        df["Название"]
        .astype(str)
        .str.lower()
        .str.split()
        .apply(lambda words: tuple(sorted(set(words) - stopwords)))
    )

    grouped = df.groupby("keywords")["Заказали, шт"].sum()
    for key, sales in grouped.items():
        info[key] = info.get(key, 0) + sales

def last(xls, month_choice="year"):
    COLUMNS = ["Название", "Предмет", "Заказали, шт"]
    STOPWORDS_FILE = os.path.join(os.path.dirname(__file__), "text.txt")
    stopwords = load_stopwords(STOPWORDS_FILE)
    info = {}

    all_sheets = list(xls.keys())

    if month_choice == "year":
        sheets_to_process = all_sheets
    else:
        try:
            sheets_to_process = [all_sheets[int(month_choice) - 1]]
        except (ValueError, IndexError):
            return []

    for sheet in sheets_to_process:
        df = xls[sheet]
        if all(col in df.columns for col in COLUMNS):
            df = df.dropna(subset=["Название", "Заказали, шт"])
            df["keywords"] = (
                df["Название"]
                .astype(str)
                .str.lower()
                .str.split()
                .apply(lambda words: tuple(sorted(set(words) - stopwords)))
            )
            grouped = df.groupby("keywords")["Заказали, шт"].sum()
            for key, sales in grouped.items():
                info[key] = info.get(key, 0) + sales

    result = [{"theme": " ".join(k), "products": 1, "sales": v} for k, v in info.items()]
    return sorted(result, key=lambda x: x["sales"], reverse=True)[2:100]

