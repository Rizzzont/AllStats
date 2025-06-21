import re
from enum import unique
import pandas as pd
import json

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

    rate_result = round(rate[0]/rate[1], 1) if rate[1] else 0
    avg_delivery_hours = delivery_time[0]/delivery_time[1] if delivery_time[1] else 0
    delivery_str = f"{int(avg_delivery_hours // 24)}д {int(avg_delivery_hours % 24)}ч"

    return {
        "profit": profit,
        "orders": orders,
        "rate": rate_result,
        "delivery_time": delivery_str
    }


def main_analytic(sheet_dict):
    combined_df = pd.concat(sheet_dict.values(), ignore_index=True)

    if "Предмет" not in combined_df.columns:
        return {"chart_names": [], "chart_sales": [], "chart_profit": []}

    names = combined_df["Предмет"].unique().tolist()
    data_about_sales = [0 for _ in names]
    data_about_profit = [0 for _ in names]

    for _, row in combined_df.iterrows():
        try:
            idx = names.index(row["Предмет"])
            data_about_sales[idx] += int(row["Выкупили, шт"])
            data_about_profit[idx] += int(row["Выкупили на сумму, ₽"])
        except (ValueError, TypeError, KeyError):
            pass

    combined = list(zip(names, data_about_sales, data_about_profit))
    combined.sort(key=lambda x: x[2], reverse=True)
    top_combined = combined[:10]

    return {
        "chart_names": [item[0] for item in top_combined],
        "chart_sales": [item[1] for item in top_combined],
        "chart_profit": [item[2] for item in top_combined]
    }