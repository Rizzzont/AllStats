class TotalProfit:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def get_results(self):
        total = 0
        for index, row in self.dataframe.iterrows():
            total += int(row["Выкупили на сумму, ₽"])  # Пример вычисления
        return total
