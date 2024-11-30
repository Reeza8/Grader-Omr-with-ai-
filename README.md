# FastAPI Grading System

A Python-based ORM project for grading test sheets with 160 multiple-choice questions. This system uses AI models to read handwritten student codes on answer sheets, linking exam results directly to the respective students in the database. The answer sheet header is customizable, allowing educators to add school logos or other relevant information.

## Features
- **AI-based Handwriting Recognition**: Links student exam results to their IDs.
- **Customizable Answer Sheet**: Tailored to meet institutional needs.
- **FastAPI Backend**: Provides a robust and scalable API.
- **SQLite Database**: Simple and easy-to-setup storage.

## Prerequisites
- Python 3.10+
- Virtual environment (recommended)
- SQLite (included with Python)

## Installation
1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd fastApiProject
    ```
2. Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```
3. Install dependencies:
    ```bash
    pip install -r requirement.txt
    ```
4. Initialize the database:
    ```bash
    python main.py
    ```

## Usage
1. Start the FastAPI server:
    ```bash
    uvicorn main:app --reload
    ```
2. Access the API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
3. Customize the answer sheet header as needed.

## Project Structure
```plaintext
fastApiProject/
├── Exam/
│   ├── Api/            # API endpoints for exam-related operations
│   ├── Schema/         # Pydantic models for data validation
│   ├── models.py       # Database models for exams
├── User/               # User management modules
├── utils/              # Helper functions and utilities
├── main.py             # Entry point of the application
├── model.onnx          # AI model for handwriting recognition
├── model_quantized.onnx # Optimized AI model for production
├── myDb.db             # SQLite database file
├── schema.py           # Shared schemas across the project
├── requirement.txt     # Python dependencies
