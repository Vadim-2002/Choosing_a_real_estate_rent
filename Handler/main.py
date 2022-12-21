from processor.dataprocessor_service import DataProcessorService
import os


"""
    Main-модуль, т.е. модуль запуска приложений ("точка входа" приложения)
"""


if __name__ == '__main__':
    while True:
        count_file = os.listdir().count("dataset.csv")
        if count_file > 0:
            DataProcessorService(datasource="dataset.csv",db_connection_url="sqlite:///base.db").run_service()
            os.remove("dataset.csv")

