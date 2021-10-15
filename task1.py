# Parsing call file

"""
Входные данные:
    -файл с номерами из договора
    -файл от оператора формата:
        nn, city_source, auth, location, svc, terminat, innn, country, zone, date_f, time, dura, seconds, rate, charge, custno

Выходные файлы:
МС 
01.09.2021 - 30.09.2021|2|777|{line}|абонентска плата|штука|1|280.0000|1
01.09.2021 - 30.09.2021|2|777|8632688720|Местные вызовы|минута|37|0.0000|1
ВЗ
8632688721;14.09.2021 11:02:00;79885403982;7988;Вызовы на абонентов сотовых сетей Ростовской области Сотовые, Ростов-на-Дону;1.00;1.49
МГ
8632688720;27.09.2021 15:41:00;74992600525;7499;г.Москва Москва;2.00;1.80
"""


import os
from itertools import islice


FILE_NUMBER_DOGOVOR = "num.txt"


def load_orange_numbers(file_name):
    orange_numbers = []
    with open(file_name, mode='r', encoding='utf-8') as sorce_file:
        for line in sorce_file:
            orange_numbers.append(line[:10])
        # print(orange_numbers)
    return orange_numbers


def fiend_start_file():
    for root , _, files in os.walk('./in'):
        if '.csv' in files[0]:
            sorce_file = os.path.normpath(os.path.join(root, files[0]))
            # print(sorce_file)
    return sorce_file


def parsing_sorce_file(sorce_file, orange_numbers):
    local_file = {}
    zone_file = []
    mg_file = []
    price_zone, price_mg = 0
    # count_local, count_zone = 0, 0
    with open(sorce_file, mode='r') as sorce_file:
        for line in islice(sorce_file, 1, None):
            _, _, auth, _, svc, terminat, _, country, zone, date_f, time, _, seconds, _, charge, _ = line.split(";")
            # print(line)

            # проверка на номер без договора
            if  auth not in orange_numbers:
                auth = orange_numbers[0]

            # Местные вызовы
            if svc == 'L':
                if auth not in local_file:
                    local_file[auth] = int(int(seconds)/60) 
                else:
                    local_file[auth] = local_file.get(auth) + int(int(seconds)/60)
                # count_local += int(int(seconds)/60)
            
            # ВЗ вызовы
            elif svc == 'Z':
                zone_file.append(f'{auth};{date_f} {time}:00;{terminat};{terminat[:4]};{zone} {country};{(int(seconds)/60)}0;{charge.replace(",",".")}')
                # print(zone_file)
                price_zone += float(charge.replace(",","."))
            
            # МГ вызовы
            elif svc == 'C':
                mg_file.append(f'{auth};{date_f} {time}:00;{terminat};{terminat[:4]};{zone} {country};{(int(seconds)/60)}0;{charge.replace(",",".")}')
                # print(mg_file)
                price_mg += float(charge.replace(",","."))