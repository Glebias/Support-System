# vectorization/vectorizer.py
from utils.config import client
from typing import List, Optional


class Embedder:
    def __init__(self, model_name: str = "bge-m3"):
        self.client = client
        self.model_name = model_name
        self._dimension: Optional[int] = None

    def encode(self, text: str) -> Optional[List[float]]:
        """
        Преобразует текст в вектор.
        """
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=[text],
            )
            embedding = response.data[0].embedding
            # Кэшируем размерность при первом вызове
            if self._dimension is None:
                self._dimension = len(embedding)
            return embedding
        except Exception as e:
            print(f"Ошибка при векторизации текста '{text[:50]}...': {e}")
            return None

    def encode_batch(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """
        Векторизует список текстов с батчингом.
        """
        vectors = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            print(
                f"Векторизация батча {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}"
            )

            for text in batch:
                vector = self.encode(text)
                if vector is not None:
                    vectors.append(vector)
                else:
                    # Добавляем нулевой вектор для пропущенных текстов
                    vectors.append([0.0] * self.get_embedding_dimension())

        return vectors

    def get_embedding_dimension(self) -> int:
        """
        Определяет размерность эмбеддингов.
        """
        if self._dimension is None:
            # Определяем размерность на тестовом тексте
            test_vector = self.encode("test")
            if test_vector:
                self._dimension = len(test_vector)
            else:
                raise ValueError("Не удалось определить размерность эмбеддингов")
        return self._dimension
