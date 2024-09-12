import csv
import os

from config.settings import USE_CSV


def start_csv(csv_name):
    if USE_CSV:
        # clear errors
        # with open(f'results/error_{csv_name}.csv', "w") as csv_file:
        #     csv_file.write("")

        # copy

        source_file = "config/wallets.csv"
        destination_file = f'results/{csv_name}.csv'
            # Read data from the source CSV file
        with open(source_file, 'r') as source_csv:
            source_lines = source_csv.readlines()

        # Write data to the destination CSV file
        with open(destination_file, 'w') as dest_csv:
            dest_csv.writelines(source_lines)


def write_csv_success(index, data):
    if USE_CSV:

        index = index + 1
        function_name = data['function']
        csv_name = data['csv_name']

        with open(f'results/{csv_name}.csv', 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)

            if index < len(rows):
                rows[index][5] = data['status']
                rows[index][6] = function_name
                rows[index][7] = data['date']

        with open(f'results/{csv_name}.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

def write_csv_error(csv_name, data):
    if USE_CSV:
        with open(f'results/error_{csv_name}.csv', 'a') as file:
            writer = csv.writer(file)

            if file.tell() == 0:
                writer.writerow(['address', 'private_key','function','params', 'error', 'time'])

            writer.writerow(data)



def write_csv_volume(csv_name, data):
    if USE_CSV:

        with open(f'results/{csv_name}.csv', 'a') as file:
            writer = csv.writer(file)

            if file.tell() == 0:
                writer.writerow(['address', 'private_key','path','total_volume USD', 'tx_sum(w-ot approves)', 'start_time','end_time'])

            writer.writerow(data)




def get_csv_separator():
    with open('config/wallets.csv', newline='') as csvfile:
        return ';' if ';' in csvfile.readline() else ','


def clear_mark_csv(csv_filename='results/marks.csv'):

    # Specify the path to the file you want to check

    # Check if the file exists
    if os.path.exists(csv_filename):
        os.remove(csv_filename)

def save_csv_marks(data, csv_filename='results/marks.csv'):
    # Проверка на существование файла
    file_exists = os.path.isfile(csv_filename)

    # Открытие файла в режиме добавления
    with open(csv_filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
        print(data)
        # Записываем заголовок только если файл не существует
        if not file_exists:
            writer.writeheader()
        writer.writerows(data)

def save_csv_balance(data, csv_filename='results/balance.csv'):
    # Проверка на существование файла
    file_exists = os.path.isfile(csv_filename)

    # Открытие файла в режиме добавления
    with open(csv_filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
        # Записываем заголовок только если файл не существует
        if not file_exists:
            writer.writeheader()
        writer.writerows(data)
