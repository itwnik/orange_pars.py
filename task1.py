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
import calendar
import datetime as dt
from itertools import islice


FILE_NUMBER_DOGOVOR = "num.txt"
IN_PATH = './in'
OUT_PATH = './out'

local_file = {}
zone_file = []
mg_file = []
price_zone, price_mg = 0, 0


def load_orange_numbers(file_name):
    orange_numbers = []
    with open(file_name, mode='r', encoding='utf-8') as sorce_file:
        for line in sorce_file:
            orange_numbers.append(line[:10])
    return orange_numbers


def fiend_start_file():
    for root , _, files in os.walk('./in'):
        if '.csv' in files[0]:
            sorce_file = os.path.normpath(os.path.join(root, files[0]))
    return sorce_file


def parsing_sorce_file(sorce_file, orange_numbers):
    global price_zone, price_mg
    count_local, count_zone, count_mg = 0, 0, 0
    with open(sorce_file, mode='r') as sorce_file:
        for line in islice(sorce_file, 1, None):
            _, _, auth, _, svc, terminat, _, country, zone, date_f, time_f, _, seconds, _, charge, _ = line.split(";")
            # проверка на номер без договора
            if  auth not in orange_numbers:
                auth = orange_numbers[0]
            # Местные вызовы
            if svc == 'L':
                if auth not in local_file:
                    local_file[auth] = int(int(seconds)/60) 
                else:
                    local_file[auth] = local_file.get(auth) + int(int(seconds)/60)
                count_local += int(int(seconds)/60)
            # ВЗ вызовы
            elif svc == 'Z':
                zone_file.append(f'{auth};{date_f} {time_f[:6]}:00;{terminat};{terminat[:4]};{zone} {country};{(int(seconds)/60)}0;{float(charge.replace(",",".")):.2f}\n')
                price_zone += round(float(charge.replace(",",".")),2)
                count_zone += int(int(seconds)/60)
            # МГ вызовы
            elif svc == 'C':
                mg_file.append(f'{auth};{date_f} {time_f[:6]}:00;{terminat};{terminat[:4]};{zone} {country};{(int(seconds)/60)}0;{float(charge.replace(",",".")):.2f}\n')
                price_mg += round(float(charge.replace(",",".")), 2)
                count_mg += int(int(seconds)/60)


def format_date_local_call():
    end_past_month_day = calendar.monthrange(dt.date.today().year, dt.date.today().month-1)[1]
    start_past_date = f'01.{dt.date.today().month-1}.{dt.date.today().year}'
    end_past_date = f'{end_past_month_day}.{dt.date.today().month-1}.{dt.date.today().year}'
    start = dt.datetime.strptime(start_past_date, '%d.%m.%Y')
    end = dt.datetime.strptime(end_past_date, '%d.%m.%Y')
    period = f'{start:%d}.{start:%m}.{start:%Y} - {end:%d}.{end:%m}.{end:%Y}'
    return period


def out_file(numbers):
    # Местные вызовы
    period = format_date_local_call()
    with open(os.path.join(OUT_PATH, "ms.txt"), mode='w', encoding='utf-8') as file:
        for number in numbers:
            file.write(f'{period}|2|777|{number}|Абонентска плата|штука|1|280.0000|1\n')
            if number in local_file.keys():
                file.write(f'{period}|2|777|{number}|Местные вызовы|минута|{local_file.get(number)}|0.0000|1\n')
    # ВЗ вызовы
    with open(os.path.join(OUT_PATH, "vz.txt"), mode='w', encoding='utf-8') as file:
        for txt in zone_file:
            file.write(txt)
    # МГ вызовы
    with open(os.path.join(OUT_PATH, "mg.txt"), mode='w', encoding='utf-8') as file:
        for txt in mg_file:
            file.write(txt)
    # Сумма
    with open(os.path.join(OUT_PATH, "price.txt"), mode='w', encoding='utf-8') as file:
            file.write(f'МС - 9 240 руб.\nВЗ - {round(price_zone, 2)} руб. \nМГ - {round(price_mg, 2)} руб. \n')

if __name__ == "main":
    try:
        orange_numbers = load_orange_numbers(FILE_NUMBER_DOGOVOR)
        sorce_file = fiend_start_file()
        parsing_sorce_file(sorce_file, orange_numbers)
        out_file(orange_numbers)
    except FileNotFoundError:
        print('Отсутствует файл с номерами из договора "num.txt"')
