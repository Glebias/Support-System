# db/vector_db.py
import numpy as np
import pickle
from typing import List, Tuple, Dict, Any, Optional
from sklearn.metrics.pairwise import cosine_similarity
from vectorization.vectorizer import Embedder


class VectorDB:
    def __init__(self, dimension: int):
        """
        Summary: Инициализирует векторную базу данных с заданной размерностью.
        Input:
            dimension (int): Размерность векторов в базе данных.
        Output:
            None
        """
        self.dimension = dimension
        self.vectors = np.array([], dtype="float32").reshape(0, dimension)
        self.texts: List[str] = []
        self.metadata: List[Dict] = []
        self.embedder = Embedder()

    def add_vector(
        self, vector: List[float], text: str, metadata: Optional[Dict] = None
    ):
        """
        Summary: Добавляет один вектор в базу данных.
        Input:
            vector (List[float]): Вектор для добавления.
            text (str): Текст, связанный с вектором.
            metadata (Optional[Dict]): Метаданные, связанные с вектором.
        Output:
            None
        """
        if len(vector) != self.dimension:
            raise ValueError(
                f"Размерность вектора {len(vector)} не совпадает с размерностью базы {self.dimension}"
            )

        vector_array = np.array(vector, dtype="float32").reshape(1, -1)

        if self.vectors.size == 0:
            self.vectors = vector_array
        else:
            self.vectors = np.vstack([self.vectors, vector_array])

        self.texts.append(text)
        self.metadata.append(metadata or {})

    def add_batch(
        self,
        vectors: List[List[float]],
        texts: List[str],
        metadata_list: Optional[List[Dict]] = None,
    ):
        """
        Summary: Добавляет батч векторов в базу данных.
        Input:
            vectors (List[List[float]]): Список векторов для добавления.
            texts (List[str]): Список текстов, связанных с векторами.
            metadata_list (Optional[List[Dict]]): Список метаданных, связанных с векторами.
        Output:
            None
        """
        if len(vectors) != len(texts):
            raise ValueError("Количество векторов и текстов должно совпадать")

        if metadata_list is None:
            metadata_list = [{}] * len(vectors)

        for vector, text, metadata in zip(vectors, texts, metadata_list):
            self.add_vector(vector, text, metadata)

    def get_vectors_by_texts(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Summary: Возвращает векторы, соответствующие заданным текстам.
        Input:
            texts (List[str]): Список текстов для поиска векторов.
        Output:
            List[Optional[List[float]]]: Список векторов, соответствующих текстам.
        """
        if self.vectors.size == 0:
            return [None] * len(texts)

        # Создаем словарь для быстрого поиска текст -> вектор
        text_to_vector = {}
        for i, text in enumerate(self.texts):
            text_to_vector[text] = self.vectors[i]

        # Возвращаем векторы в той же последовательности
        result_vectors = []
        for text in texts:
            if text in text_to_vector:
                result_vectors.append(text_to_vector[text].tolist())
            else:
                result_vectors.append(None)

        return result_vectors

    def search(
        self, query_vector: List[float], top_k: int = 5
    ) -> List[Tuple[float, str, Dict]]:
        """
        Summary: Ищет ближайшие векторы, используя косинусное сходство.
        Input:
            query_vector (List[float]): Вектор для поиска.
            top_k (int): Количество ближайших векторов для возврата.
        Output:
            List[Tuple[float, str, Dict]]: Список кортежей с косинусным сходством, текстом и метаданными.
        """
        if self.vectors.size == 0:
            return []

        query_array = np.array(query_vector, dtype="float32").reshape(1, -1)

        # Вычисляем косинусное сходство
        similarities = cosine_similarity(query_array, self.vectors)[0]

        # Получаем индексы top_k наиболее похожих
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # фильтруем совсем непохожие
                results.append(
                    (
                        float(
                            similarities[idx]
                        ),  # косинусное сходство (1.0 = идентичные)
                        self.texts[idx],
                        self.metadata[idx],
                    )
                )

        return results

    def search_by_text(
        self, query_text: str, top_k: int = 5
    ) -> List[Tuple[float, str, Dict]]:
        """
        Summary: Ищет по текстовому запросу.
        Input:
            query_text (str): Текст для поиска.
            top_k (int): Количество ближайших векторов для возврата.
        Output:
            List[Tuple[float, str, Dict]]: Список кортежей с косинусным сходством, текстом и метаданными.
        """
        query_vector = self.embedder.encode(query_text)
        if query_vector is None:
            return []
        return self.search(query_vector, top_k)

    def get_stats(self) -> Dict[str, Any]:
        """
        Summary: Возвращает статистику базы данных.
        Input:
            None
        Output:
            Dict[str, Any]: Словарь с статистикой базы данных.
        """
        return {
            "total_vectors": len(self.texts),
            "dimension": self.dimension,
            "texts_count": len(self.texts),
            "metadata_count": len(self.metadata),
        }

    def save(self, base_path: str):
        """
        Summary: Сохраняет всю векторную базу на диск.
        Input:
            base_path (str): Путь для сохранения файла.
        Output:
            None
        """
        data = {
            "vectors": self.vectors.tolist(),
            "texts": self.texts,
            "metadata": self.metadata,
            "dimension": self.dimension,
        }

        with open(f"{base_path}.pkl", "wb") as f:
            pickle.dump(data, f)

    @classmethod
    def load(cls, base_path: str):
        """
        Summary: Загружает векторную базу с диска.
        Input:
            base_path (str): Путь к файлу для загрузки.
        Output:
            VectorDB: Экземпляр класса VectorDB с загруженными данными.
        """
        with open(f"{base_path}.pkl", "rb") as f:
            data = pickle.load(f)

        db = cls(data["dimension"])
        db.vectors = np.array(data["vectors"], dtype="float32")
        db.texts = data["texts"]
        db.metadata = data["metadata"]

        return db
