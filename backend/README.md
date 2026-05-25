# Enterprise Multi-Agent AI Assistant - Backend

This is the backend service for the Enterprise Multi-Agent AI Assistant.

## Prerequisites

- Python `>=3.14`
- [Ollama](https://ollama.com/) running locally or a hosted model endpoint.

## Getting Started

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   Or using your package manager of choice (e.g. `uv`, `poetry`, or `pip`).

2. **Configure your environment**:
   Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```

3. **Run the Application**:
   ```bash
   python -m app.main
   ```
