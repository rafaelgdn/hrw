import pandas as pd
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

csv_path = os.path.join(current_dir, "hrw_news.csv")
excel_path = os.path.join(current_dir, "hrw_news.xlsx")

df = pd.read_csv(csv_path)

df.to_excel(excel_path, index=False)
print(f"Arquivo Excel criado com sucesso: {excel_path}")
