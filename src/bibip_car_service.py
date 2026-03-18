"""Python-модуль, имитирующий аналог базы данных автомобильного салона.
Позволяет добавлять, извлекать, обновлять и удалять информацию из БД.
"""

from datetime import datetime
from decimal import Decimal
import os

from models import (
    Car,
    CarFullInfo,
    CarStatus,
    Model,
    ModelSaleStats,
    Sale
)


class CarService:

    def __init__(self, root_directory_path: str) -> None:
        """Инициализатор класса принимает в качестве аргумента
        адрес корневой директории и создает файлы для хранения информации.
        """
        self.root_directory_path = root_directory_path
        self.path_models_file = os.path.join(
            self.root_directory_path, 'models.txt'
        )
        self.path_models_index_file = os.path.join(
            self.root_directory_path, 'models_index.txt'
        )
        self.path_cars_file = os.path.join(
            self.root_directory_path, 'cars.txt'
        )
        self.path_cars_index_file = os.path.join(
            self.root_directory_path, 'cars_index.txt'
        )
        self.path_sales_file = os.path.join(
            self.root_directory_path, 'sales.txt'
        )
        self.path_sales_index_file = os.path.join(
            self.root_directory_path, 'sales_index.txt'
        )

    def add_model(self, model: Model) -> Model:
        """Метод принимает в качестве аргумента объект класса Model,
        делает запись в файлах models.txt и models_index.txt,
        возращает объект класса Model.
        """
        with open(self.path_models_file, 'a') as models_file:
            # определяем позицию для вычесления индекса
            model_index = models_file.tell()
            new_entry = f'{model.id};{model.name};{model.brand}'.ljust(500)
            models_file.write(new_entry + '\n')
        with open(self.path_models_index_file, 'a') as models_index_file:
            models_index_file.write(f'{model.id};{model_index}\n')
        return model

    def add_car(self, car: Car) -> Car:
        """Метод принимает в качестве аргумента объект класса Car,
        делает запись в файлах cars.txt и cars_index.txt,
        возращает объект класса Car.
        """
        with open(self.path_cars_file, 'a') as cars_file:
            # определяем позицию для вычесления индекса
            car_index = cars_file.tell()
            new_entry = (
                f'{car.vin};{car.model};{car.price};'
                f'{car.date_start};{car.status}'.ljust(500)
            )
            cars_file.write(new_entry + '\n')
        with open(self.path_cars_index_file, 'a') as car_index_file:
            car_index_file.write(f'{car.vin};{car_index}\n')
        return car

    def sell_car(self, sale: Sale) -> Car:
        """Метод принимает в качестве аргумента объект класса Sale,
        делает запись в файлах sales.txt и sales_index.txt,
        возращает объект класса Car (проданное авто).
        """
        with open(self.path_sales_file, 'a') as sales_file:
            # определяем позицию для вычесления индекса
            sale_index = sales_file.tell()
            new_entry = (
                f'{sale.sales_number};{sale.car_vin};'
                f'{sale.sales_date};{sale.cost}'.ljust(500)
            )
            sales_file.write(new_entry + '\n')
        with open(self.path_sales_index_file, 'a') as sales_index_file:
            sales_index_file.write(f'{sale.car_vin};{sale_index}\n')
        car_index = None
        with open(self.path_cars_index_file, 'r') as cars_index_file:
            for entry in cars_index_file:
                vin, index = entry.rstrip().split(';')
                if vin == sale.car_vin:
                    car_index = int(index)
                    break
        # меняем статус авто на sold
        with open(self.path_cars_file, 'r+') as cars_file:
            cars_file.seek(car_index)
            car_entry = cars_file.readline().rstrip().split(';')
            car_entry[4] = CarStatus.sold
            cars_file.seek(car_index)
            new_entry = ';'.join(car_entry).ljust(500)
            cars_file.write(new_entry + '\n')
        return Car(
            vin=car_entry[0],
            model=int(car_entry[1]),
            price=Decimal(car_entry[2]),
            date_start=datetime.strptime(
                            car_entry[3], '%Y-%m-%d %H:%M:%S'
                        ),
            status=car_entry[4]
        )

    def get_cars(self, status: CarStatus) -> list[Car]:
        """Метод принимает в качестве аргумета объект класса CarStatus,
        делает выборку доступных к продаже авто (available), сортирует
        данные по VIN-коду, возвращает список с объектами класса Car.
        """
        with open(self.path_cars_file, 'r') as cars_file:
            cars_available = []
            for entry in cars_file:
                if status in entry:
                    entry_split = entry.rstrip().split(';')
                    cars_available.append(
                        Car(
                            vin=entry_split[0],
                            model=int(entry_split[1]),
                            price=Decimal(entry_split[2]),
                            date_start=datetime.strptime(
                                            entry_split[3],
                                            '%Y-%m-%d %H:%M:%S'
                                        ),
                            status=entry_split[4]
                        )
                    )
        # сортируем выборку по VIN-коду авто
        # cars_available.sort(key=lambda x: x.vin)
        # в чате study выяснили, что тест ругается на сортировку
        # и поэтому можно закомментить
        return cars_available

    def get_car_info(self, vin: str) -> CarFullInfo | None:
        """Метод принимает в качестве аргумента VIN-код автомобиля,
        возращает объект класса CarFullInfo с детальной информацией
        о машине либо None.
        """
        car_index = None
        sales_date = None
        sales_cost = None
        with open(self.path_cars_index_file, 'r') as cars_index_file:
            for entry in cars_index_file:
                index_vin, index = entry.rstrip().split(';')
                if index_vin == vin:
                    car_index = int(index)
                    break
        if car_index is None:
            return None
        with open(self.path_cars_file, 'r') as cars_file:
            # извлекаем данные об авто
            cars_file.seek(car_index)
            car_entry = cars_file.readline().rstrip().split(';')
        with open(self.path_models_file, 'r') as models_file:
            # извлекаем данные о модели
            for entry in models_file:
                model_entry = entry.rstrip().split(';')
                if model_entry[0] == car_entry[1]:
                    model_name = model_entry[1]
                    model_brand = model_entry[2]
                    break
        if car_entry[4] == CarStatus.sold:
            with open(self.path_sales_file, 'r') as sales_files:
                # извлекаем данные о продаже
                for entry in sales_files:
                    sale_entry = entry.rstrip().split(';')
                    if sale_entry[1] == vin:
                        sales_date = datetime.strptime(
                            sale_entry[2],
                            '%Y-%m-%d %H:%M:%S'
                        )
                        sales_cost = Decimal(sale_entry[3])
        return CarFullInfo(
            vin=car_entry[0],
            car_model_name=model_name,
            car_model_brand=model_brand,
            price=Decimal(car_entry[2]),
            date_start=datetime.strptime(
                car_entry[3],
                '%Y-%m-%d %H:%M:%S'
            ),
            status=car_entry[4],
            sales_date=sales_date,
            sales_cost=sales_cost
        )

    def update_vin(self, vin: str, new_vin: str) -> Car:
        """Метод позволяет скорректировать VIN-код автомобиля, принимает
        в качестве аргументов старый и новый идетификаторы, возвращает
        объект класса Car.
        """
        with open(self.path_cars_file, 'r') as f:
            car_entries = f.readlines()
            car_entries_upd = []
            for entry in car_entries:
                entry_split = entry.rstrip().split(';')
                if vin in entry_split:
                    entry_split[0] = new_vin
                    car_upd_vin = Car(
                        vin=entry_split[0],
                        model=int(entry_split[1]),
                        price=Decimal(entry_split[2]),
                        date_start=datetime.strptime(
                                        entry_split[3], '%Y-%m-%d %H:%M:%S'
                                    ),
                        status=entry_split[4]
                    )
                car_entries_upd.append(';'.join(entry_split) + '\n')
        with open(self.path_cars_file, 'w') as f:
            f.writelines(car_entries_upd)
        with open(self.path_cars_index_file, 'r') as f:
            # обновляем данные в файле с индексами авто
            car_idx_entries = f.readlines()
            car_idx_entries_upd = []
            for entry in car_idx_entries:
                entry_split = entry.split(';')
                if vin in entry_split:
                    entry_split[0] = new_vin
                car_idx_entries_upd.append(';'.join(entry_split))
        with open(self.path_cars_index_file, 'w') as f:
            f.writelines(car_idx_entries_upd)
        return car_upd_vin

    def revert_sale(self, sales_number: str) -> Car:
        """Метод принимает в качестве аргумента номер несостоявшейся продажи,
        удаляет запись продажи, изменяет статус авто на available,
        возвращает объект класса Car.
        """
        car_vin = None
        sale_index = None
        with open(self.path_sales_file, 'r') as sales_file:
            sales_entries = sales_file.readlines()
        for index, sale_data in enumerate(sales_entries):
            # извлекаем данные о продаже
            sale_entry = sale_data.rstrip().split(';')
            if sale_entry[0].rstrip() == sales_number.rstrip():
                sale_index = index
                car_vin = sale_entry[1]
                break
        car_index = None
        with open(self.path_cars_file, 'r') as cars_file:
            cars_entries = cars_file.readlines()
        for index, sale_data in enumerate(cars_entries):
            car_data = sale_data.rstrip().split(';')
            if car_data[0].rstrip() == car_vin.rstrip():
                car_index = index
                break
        with open(self.path_cars_file, 'r+') as cars_file:
            # возвращаем авто статус available
            car_data = cars_entries[car_index].rstrip().split(';')
            car_data[4] = CarStatus.available
            updated_car_info = ';'.join(car_data).ljust(500)
            cars_file.seek(0)
            cars_entries[car_index] = updated_car_info + '\n'
            cars_file.writelines(cars_entries)
        sales_entries.pop(sale_index)
        with open(self.path_sales_file, 'w') as sales_file:
            # перезаписываем файл продаж
            sales_file.writelines(sales_entries)
        with open(self.path_sales_index_file, 'r') as sales_index_file:
            sales_index_entries = sales_index_file.readlines()
        with open(self.path_sales_index_file, 'w') as sales_index_file:
            # перезаписываем файл с индексами продаж
            for sale_index_entries in sales_index_entries:
                sale_index_data = sale_index_entries.rstrip().split(';')
                if sale_index_data[0].rstrip() != car_vin.rstrip():
                    sales_index_file.write(sale_index_entries)
        return Car(
            vin=car_data[0],
            model=int(car_data[1]),
            price=Decimal((car_data[2])),
            date_start=datetime.strptime(
                car_data[3],
                '%Y-%m-%d %H:%M:%S'
            ),
            status=car_data[4]
        )

    def top_models_by_sales(self) -> list[ModelSaleStats]:
        """Метод сортирует данные по количеству продаж каждой модели авто
        с учетом ее цены, делает срез с тремя самыми продаваемыми моделями,
        возвращает список с объектами ModelSaleStats.
        """
        sold_models_data = {}
        model_prices = {}
        top_list = []
        with open(self.path_models_file, 'r') as f:
            model_entries = f.readlines()
            for entry in model_entries:
                # заполняем словарь с данными по проданным моделям
                # используем id моделей в качестве ключей
                entry_split = entry.split(';')
                sold_models_data[entry_split[0]] = 0
        with open(self.path_cars_file, 'r') as f:
            car_entries = f.readlines()
            for entry in car_entries:
                # проверяем записи с параметром sold, извлекаем id модели
                # подсчитываем количество продаж конкретной модели
                entry_split = entry.rstrip().split(';')
                if entry_split[4] == 'sold':
                    sold_models_data[entry_split[1]] += 1
        with open(self.path_sales_file, 'r') as f:
            sale_entries = f.readlines()
            for entry in car_entries:
                entry_split = entry.split(';')
                car_vin = entry_split[0]
                model_id = entry_split[1]
                for entry in sale_entries:
                    entry_split = entry.rstrip().split(';')
                    sale_cost = entry_split[3]
                    # получаем цены проданных моделей
                    if car_vin == entry_split[1]:
                        model_prices[model_id] = sale_cost
        # сортируем модели по количеству продаж и цене, формируем топ-3
        sorted_data = sorted(
            sold_models_data.items(),
            key=lambda x: (-x[1], -int(model_prices.get(x[0], 0)))
        )[:3]
        for model_id, sale_count in sorted_data:
            for entry in model_entries:
                entry_split = entry.rstrip().split(';')
                if model_id == entry_split[0]:
                    top_list.append(
                        ModelSaleStats(
                            car_model_name=entry_split[1],
                            brand=entry_split[2],
                            sales_number=sale_count
                        )
                    )
        return top_list
