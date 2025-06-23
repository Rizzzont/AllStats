import re
from enum import unique
import pandas as pd
import json
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
    rate = [0, 0]
    delivery_time = [0, 0]

    for sheet_name, df in sheet_dict.items():
        for _, row in df.iterrows():
            try:
                profit += int(row["Выкупили на сумму, ₽"])
            except (ValueError, TypeError, KeyError):
                pass

            try:
                orders += int(row["Заказали, шт"])
            except (ValueError, TypeError, KeyError):
                pass

            try:
                rate[0] += float(row["Рейтинг карточки"])
                rate[1] += 1
            except (ValueError, TypeError, KeyError):
                pass

            try:
                delivery_time[0] += parse_delivery_time(row["Среднее время доставки"])
                delivery_time[1] += 1
            except (ValueError, TypeError, KeyError):
                pass

    rate_result = round(rate[0] / rate[1], 1) if rate[1] else 0
    avg_delivery_hours = delivery_time[0] / delivery_time[1] if delivery_time[1] else 0
    delivery_str = f"{int(avg_delivery_hours // 24)}д {int(avg_delivery_hours % 24)}ч"
    return {
        "profit": profit,
        "orders": orders,
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

        if "Выкупили, шт" in df.columns and "Выкупили на сумму, ₽" in df.columns:
            for _, row in df.iterrows():
                try:
                    total_sales += int(row["Выкупили, шт"])
                    total_profit += int(row["Выкупили на сумму, ₽"])
                except (ValueError, TypeError, KeyError):
                    continue

        chart_names.append(sheet_name)
        chart_sales.append(total_sales)
        chart_profit.append(total_profit)

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

