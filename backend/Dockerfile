# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory
WORKDIR /app/backend

# Copy the pyproject.toml file
COPY pyproject.toml ./

# Install dependencies using Poetry (export to reqs)
RUN pip install --no-cache-dir poetry
RUN poetry self add poetry-plugin-export  # <-- Добавьте: Установка плагина для export
RUN poetry export --format requirements.txt --output requirements.txt --without-hashes  # <-- Правильный синтаксис
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set the command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
