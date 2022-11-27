from abc import ABC, abstractmethod     # подключаем инструменты для создания абстрактных классов
import pandas   # пакет для работы с датасетами
import numpy as np

"""
    В данном модуле реализуются классы обработчиков для 
    применения алгоритма обработки к различным типам файлов (csv или txt).
    
    ВАЖНО! Если реализация различных обработчиков занимает большое 
    количество строк, то необходимо оформлять каждый класс в отдельном файле
"""


class DataProcessor(ABC):
    """ Родительский класс для обработчиков файлов """

    def __init__(self, datasource):
        # общие атрибуты для классов обработчиков данных
        self._datasource = datasource   # путь к источнику данных
        self._dataset = None            # входной набор данных
        self.result = None              # выходной набор данных (результат обработки)

    # Все методы, помеченные декоратором @abstractmethod, ОБЯЗАТЕЛЬНЫ для переобределения
    @abstractmethod
    def read(self) -> bool:
        """ Метод, инициализирующий источник данных """
        pass

    @abstractmethod
    def run(self) -> None:
        """ Точка запуска методов обработки данных """
        pass

    """
        Метод sort_data_by_col - пример одного из методов обработки данных.
        В данном случае метод просто сортирует входной датасет по наименованию 
        заданной колонки (аргумент colname) и устанавливает тип сортировки: 
        ascending = True - по возрастанию, ascending = False - по убыванию
        
        ВАЖНО! Следует логически разделять методы обработки, например, отдельный метод для сортировки, 
        отдельный метод для удаления "пустот" в датасете (очистка) и т.д. Это позволит гибко применять необходимые
        методы при переопределении метода run для того или иного типа обработчика.
        НАПРИМЕР, если ваш источник данных это не файл, а база данных, тогда метод сортировки будет не нужен,
        т.к. сортировку можно сделать при выполнении SQL-запроса типа SELECT ... ORDER BY...
    """

    def sorting_by_columns(self, df: pandas.DataFrame, col_name: str, asc: bool) -> pandas.DataFrame:
        return df.sort_values(by=[col_name], ascending=asc)

    @abstractmethod
    def print_result(self) -> None:
        """ Абстрактный метод для вывода результата на экран """
        pass

        """ Метод для категоризирования данных"""
    def add_category(self, df: pandas.DataFrame) -> pandas.DataFrame:
        min_price = df["price"].min()
        max_price = df["price"].max()
        avg_price = df["price"].mean()

        avg_max = (avg_price + max_price) / 2
        avg_min = (avg_price + min_price) / 2

        df['category'] = pandas.cut(df['price'], [min_price, avg_min, avg_max / 30, max_price], labels=[1, 2, 3])
        return df

    def save_in_file(self):
        self.result.to_csv('result_dt.csv', index=False, sep=',')
        
    def missing_data(self, df: pandas.DataFrame):
        for col in df.columns:
            pct_missing = np.mean(df[col].isnull())
            print('{} - {}%'.format(col, round(pct_missing*100)))


class CsvDataProcessor(DataProcessor):
    """ Реализация класса-обработчика csv-файлов """

    def __init__(self, datasource):
        # Переопределяем конструктор родительского класса
        DataProcessor.__init__(self, datasource)    # инициализируем конструктор родительского класса для получения общих атрибутов
        self.separators = [';', ',', '|']        # список допустимых разделителей

    """
        Переопределяем метод инициализации источника данных.
        Т.к. данный класс предназначен для чтения CSV-файлов, то используем метод read_csv
        из библиотеки pandas
    """
    def read(self):
        try:
            # Пытаемся преобразовать данные файла в pandas.DataFrame, используя различные разделители
            for separator in self.separators:
                self._dataset = pandas.read_csv(self._datasource, sep=separator, header='infer', names=None, encoding="utf-8")
                # Читаем имена колонок из файла данных
                col_names = self._dataset.columns
                # Если количество считанных колонок > 1 возвращаем True
                if len(col_names) > 1:
                    print(f'Columns read: {col_names} using separator {separator}')
                    return True
        except Exception as e:
            print(e)
        return False

    def run(self):
        # Удаляем пустоты в каждой колонке
        self.result = pandas.DataFrame()
        for col in ['bedroom', 'locality', 'property_type', 'price', 'area', 'city']:
            col_data = self._dataset[col].dropna()
            self.result[col] = col_data
        self.result = self.add_category(self.result)
        #записываем результат в отдельный файл
        self.save_in_file()
            
    def print_result(self):
        print(f'Running CSV-file processor!\n', self.result)


class TxtDataProcessor(DataProcessor):
    """ Реализация класса-обработчика txt-файлов """

    def read(self):
        """ Реализация метода для чтения TXT-файла (разедитель колонок - пробелы) """
        try:
            self._dataset = pandas.read_table(self._datasource, sep='\s+', engine='python')
            col_names = self._dataset.columns
            if len(col_names) < 2:
                return False
            return True
        except Exception as e:
            print(str(e))
            return False

    def run(self):
        self.result = self.add_category(self._dataset)

    def print_result(self):
        print(f'Running TXT-file processor!\n', self.result)
