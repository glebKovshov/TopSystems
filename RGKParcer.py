import re
from pathlib import Path
import os

#Ввести путь, где хранятся файлы include RGK
RGKPath = "C:\\RGK\\install\\include\\RGK\\"

def find_method_name(method):
    end = method.index("(")
    method_name = method[method.rindex(" ", 0, end)+1:end]
    return method_name

def find_return_type(method):
    end = method.index("(")
    method = method[:end]
    #Убираем название метода и оставляем только возвращаемый тип
    return_type = method.split(" ")[:-1] 
    #Возвращаем последний элемент разбитой на части строки
    return "".join(return_type[len(return_type)-1])

def find_arguments(method):
    start = method.index("(")+1
    end = method.index(")")
    if not (end-start): return None
    #отделяем основную часть с аргументами
    method = method[start:end]
    #разбиваем аргументы на части
    arguments = method.split(", ")
    for i in range(0, len(arguments)):
        #Вытаскиваем только тип данных
        arguments[i] = " ".join(arguments[i].split(" ")[:-1])
    return arguments

def find_features(method):
    if (method.split(" ")[0] == "static"): return "static"
    #если определяется константный метод, то синтактически он заключен между именем и описания метода
    start = method.index(")")+1
    #Константный метод может быть либо с описанием, либо - без
    if (method[-1] == "}" and "const" in method[start:method.index("{")]): return "const"
    if (method[-1] == ";" and "const" in method[start:method.index(";")]): return "const"
    return None

def parse_cpp_header(filename): # -> list methods

    #Функция парсинга CPP .h файла для нахождения функций классов

    #Регулярное выражение для поиска метода в строке
    method_pattern = r'\b(?:\w+\s+)+\w+\s*\([^)]*\)\s*(?:const)?\s*(?:{|\s*;|= delete)' 
    #Запись файла в переменную
    file = open(filename, "r", encoding="utf-8") 
    #Исходный префикс
    prefix = "" 
    #Символы, которые пропускаются при перебори строк файла
    PassChar = ["#", "/", "\n"] 
    #Возвращаемые методы (результат парсера)
    methods = list()

    #Цикл перебора всех строк в тексте файла
    for line in file:
        try:
            #Избавляемся в начале от пробелов или табуляци
            while (line[0] == " "): line = line[1:]
            if (line[0] == "\t"): line = line.replace("\t", "")

            #Если в начале строки имеются симвлолы, с которыми мы работать не будем, то переходим к следующей строке
            if (line[0] in PassChar): continue
            
            #Убираем все сноски для удобства
            if ("\n" in line): line = line.replace("\n", "")
            #Если нашли имя пространства имен, то записываем его в самое начало префикса
            if (line.split(" ")[0] == "namespace"):
                prefix = line.split(" ")[1]
                continue
            
            #Если нашли строку с описанием имени класса или перечисления, то записываем его в префикс
            if ("class" in line or "enum" in line):
                #Если класс заканчивается на ;, то в нем ничего нет
                if (line[-1] == ";"): continue
                #В других случаях записываем имя класса
                else:
                    #print(line)
                    prefix+=f'::{line.split(" ")[2]}' 
                continue
            
            #Удаляем последний элемент префикса при закрытии скобки в файле
            if (line[0] == "}"):
                prefix = prefix[:prefix.rfind("::")]
                continue
            
            #Нахождение имени, типа, аргументов метода
            method = re.findall(method_pattern, line)
            if (len(method) != 0):
                method = line
                method_name = find_method_name(method)
                return_type = find_return_type(method)
                arguments = find_arguments(method)
                #если метод константный или статичный, то возвращает const или static, в ином случае - None
                feature = find_features(method)
                methods.append(f'{prefix}::{method_name}({return_type}, {arguments}) {feature}')
        except:
            print(line, filename)
    return methods

def get_folders(directory):
    subfolders = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            subfolders.append(item_path)
    return subfolders

def headers_search_and_write(RGKPath="C:\RGK\install\include\RGK"):
    paths = get_folders(RGKPath)
    PassFolders = [".vs"]
    PassFiles = ["C:\\RGK\\install\\include\\RGK\\Utils\\RayTest.h", "C:\\RGK\\install\\include\\RGK\\Utils\\Storage.h"]

    for path in paths:
        path = Path(path)
        file = open("C:\\ParseResult\\"+str(path)[str(path).rindex("\\"):]+".txt", "w")

        for p in path.rglob('*.h'):
            if (str(p) not in PassFiles):
                methods = parse_cpp_header(p)
                file.write(str(p)+"\n")
                for method in methods:
                    file.write(method+"\n")
                file.write("="*100+"\n")

        print("SUCCESS")

headers_search_and_write()
