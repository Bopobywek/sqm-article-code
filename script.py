import os
import javalang
import csv

csv_filename = "data.csv"


def find_overloaded_methods(java_code):
    tree = javalang.parse.parse(java_code)
    method_overloads = {}

    for path, node in tree.filter(javalang.tree.ClassDeclaration):
        class_name = node.name
        method_overloads[class_name] = {}

        for method_declaration in node.methods:
            method_name = method_declaration.name

            if method_name not in method_overloads[class_name]:
                method_overloads[class_name][method_name] = [method_declaration]
            else:
                method_overloads[class_name][method_name].append(method_declaration)

    return method_overloads


def process_directory(source_directory, data_directory, csv_path):
    fields = ["java_file", "ncss", "coco", "cc"]

    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['File', 'NCSS', "Total Cognitive Complexity", "Cyclomatic Complexity", "Overloads"]
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)

        for root, dirs, files in os.walk(data_directory):
            if "all.csv" not in files:
                continue

            try:
                with open(os.path.join(root, "all.csv")) as csv_all:
                    reader_obj = csv.DictReader(csv_all)

                    for row in reader_obj:
                        result = []
                        for metric in fields:
                            result.append(row[metric])

                        file_path = root.replace(data_directory, source_directory) + result[0]

                        with open(file_path, "r", encoding="utf_8") as file:
                            java_code = file.read()

                        overloads = find_overloaded_methods(java_code)

                        counter = 0
                        for class_name, method_overloads in overloads.items():
                            for method_name, overloads_list in method_overloads.items():
                                if len(overloads_list) > 1:
                                    counter = 1
                                    break
                            if counter == 1:
                                break

                        result.append(counter)
                        writer.writerow(result)
                        csvfile.flush()
            except:
                continue


if __name__ == "__main__":
    base_path = os.environ.get("DATASET_PATH")
    source_dir = os.path.join(base_path, "github")
    data_dir = os.path.join(base_path, "data")
    process_directory(source_dir, data_dir, "data.csv")
