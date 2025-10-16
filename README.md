# Smart Support Backend

This repository contains the backend for the Smart Support project. Below are the instructions to set up and run the project.
Presentation: SmartSupport
## Prerequisites
- Python 3.8 or higher
- Docker (optional, for containerized deployment)
- Poetry (for dependency management)


## Setup

### 1. Clone the Repository
Clone the repository to your local machine:
```bash
git clone https://github.com/your-repo/smart-support.git
cd smart-support
```

### 2. Environment Variables
Create a `.env` file in the root of the project and add the required environment variables.
```
API_KEY = ...
BASE_URL = ...
```
### 3. Environment Variables
Create a `smart_support_vtb_belarus_faq_final.xlsl` with database.*smart_support_vtb_belarus_faq_final*

## Running the Project


### 1. Docker (Optional)
If you prefer to run the project in a containerized environment, use Docker:
```bash
docker-compose up --build
```
## Зарегестрируйтесь как админ пароль и почта одинакове: adsd@asd.asd

## Project Structure
- `backend/`: Contains the backend code, including classification, data loading, and vector database logic.
- `smart-support/`: Contains the frontend code (if applicable).
- `pyproject.toml`: Poetry configuration for dependencies and project settings.
- `docker-compose.yml`: Docker configuration for containerized deployment.

## Video

https://github.com/user-attachments/assets/cb6b1259-c311-47a8-bb4c-ee78cba1fb27


