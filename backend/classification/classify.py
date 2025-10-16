# classify.py
from classification.llm_solver import figuare_diffficults
from data.loader import load_questions
from vector_db.vector_db import VectorDB
import pandas as pd
from typing import Tuple, List, Dict, Any
from vectorization.vectorizer import Embedder

# Embedder is used to vectorize text for similarity search.
embedder = Embedder()

def find_solve_pattern(question: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Finds similar questions in the dataset and returns their details.

    Args:
        question (str): The input question to search for.
        top_k (int): The number of top similar questions to retrieve.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing details of similar questions,
                              including their scores and metadata.
    """

    df = load_questions("smart_support_vtb_belarus_faq_final.xlsx")
    vec_db = VectorDB.load("my_vector_db")

    res = vec_db.search_by_text(query_text=question, top_k=top_k)

    res_d = []
    for data in res:
        matching_rows = df[df["Пример вопроса"] == data[1]]
        if not matching_rows.empty:
            pattern = matching_rows.iloc[0].to_dict()
            pattern["Score"] = data[0]
            res_d.append(pattern)
        else:
            print(f"⚠️ Вопрос не найден в базе: {data[1]}")

    return res_d

def classify_text(text: str) -> Tuple[str, str, str, float]:
    """
    Classifies the input text into categories and returns the most relevant answer.

    Args:
        text (str): The input text to classify.

    Returns:
        Tuple[str, str, str, float]: A tuple containing the main category, subcategory,
                                      pattern answer, and similarity score.
    """

    results = find_solve_pattern(text)

    if not results:
        raise ValueError("Не найдено похожих вопросов")

    # If the top result has a low score, use a fallback classification method.
    
    main_cat = results[0]["Основная категория"]
    sub_cat = results[0]["Подкатегория"]
    pattern = results[0]["Шаблонный ответ"]
    score = results[0]["Score"]

    return main_cat, sub_cat, pattern, score
