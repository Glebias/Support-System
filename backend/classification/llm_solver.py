# llm_solver.py
from utils.config import client
from typing import Dict, List, Tuple, Any
import json

def figuare_diffficults(question: str, data: List[Dict[str, Any]]) -> Tuple[str, str, str, float]:
    """Использует LLM для классификации сложных случаев."""

    system_prompt = """
    Ты помощник сотрудника, который помогает классифицировать вопросы пользователя.
    На вход тебе подается вопрос пользователя и список похожих вопросов с их характеристиками.
    Выбери наиболее подходящую категорию из предоставленных вариантов.

    Формат вывода: ТОЛЬКО JSON в формате:
    {
        "Основная категория": "название",
        "Подкатегория": "название",
        "Шаблонный ответ": "текст",
        "Score": 0.95
    }
    """

    user_prompt = f"""
    Вопрос пользователя: {question}

    Похожие вопросы и их категории:
    {json.dumps(data, ensure_ascii=False, indent=2)}

    Выбери наиболее подходящую категорию из списка выше.
    """

    try:
        resp = client.chat.completions.create(
            model="Qwen2.5-72B-Instruct-AWQ",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            top_p=0.9,
            max_tokens=512,
        )

        response_content = resp.choices[0].message.content.strip()

        # Парсим JSON ответ
        try:
            result = json.loads(response_content)
            return (
                result["Основная категория"],
                result["Подкатегория"],
                result["Шаблонный ответ"],
                result.get("Score", 0.8)  # дефолтное значение если нет Score
            )
        except json.JSONDecodeError:
            # Если LLM не вернул JSON, используем первый результат
            print("⚠️ LLM не вернул JSON, использую первый результат")
            return (
                data[0]["Основная категория"],
                data[0]["Подкатегория"],
                data[0]["Шаблонный ответ"],
                data[0]["Score"]
            )

    except Exception as e:
        print(f"Ошибка в LLM: {e}")
        # Возвращаем первый результат как fallback
        return (
            data[0]["Основная категория"],
            data[0]["Подкатегория"],
            data[0]["Шаблонный ответ"],
            data[0]["Score"]
        )
