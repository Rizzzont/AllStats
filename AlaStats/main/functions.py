import re
from operator import index
import pandas as pd
import os
from typing import Dict, Any, List


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

def parse_delivery_time_second(value):
    if not isinstance(value, str):
        return 0

    days_matches = re.findall(r"(\d+)\s*д", value)
    hours_matches = re.findall(r"(\d+)\s*ч", value)

    total_days = sum(int(d) for d in days_matches)
    total_hours = sum(int(h) for h in hours_matches)

    return total_days * 24 + total_hours


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

def designer_sum(sheet_dict: Dict[str, pd.DataFrame], designer: str) -> List[float]:
    value_profit = []
    value_not_profit = []
    value_sales = []
    value_not_sales = []
    for sheet_name, df in sheet_dict.items():

        if df is None or df.empty:
            value_profit.append(0)
            print("Такого нет")
            continue

        if "Артикул продавца" not in df.columns:
            value_profit.append(0)
            print("Такого нет 2")
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
        grouped_sales = df.groupby("Инициалы дизайнера")[["Выкупили, шт"]].sum()
        grouped_not_sales = df.groupby("Инициалы дизайнера")[["Заказали, шт"]].sum()

        if designer:
            val_profit = float(grouped_profit.loc[designer]["Выкупили на сумму, ₽"])
            val_not_profit = float(grouped_not_profit.loc[designer]["Заказали на сумму, ₽"])
            val_sales = float(grouped_sales.loc[designer]["Выкупили, шт"])
            val_not_sales = float(grouped_not_sales.loc[designer]["Заказали, шт"])


        else:
            val = 0


        value_profit.append(val_profit)
        value_not_profit.append(val_not_profit)
        value_sales.append(val_sales)
        value_not_sales.append(val_not_sales)
    print([value_profit, value_not_profit, value_sales, value_not_sales])
    return [value_profit, value_not_profit, value_sales, value_not_sales]

def designers_sum(sheet_dict: Dict[str, pd.DataFrame]) -> List[List[float]]:
    all_data = []

    for df in sheet_dict.values():
        if df is None or df.empty or "Артикул продавца" not in df.columns:
            continue
        df["Инициалы дизайнера"] = df["Артикул продавца"].apply(parsing)
        all_data.append(df)

    if not all_data:
        return []

    full_df = pd.concat(all_data, ignore_index=True)

    full_df = full_df.dropna(subset=[
        "Инициалы дизайнера", "Выкупили на сумму, ₽", "Заказали на сумму, ₽",
        "Выкупили, шт", "Заказали, шт"
    ])

    grouped = full_df.groupby("Инициалы дизайнера")[[
        "Выкупили на сумму, ₽", "Заказали на сумму, ₽",
        "Выкупили, шт", "Заказали, шт"
    ]].sum()

    top10 = grouped.sort_values(by="Выкупили на сумму, ₽", ascending=False).head(15)

    labels = []
    profit = []
    orders = []
    sales = []
    not_sales = []

    for index, row in top10.iterrows():
        labels.append(index)
        profit.append(float(row["Выкупили на сумму, ₽"]))
        orders.append(float(row["Заказали на сумму, ₽"]))
        sales.append(float(row["Выкупили, шт"]))
        not_sales.append(float(row["Заказали, шт"]))

    return [labels, profit, orders, sales, not_sales]

def categories_sum(sheet_dict: Dict[str, pd.DataFrame]) -> List[List[float]]:
    all_data = []

    for df in sheet_dict.values():
        if df is None or df.empty or "Предмет" not in df.columns:
            continue
        all_data.append(df)

    if not all_data:
        return []

    full_df = pd.concat(all_data, ignore_index=True)

    full_df = full_df.dropna(subset=[
        "Предмет", "Выкупили на сумму, ₽", "Заказали на сумму, ₽",
        "Выкупили, шт", "Заказали, шт"
    ])

    grouped = full_df.groupby("Предмет")[[
        "Выкупили на сумму, ₽", "Заказали на сумму, ₽",
        "Выкупили, шт", "Заказали, шт"
    ]].sum()

    top10 = grouped.sort_values(by="Выкупили на сумму, ₽", ascending=False).head(10)

    labels = []
    profit = []
    orders = []
    sales = []
    not_sales = []

    for index, row in top10.iterrows():
        labels.append(index)
        profit.append(float(row["Выкупили на сумму, ₽"]))
        orders.append(float(row["Заказали на сумму, ₽"]))
        sales.append(float(row["Выкупили, шт"]))
        not_sales.append(float(row["Заказали, шт"]))

    return [labels, profit, orders, sales, not_sales]

def category_sum(sheet_dict: Dict[str, pd.DataFrame], category: str) -> List[List[float]]:
    value_profit = []
    value_not_profit = []
    value_sales = []
    value_not_sales = []

    for df in sheet_dict.values():
        if df is None or df.empty or "Предмет" not in df.columns:
            value_profit.append(0)
            value_not_profit.append(0)
            value_sales.append(0)
            value_not_sales.append(0)
            continue

        required = [
            "Выкупили на сумму, ₽", "Заказали на сумму, ₽",
            "Выкупили, шт", "Заказали, шт"
        ]
        if not all(col in df.columns for col in required):
            value_profit.append(0)
            value_not_profit.append(0)
            value_sales.append(0)
            value_not_sales.append(0)
            continue

        grouped = df.groupby("Предмет")[
            ["Выкупили на сумму, ₽", "Заказали на сумму, ₽", "Выкупили, шт", "Заказали, шт"]
        ].sum()

        if category in grouped.index:
            row = grouped.loc[category]
            value_profit.append(float(row["Выкупили на сумму, ₽"]))
            value_not_profit.append(float(row["Заказали на сумму, ₽"]))
            value_sales.append(float(row["Выкупили, шт"]))
            value_not_sales.append(float(row["Заказали, шт"]))
        else:
            value_profit.append(0)
            value_not_profit.append(0)
            value_sales.append(0)
            value_not_sales.append(0)

    return [value_profit, value_not_profit, value_sales, value_not_sales]

def good_sum(sheet_dict: Dict[str, pd.DataFrame], article: Any) -> List[List[float]]:
    value_profit = []
    value_not_profit = []
    value_sales = []
    value_not_sales = []

    for df in sheet_dict.values():
        if df is None or df.empty or "Артикул продавца" not in df.columns:
            value_profit.append(0)
            value_not_profit.append(0)
            value_sales.append(0)
            value_not_sales.append(0)
            continue

        required = [
            "Выкупили на сумму, ₽", "Заказали на сумму, ₽",
            "Выкупили, шт", "Заказали, шт"
        ]
        if not all(col in df.columns for col in required):
            value_profit.append(0)
            value_not_profit.append(0)
            value_sales.append(0)
            value_not_sales.append(0)
            continue

        filtered = df[df["Артикул продавца"] == article]

        value_profit.append(float(filtered["Выкупили на сумму, ₽"].sum()) if not filtered.empty else 0)
        value_not_profit.append(float(filtered["Заказали на сумму, ₽"].sum()) if not filtered.empty else 0)
        value_sales.append(float(filtered["Выкупили, шт"].sum()) if not filtered.empty else 0)
        value_not_sales.append(float(filtered["Заказали, шт"].sum()) if not filtered.empty else 0)

    return [value_profit, value_not_profit, value_sales, value_not_sales]

def goods_sum(sheet_dict: Dict[str, pd.DataFrame]) -> List[List[float]]:
    all_data = []

    for df in sheet_dict.values():
        if df is None or df.empty or "Артикул продавца" not in df.columns:
            continue
        all_data.append(df)

    if not all_data:
        return []

    full_df = pd.concat(all_data, ignore_index=True)

    full_df = full_df.dropna(subset=[
        "Артикул продавца", "Выкупили на сумму, ₽", "Заказали на сумму, ₽",
        "Выкупили, шт", "Заказали, шт"
    ])

    grouped = full_df.groupby("Артикул продавца")[[
        "Выкупили на сумму, ₽", "Заказали на сумму, ₽",
        "Выкупили, шт", "Заказали, шт"
    ]].sum()

    top10 = grouped.sort_values(by="Выкупили на сумму, ₽", ascending=False).head(10)

    labels = []
    profit = []
    orders = []
    sales = []
    not_sales = []

    for index, row in top10.iterrows():
        labels.append(index)
        profit.append(float(row["Выкупили на сумму, ₽"]))
        orders.append(float(row["Заказали на сумму, ₽"]))
        sales.append(float(row["Выкупили, шт"]))
        not_sales.append(float(row["Заказали, шт"]))

    return [labels, profit, orders, sales, not_sales]



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


def get_card_data_from_excel(xl, article, article_col='Артикул продавца'):
    dfs = []
    for sheet_names, df in xl.items():
        dfs.append(df)
    df_full = pd.concat(dfs, ignore_index=True)

    df_art = df_full[df_full[article_col] == article]
    if df_art.empty:
        return None

    name = df_art["Название"].iloc[0]
    subject = df_art["Предмет"].iloc[0]
    designer = df_art["Бренд"].iloc[0]
    avg_rating = df_art["Рейтинг по отзывам"].mean()

    sum_transitions = df_art["Переходы в карточку"].sum()
    sum_to_cart = df_art["Положили в корзину"].sum()
    sum_ordered = df_art["Заказали, шт"].sum()
    sum_purchased = df_art["Выкупили, шт"].sum()

    avg_cart_conversion = df_art["Конверсия в корзину, %"].mean()
    avg_order_conversion = df_art["Конверсия в заказ, %"].mean()
    avg_purchase_percent = df_art["Процент выкупа"].mean()
    avg_purchase_percent2 = df_art["Отменили, шт"].mean()

    sum_ordered_rub = df_art["Заказали на сумму, ₽"].sum()
    sum_to_cart_rub = df_art["Положили в корзину"].sum() if "Положили в корзину" in df_art.columns else 0
    sum_purchased_rub = df_art["Выкупили на сумму, ₽"].sum()
    sum_purchased_rub2 = sum_purchased_rub

    cards = [
        name, subject, designer, round(avg_rating, 2),
        int(sum_transitions), int(sum_to_cart), int(sum_ordered), int(sum_purchased),
        round(avg_cart_conversion, 2), round(avg_order_conversion, 2), round(avg_purchase_percent, 2),
        int(avg_purchase_percent2),
        int(sum_ordered_rub), int(sum_to_cart_rub), int(sum_purchased_rub), int(sum_purchased_rub2)
    ]
    return cards

