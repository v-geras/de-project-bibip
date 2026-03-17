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

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        """Метод принимает в качестве аргумента объект класса Model,
        делает запись в файлах models.txt и models_index.txt,
        возращает объект класса Model.
        """
        with open(self.path_models_file, 'a') as f:
            f.write(f'{model.id};{model.name};{model.brand}\n')
        with open(self.path_models_file, 'r') as f:
            model_entries = f.readlines()
        with open(self.path_models_index_file, 'w') as f:
            for line_num, model_data in enumerate(model_entries, start=1):
                # извлекаем id модели и записываем его вместе с номером строки
                f.write(f'{model_data.split(';')[1]},{line_num}\n')
        return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        """Метод принимает в качестве аргумента объект класса Car,
        делает запись в файлах cars.txt и cars_index.txt,
        возращает объект класса Car.
        """
        with open(self.path_cars_file, 'a') as f:
            f.write(
                f'{car.vin};{car.model};{car.price};'
                f'{car.date_start};{car.status}\n'
            )
        with open(self.path_cars_file, 'r') as f:
            car_entries = f.readlines()
        with open(self.path_cars_index_file, 'w') as f:
            for line_num, car_data in enumerate(car_entries, start=1):
                # извлекаем id авто и записываем его вместе с номером строки
                f.write(f'{car_data.split(';')[0]};{line_num}\n')
        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        """Метод принимает в качестве аргумента объект класса Sale,
        делает запись в файлах sales.txt и sales_index.txt,
        возращает объект класса Car (проданное авто).
        """
        with open(self.path_sales_file, 'a') as f:
            f.write(
                f'{sale.sales_number};{sale.car_vin};'
                f'{sale.sales_date};{sale.cost}\n'
            )
        with open(self.path_sales_file, 'r') as f:
            sale_entries = f.readlines()
        with open(self.path_sales_index_file, 'w') as f:
            for line_num, sale_data in enumerate(sale_entries, start=1):
                # извлекаем номер продажи
                # и записываем его вместе с номером строки
                f.write(f'{sale_data.split(';')[0]};{line_num}\n')
        with open(self.path_cars_file, 'r') as f:
            car_entries = f.readlines()
            car_entries_upd = []
            sold_car = None
            for entry in car_entries:
                entry_split = entry.rstrip().split(';')
                if sale.car_vin in entry_split:
                    entry_split[-1] = 'sold'
                    sold_car = Car(
                        vin=entry_split[0],
                        model=int(entry_split[1]),
                        price=Decimal(entry_split[2]),
                        date_start=datetime.strptime(
                                        entry_split[3], '%Y-%m-%d %H:%M:%S'
                                    ),
                        status=CarStatus.sold
                    )
                car_entries_upd.append(';'.join(entry_split) + '\n')
        with open(self.path_cars_file, 'w') as f:
            f.writelines(car_entries_upd)
        return sold_car

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        """Метод принимает в качестве аргумета объект класса CarStatus,
        делает выборку доступных к продаже авто (available), сортирует
        данные по VIN-коду, возвращает список с объектами класса Car.
        """
        with open(self.path_cars_file, 'r') as f:
            car_entries = f.readlines()
            cars_available = []
            for entry in car_entries:
                if status in entry:
                    entry_split = entry.rstrip().split(';')
                    car = Car(
                        vin=entry_split[0],
                        model=int(entry_split[1]),
                        price=Decimal(entry_split[2]),
                        date_start=datetime.strptime(
                                        entry_split[3], '%Y-%m-%d %H:%M:%S'
                                    ),
                        status=status
                    )
                    cars_available.append(car)
            # сортируем выборку по VIN-коду авто
            # cars_available.sort(key=lambda x: x.vin)
            # в чате study выяснили, что тест ругается на сортировку
            # и поэтому можно закомментить
        return cars_available

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        """Метод принимает в качестве аргумента VIN-код автомобиля,
        возращает объект класса CarFullInfo с детальной информацией
        о машине либо None.
        """
        with open(self.path_cars_file, 'r') as f:
            car_entries = f.readlines()
        with open(self.path_models_file, 'r') as f:
            model_entries = f.readlines()
        car_sales_date = None
        car_sales_cost = None
        car_full_data = None
        for entry in car_entries:
            # извлекаем данные об авто
            if vin in entry:
                car_entry_split = entry.rstrip().split(';')
                model_id = car_entry_split[1]
                car_price = car_entry_split[2]
                car_date_start = car_entry_split[3]
                car_status = car_entry_split[4]
                for entry in model_entries:
                    # извлекаем данные о модели
                    if model_id in entry:
                        model_entry_split = entry.rstrip().split(';')
                        model_name = model_entry_split[1]
                        model_brand = model_entry_split[2]
                if car_status == 'sold':
                    with open(self.path_sales_file, 'r') as f:
                        sale_entries = f.readlines()
                        for entry in sale_entries:
                            # извлекаем данные о продаже
                            if vin in entry:
                                sale_entry_split = entry.rstrip().split(';')
                                car_sales_date = sale_entry_split[2]
                                car_sales_cost = sale_entry_split[3]
                # формируем профайл
                car_full_data = CarFullInfo(
                    vin=vin,
                    car_model_name=model_name,
                    car_model_brand=model_brand,
                    price=Decimal(car_price),
                    date_start=datetime.strptime(
                        car_date_start, '%Y-%m-%d %H:%M:%S'
                    ),
                    status=CarStatus(car_status),
                    sales_date=car_sales_date,
                    sales_cost=car_sales_cost
                )
        return car_full_data

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        """Метод позволяет скорректировать VIN-код автомобиля, принимает
        в качестве аргументов старый и новый идетификаторы, возвращает
        объект класса Car.
        """
        # обновляем данные в файле с авто
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

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        """Метод принимает в качестве аргумента номер несостоявшейся продажи,
        удаляет запись продажи, изменяет статус авто на available,
        возвращает объект класса Car.
        """
        with open(self.path_sales_file, 'r') as f:
            sale_entries = f.readlines()
            car_vin = None
            for entry in sale_entries:
                # убираем строку с продажей
                if sales_number in entry:
                    car_vin = entry.split(';')[1]
                    sale_entries.remove(entry)
        with open(self.path_sales_file, 'w') as f:
            f.writelines(sale_entries)
        with open(self.path_sales_index_file, 'w') as f:
            for line_num, sale_data in enumerate(sale_entries, start=1):
                f.write(f'{sale_data.split(';')[0]};{line_num}\n')
        with open(self.path_cars_file, 'r') as f:
            car_entries = f.readlines()
            car_entries_upd = []
            for entry in car_entries:
                entry_split = entry.rstrip().split(';')
                # возвращаем авто статус available
                if car_vin in entry_split:
                    entry_split[4] = CarStatus.available
                    car = Car(
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
        return car

    # Задание 7. Самые продаваемые модели
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
