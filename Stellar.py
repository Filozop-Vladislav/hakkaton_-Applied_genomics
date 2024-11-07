import os
import pandas as pd
import re

def process_alleles_files_in_pharma_directories(root_directory):
    data = []  # Список для хранения данных из всех файлов

    # Проходимся по каждой папке в указанной директории
    for pharma_dir in os.listdir(root_directory):
        # Проверяем, что имя папки заканчивается на .MGI.Pharma
        match = re.match(r'^(\d+)\.MGI\.Pharma$', pharma_dir)
        if match:
            pharma_path = os.path.join(root_directory, pharma_dir)
            numeric_prefix = match.group(1)  # Извлекаем числовую часть

            print(f"Обрабатываем директорию: {pharma_path}")  # Отладочный вывод

            # Проверяем, что это действительно директория
            if os.path.isdir(pharma_path):
                # Ищем папку, содержащую .MGI.StellarPGx
                stellar_pgx_dir = None
                for subdir in os.listdir(pharma_path):
                    if re.match(r'^\d+\.MGI\.StellarPGx$', subdir):
                        stellar_pgx_dir = os.path.join(pharma_path, subdir)
                        print(f"Найдена папка StellarPGx: {stellar_pgx_dir}")  # Отладочный вывод
                        break
                
                # Если папка .MGI.StellarPGx найдена
                if stellar_pgx_dir and os.path.isdir(stellar_pgx_dir):
                    # Проходим по всем файлам в папке .MGI.StellarPGx
                    for filename in os.listdir(stellar_pgx_dir):
                        if filename.endswith(".alleles"):
                            filepath = os.path.join(stellar_pgx_dir, filename)

                            print(f"Обрабатываем файл: {filepath}")  # Отладочный вывод

                            # Извлечение названия гена из имени файла
                            gene_match = re.search(r'_([a-zA-Z0-9]+)\.alleles$', filename)
                            gene_name = gene_match.group(1) if gene_match else "Unknown"  # Если не найдено, ставим "Unknown"

                            # Читаем файл .alleles
                            with open(filepath, 'r') as file:
                                content = file.readlines()
                                
                                # Ищем строки "Metaboliser status:" и "Result:"
                                metaboliser_status = None
                                result_status = None
                                for i, line in enumerate(content):
                                    if "Metaboliser status:" in line:
                                        # Проверяем, есть ли следующая строка и содержит ли она статус
                                        if i + 1 < len(content):
                                            metaboliser_status = content[i + 1].strip()
                                            print(f"Найден Metaboliser status: {metaboliser_status}")  # Отладочный вывод
                                    elif "Result:" in line:
                                        # Проверяем, есть ли следующая строка и содержит ли она статус
                                        if i + 1 < len(content):
                                            result_status = content[i + 1].strip()
                                            print(f"Найден Result: {result_status}")  # Отладочный вывод
                                
                                # Если статусы найдены и не пустые, добавляем информацию в список
                                if metaboliser_status and result_status:
                                    data.append({
                                        "File": numeric_prefix,        # Сохраняем только числовую часть
                                        "Metaboliser Status": metaboliser_status,
                                        "Result": result_status,
                                        "Gene": gene_name              # Сохраняем название гена
                                    })

    # Создаем единый DataFrame и сохраняем его как CSV файл
    if data:
        result_df = pd.DataFrame(data)
        output_file = os.path.join(root_directory, "combined_results.csv")
        result_df.to_csv(output_file, index=False)
        print(f"Сохранён единый файл: {output_file}")
    else:
        print("Не найдено подходящих файлов с 'Metaboliser status:' и 'Result:'.")

# Задайте путь к вашей папке
process_alleles_files_in_pharma_directories(r"C:\MyPythonWorks\Pharma")



