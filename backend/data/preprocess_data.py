import pandas as pd
from typing import List, Dict, Tuple


def preprocess_text(text):
    """Простейшая предобработка текста перед векторизацией."""
    # text = str(text).strip().lower()
    # Здесь можно добавить удаление пунктуации, стоп-слов и т.п.
    return text


def encode_categorical_features(
    dataset: pd.DataFrame, features: List[str]
) -> Tuple[pd.DataFrame, Dict[str, Dict]]:
    """
    Преобразует категориальные признаки в числа 0, 1, 2, 3...

    Args:
        dataset: DataFrame с данными
        features: список названий фичей для кодирования

    Returns:
        Tuple[pd.DataFrame, Dict[str, Dict]]:
            - DataFrame с закодированными фичами
            - словарь с mapping для каждой фичи
    """

    # Создаем копию датасета чтобы не изменять оригинал
    encoded_dataset = dataset.copy()
    mappings = {}

    for feature in features:
        if feature not in encoded_dataset.columns:
            print(f"⚠️ Фича '{feature}' не найдена в датасете")
            continue

        # Получаем уникальные значения и сортируем их
        unique_values = sorted(encoded_dataset[feature].unique())

        # Создаем mapping: значение -> число
        mapping = {value: idx for idx, value in enumerate(unique_values)}
        mappings[feature] = mapping

        # Применяем преобразование
        encoded_dataset[feature] = encoded_dataset[feature].map(mapping)

        print(f"✅ Закодирована фича '{feature}': {len(unique_values)} категорий")
        print(f"   Mapping: {mapping}")

    return encoded_dataset, mappings


# Функция для обратного преобразования
def decode_categorical_features(
    dataset: pd.DataFrame, mappings: Dict[str, Dict]
) -> pd.DataFrame:
    """
    Обратное преобразование чисел в категориальные значения.

    Args:
        dataset: DataFrame с закодированными данными
        mappings: словарь mapping'ов от encode_categorical_features

    Returns:
        pd.DataFrame: DataFrame с восстановленными категориями
    """
    decoded_dataset = dataset.copy()

    for feature, mapping in mappings.items():
        if feature in decoded_dataset.columns:
            # Создаем обратный mapping
            reverse_mapping = {v: k for k, v in mapping.items()}
            decoded_dataset[feature] = decoded_dataset[feature].map(reverse_mapping)

    return decoded_dataset


def get_ready_data(data):

    data["Пример вопроса"] = data["Пример вопроса"].apply(preprocess_text)
    encoded_data, mappings = encode_categorical_features(
        data, ["Основная категория", "Подкатегория"]
    )

    return encoded_data, mappings
