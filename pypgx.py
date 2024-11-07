import os
import pandas as pd
import zipfile

def extract_data_from_pharma_directories(root_directory):
    data = []  # Список для хранения всех извлечённых данных

    # Перебор папок в корневой директории
    for pharma_dir in os.listdir(root_directory):
        # Проверка, что папка соответствует шаблону *.MGI.Pharma
        if pharma_dir.endswith(".MGI.Pharma") and pharma_dir.split(".")[0].isdigit():
            pharma_path = os.path.join(root_directory, pharma_dir)
            
            # Проверяем, что это директория
            if os.path.isdir(pharma_path):
                # Ищем поддиректорию вида *.MGI.pypgx
                pypgx_dirs = [d for d in os.listdir(pharma_path) if d.endswith(".MGI.pypgx")]
                
                for pypgx_dir in pypgx_dirs:
                    pypgx_path = os.path.join(pharma_path, pypgx_dir)
                    
                    # Проверка, что это действительно директория
                    if os.path.isdir(pypgx_path):
                        # Ищем папки вида *-!-pipeline
                        for pipeline_dir in os.listdir(pypgx_path):
                            parts = pipeline_dir.split("-")
                            if len(parts) >= 2 and parts[1].isalnum():  # Проверка на формат *-!-pipeline
                                people = parts[0]  # Значение *, например, 000005008000
                                gen = parts[1]      # Значение !, например, A23b4

                                pipeline_path = os.path.join(pypgx_path, pipeline_dir)
                                
                                # Проверяем, что это директория и ищем архив results.zip
                                if os.path.isdir(pipeline_path):
                                    results_zip_path = os.path.join(pipeline_path, "results.zip")
                                    
                                    if os.path.exists(results_zip_path):
                                        # Открываем и распаковываем results.zip
                                        with zipfile.ZipFile(results_zip_path, 'r') as zip_ref:
                                            zip_ref.extractall(pipeline_path)
                                            
                                            # Ищем папку внутри архива
                                            for inner_dir in os.listdir(pipeline_path):
                                                inner_path = os.path.join(pipeline_path, inner_dir)
                                                
                                                # Проверяем, что это директория с двумя файлами
                                                if os.path.isdir(inner_path):
                                                    data_file_path = os.path.join(inner_path, "data.tsv")
                                                    
                                                    # Проверка на наличие файла data.tsv
                                                    if os.path.exists(data_file_path):
                                                        # Чтение данных из data.tsv
                                                        try:
                                                            df = pd.read_csv(data_file_path, sep="\t", usecols=["Genotype", "Phenotype"])
                                                            
                                                            # Добавление данных в список
                                                            for _, row in df.iterrows():
                                                                data.append({
                                                                    "people": people,
                                                                    "gen": gen,
                                                                    "Genotype": row["Genotype"],
                                                                    "Phenotype": row["Phenotype"]
                                                                })
                                                        except Exception as e:
                                                            print(f"Ошибка при обработке файла {data_file_path}: {e}")
                                    else:
                                        print(f"Файл results.zip не найден в {pipeline_path}")

    # Создание итоговой таблицы и сохранение её как CSV
    if data:
        result_df = pd.DataFrame(data)
        output_file = os.path.join(root_directory, "final_data.csv")
        result_df.to_csv(output_file, index=False)
        print(f"Сохранён итоговый файл: {output_file}")
    else:
        print("Данные не найдены.")

# Пример использования
root_directory = r"C:\MyPythonWorks\Pharma"  # Укажите путь к корневой директории
extract_data_from_pharma_directories(root_directory)
