from vector_db.vector_builder import VectorDatabaseBuilder


def create_db(data):

    # Создаем базу
    builder = VectorDatabaseBuilder()
    vector_db = builder.build_from_texts(data)
    builder.save_database("my_vector_db")

    return vector_db
