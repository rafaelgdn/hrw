import csv
import os
from datetime import datetime
import pandas as pd
import re
import sys

csv.field_size_limit(sys.maxsize)


def clean_text(text):
    return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)


def process_csv(input_file):
    data_by_year = {}

    with open(input_file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cleaned_row = {k: clean_text(v) for k, v in row.items()}

            date = datetime.strptime(cleaned_row["Date"], "%m/%d/%Y")
            year = date.year

            if year not in data_by_year:
                data_by_year[year] = []
            data_by_year[year].append(cleaned_row)

    for year, data in data_by_year.items():
        os.makedirs(f"output/{year}", exist_ok=True)

        csv_file = f"output/{year}/hrw-{year}.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

            writer.writeheader()
            for row in data:
                writer.writerow(row)

        excel_file = f"output/{year}/hrw-{year}.xlsx"
        df = pd.DataFrame(data)
        df.to_excel(excel_file, index=False, engine="openpyxl")

    print("Processamento concluído. Arquivos CSV e Excel criados por ano.")


current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, "hrw_news.csv")
process_csv(csv_path)
