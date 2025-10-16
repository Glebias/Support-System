from fastapi import FastAPI
from pydantic import BaseModel
from backend.classification.classify import classify_text

# Создаем экземпляр приложения FastAPI
app = FastAPI()


# Модель запроса
class RequestModel(BaseModel):
    question: str


# Модель ответа
class ResponseModel(BaseModel):
    score: float
    offered_responce: str
    main_category: str
    sub_category: str


@app.post("/process", response_model=ResponseModel)
async def process_string(request: RequestModel):
    """
    Обрабатывает входную строку и возвращает обработанную строку.

    Args:
        request (RequestModel): Модель запроса, содержащая входную строку.

    Returns:
        ResponseModel: Модель ответа, содержащая обработанную строку.
    """
    # Логика обработки строки
    # В данном примере строка преобразуется в верхний регистр
    response = classify_text(request.question)

    # Возвращаем модель ответа с обработанной строкой
    return ResponseModel(
        score=response[3],
        offered_responce=response[2],
        main_category=response[0],
        sub_category=response[1],
    )
