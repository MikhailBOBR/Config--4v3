import argparse
import struct
import xml.etree.ElementTree as ET
from xml.dom import minidom

def interpreter(binary_path, result_path, memory_range):
    # Инициализация памяти УВМ и стека
    memory = [0] * 256  # 256 ячеек памяти
    stack = []  # Стек для хранения значений
    memory[5] = 100
    # Чтение бинарного файла
    with open(binary_path, "rb") as f:
        byte_code = f.read()

    i = 0  # Указатель на текущую команду
    while i < len(byte_code):
        # Извлечение команды из первых 4 битов
        command = byte_code[i] & 0x0F
        print(f"Шаг {i}: Команда 0x{command:X}")

        if command == 8:  # Загрузка константы
            B = struct.unpack("<I", byte_code[i+1:i+5])[0]  # Получаем значение константы из 4 байт
            stack.append(B)
            print(f"Загружена константа {B} в стек")
            i += 5

        elif command == 4:  # Чтение из памяти
            address = struct.unpack("<H", byte_code[i+1:i+3])[0]  # Адрес в памяти
            stack.append(memory[address])  # Читаем значение из памяти и кладем на стек
            print(f"Прочитано значение {memory[address]} из памяти по адресу {address} и помещено в стек")
            i += 3

        elif command == 13:  # Запись в память
            address = struct.unpack("<H", byte_code[i+1:i+3])[0]  # Адрес в памяти
            if stack:  # Проверяем, что стек не пуст
                value = stack.pop()  # Забираем элемент с вершины стека
                memory[address] = value  # Записываем значение в память
                print(f"Записано значение {value} из стека в память по адресу {address}")
            else:
                print("Ошибка: стек пуст, невозможно выполнить запись")
            i += 3

        elif command == 0:  # Унарная операция abs()
            if stack:  # Проверяем, что стек не пуст
                value = stack.pop()  # Извлекаем элемент с вершины стека
                result = abs(value)  # Применяем abs()
                stack.append(result)  # Возвращаем результат обратно в стек
                print(f"Применена операция abs() к значению {value}, результат: {result}")
            else:
                print("Ошибка: стек пуст, невозможно выполнить abs()")
            i += 1

        else:
            raise ValueError(f"Неизвестная команда: {command}")

    # Запись результатов в XML файл
    root = ET.Element("memory")
    for address in range(memory_range[0], memory_range[1] + 1):
        memory_element = ET.SubElement(root, "memory_element", address=str(address))
        memory_element.text = str(memory[address])

    # Форматирование XML для читаемого вида
    xml_str = ET.tostring(root, encoding="utf-8")
    parsed_str = minidom.parseString(xml_str)  # Преобразуем в объект DOM для отступов
    pretty_xml_str = parsed_str.toprettyxml(indent="  ")  # Форматируем строку с отступами

    # Запись отформатированного XML в файл
    with open(result_path, "w", encoding="utf-8") as result_file:
        result_file.write(pretty_xml_str)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Интерпретатор для выполнения инструкций из бинарного файла.")
    parser.add_argument("binary_path", help="Путь к бинарному файлу")
    parser.add_argument("result_path", help="Путь к XML-файлу для результатов")
    parser.add_argument("first_index", type=int, help="Первый индекс диапазона памяти")
    parser.add_argument("last_index", type=int, help="Последний индекс диапазона памяти")
    args = parser.parse_args()
    
    interpreter(args.binary_path, args.result_path, (args.first_index, args.last_index))
