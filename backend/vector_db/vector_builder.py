# vector_builder.py
from vectorization.vectorizer import Embedder
from vector_db.vector_db import VectorDB
from typing import List, Dict, Optional
import time


class VectorDatabaseBuilder:
    """
    Фабрика для создания векторной базы без FAISS.
    """

    def __init__(self, model_name: str = "bge-m3"):
        """
        Summary: Инициализирует фабрику для создания векторной базы.
        Input:
            model_name (str): Имя модели для эмбеддинга.
        Output:
            None
        """
        self.embedder = Embedder(model_name)
        self.vector_db = None

    def build_from_texts(
        self, texts: List[str], metadata_list: Optional[List[Dict]] = None
    ) -> VectorDB:
        """
        Summary: Создает полную векторную базу из списка текстов.
        Input:
            texts (List[str]): Список текстов для векторизации.
            metadata_list (Optional[List[Dict]]): Список метаданных для текстов.
        Output:
            VectorDB: Созданная векторная база.
        """
        if metadata_list is None:
            metadata_list = [{} for _ in texts]

        print(f"🚀 Начало построения векторной базы для {len(texts)} текстов...")

        # Определяем размерность
        print("📏 Определение размерности эмбеддингов...")
        dimension = self.embedder.get_embedding_dimension()
        print(f"✅ Размерность эмбеддингов: {dimension}")

        # Создаем векторную базу
        self.vector_db = VectorDB(dimension)

        # Векторизуем и добавляем в базу
        print("🔧 Векторизация текстов...")
        start_time = time.time()

        vectors = self.embedder.encode_batch(texts)

        # Фильтруем успешные векторизации
        valid_data = []
        for i, (vector, text, metadata) in enumerate(
            zip(vectors, texts, metadata_list)
        ):
            if vector and any(
                v != 0 for v in vector
            ):  # проверяем что вектор не нулевой
                valid_data.append((vector, text, metadata))
            else:
                print(f"⚠️ Пропущен текст {i}: {text[:50]}...")

        # Добавляем валидные данные в базу
        if valid_data:
            vectors_valid, texts_valid, metadata_valid = zip(*valid_data)
            self.vector_db.add_batch(
                list(vectors_valid), list(texts_valid), list(metadata_valid)
            )

        elapsed_time = time.time() - start_time
        print(
            f"✅ Векторная база создана! Обработано {len(valid_data)}/{len(texts)} текстов"
        )
        print(f"⏱️ Время выполнения: {elapsed_time:.2f} секунд")

        return self.vector_db

    def save_database(self, base_path: str):
        """
        Summary: Сохраняет созданную векторную базу.
        Input:
            base_path (str): Путь для сохранения файла.
        Output:
            None
        """
        if self.vector_db:
            self.vector_db.save(base_path)
            print(f"💾 Векторная база сохранена: {base_path}.pkl")
        else:
            raise ValueError("Векторная база не создана")
