import os
import re
import pandas as pd

# Укажите путь к основной директории
base_path = r"C:\MyPythonWorks\Pharma"

# Создаем пустой список для итоговых данных
columns = ["human", "gen", "genotype"]
results = []

# Проходим по всем директориям и подпапкам
for root, dirs, files in os.walk(base_path):
    # Проверяем, что мы в нужной директории вида *.MGI.aldy
    if re.search(r"\d+\.MGI\.aldy$", root):
        # Извлекаем число (human) из имени директории
        human_match = re.search(r"(\d+)\.MGI\.aldy$", root)
        if not human_match:
            continue
        human_id = human_match.group(1)
        
        # Проходим по всем файлам в этой директории
        for file in files:
            # Проверяем, что файл соответствует шаблону *.?.out
            if re.match(r"\d+\.\w+\.out$", file):
                file_path = os.path.join(root, file)
                
                # Извлекаем gen (часть имени файла между точками)
                gen_match = re.search(r"\d+\.(\w+)\.out$", file)
                if not gen_match:
                    continue
                gen_id = gen_match.group(1)
                
                # Открываем файл и анализируем его содержимое
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                # Извлекаем нужные строки для genotype
                genotype = ""
                # Регулярное выражение для поиска строки "Best {gen_id.upper()} star-alleles for {human_id}:"
                genotype_pattern = re.compile(rf"Best {gen_id.upper()} star-alleles for {human_id}:")
                found = False
                for i, line in enumerate(lines):
                    if genotype_pattern.search(line):
                        # Ищем следующую строку для получения генотипа
                        if i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            genotype_match = re.match(r"^\s*(\d+):\s*(.*)\s*\(confidence=.*\)$", next_line)
                            if genotype_match:
                                genotype = genotype_match.group(2)
                                found = True
                                break
                
                # Если не нашли нужную строку, выводим сообщение
                if not found:
                    print(f"Строка 'Best {gen_id.upper()} star-alleles for {human_id}:' не найдена в файле {file_path}")

                # Добавляем данные в список
                results.append({
                    "human": human_id,
                    "gen": gen_id,
                    "genotype": genotype
                })

# Преобразуем список в DataFrame
results_df = pd.DataFrame(results, columns=columns)

# Сохраняем результаты в CSV файл
results_df.to_csv("analyz.csv", index=False, encoding='utf-8')
print("Таблица сохранена в файл 'analyz.csv'.")





