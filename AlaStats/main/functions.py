import re


def parse_delivery_time(value):
    if not isinstance(value, str):
        return 0

    days = 0
    hours = 0


    # Используем регулярки для поиска чисел перед "д" и "ч"
    match_days = re.search(r"(\d+)\s*д", value)
    match_hours = re.search(r"(\d+)\s*ч", value)

    if match_days:
        days = int(match_days.group(1))
    if match_hours:
        hours = int(match_hours.group(1))

    return days * 24 + hours

def main_info(dataframe):
    profit = 0
    orders = 0
    rate = [0, 0]
    delivery_time = [0, 0]
    for index, row in dataframe.iterrows():
        try:
            profit += int(row["Выкупили на сумму, ₽"])
        except (ValueError, TypeError):
            pass

        try:
            orders += int(row["Заказали, шт"])
        except (ValueError, TypeError):
            pass

        try:
            rate[0] += float(row["Рейтинг карточки"])
            rate[1] += 1
        except (ValueError, TypeError):
            pass

        try:
            delivery_time[0] += parse_delivery_time(row['Среднее время доставки'])
            delivery_time[1] += 1

        except (ValueError, TypeError):
            pass

    rate = round(rate[0]/rate[1], 1)
    delivery_time = delivery_time[0]/delivery_time[1]
    delivery_time = f"{int(delivery_time // 24)}д {int(delivery_time % 24)}ч"
    return {"profit":profit, "orders":orders, "rate":rate, "delivery_time":delivery_time}


def analyt(dataframe):
    pass