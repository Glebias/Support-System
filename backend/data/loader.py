# data/loader.py
import pandas as pd


def load_questions(file_path):
    """Загружает Excel-файл и возвращает DataFrame."""
    df = pd.read_excel(
        file_path
    )  # чтение Excel в DataFrame:contentReference[oaicite:7]{index=7}
    return df
