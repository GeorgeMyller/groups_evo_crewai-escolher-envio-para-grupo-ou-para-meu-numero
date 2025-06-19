# WhatsApp Group Manager and Summarizer

## About the Project

The WhatsApp Group Manager and Summarizer is a Python application designed to help users manage their WhatsApp groups efficiently. It provides features for fetching group information, scheduling automated message summaries using AI, and interacting with the Evolution API for WhatsApp. The project leverages CrewAI for intelligent summarization tasks and Streamlit for an interactive web interface.

## Technologies Used

*   Python 3.12+
*   Streamlit (for the web UI)
*   CrewAI (for AI-powered summarization)
*   Evolution API (for WhatsApp communication)
*   Docker & Docker Compose (for containerization)
*   Pandas (for data manipulation)
*   python-dotenv (for environment variable management)
*   The project uses an OS-level task scheduler via the `TaskSchedulingService` for background tasks.

## Project Structure

The project follows a clean architecture pattern to separate concerns:

*   `src/whatsapp_manager/`: Main package root.
    *   `core/`: Contains the core business logic, including:
        *   `controllers/`: Handles incoming requests and orchestrates actions.
        *   `models/`: Defines data structures (e.g., Group, Message).
        *   `services/`: Implements business rules and orchestrates tasks (e.g., summary generation, group data fetching).
    *   `infrastructure/`: Manages interactions with external services and tools:
        *   `api/`: Wrappers for external APIs (e.g., Evolution API).
        *   `persistence/`: Handles data storage and retrieval (e.g., CSV files for group settings).
        *   `scheduling/`: Manages task scheduling using OS-level schedulers.
        *   `messaging/`: Components related to message sending abstractions.
    *   `presentation/web/`: Contains the Streamlit web application:
        *   `app.py`: The main landing page of the Streamlit app.
        *   `pages/`: Individual pages of the Streamlit application.
        *   `assets/`: Static files like CSS.
    *   `shared/`: Common utilities, constants, and modules used across the application:
        *   `utils/`: General utility functions (date formatting, text processing, etc.).
        *   `constants/`: Application-wide constants.

## Getting Started

### Prerequisites

*   Python 3.12 or higher
*   Docker Desktop (or Docker Engine with Docker Compose)
*   An OS-level mechanism for scheduling tasks if using the summary scheduling feature outside Docker (e.g., cron on Linux/macOS, Task Scheduler on Windows). The application will attempt to create these tasks.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-name>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    The project uses `pyproject.toml` for dependency management with setuptools. To install the project in editable mode along with its dependencies:
    ```bash
    pip install -e .
    ```

4.  **Configure environment variables:**
    Create a `.env` file in the project root. Copy the contents of `.env.example` and fill in your specific details.
    Necessary variables include:
    ```env
    # Evolution API Settings
    EVO_BASE_URL=http://localhost:8081
    EVO_API_TOKEN=your_evolution_api_token
    EVO_INSTANCE_NAME=your_instance_name
    EVO_INSTANCE_TOKEN=your_instance_token

    # CrewAI Language Model (Example: OpenAI)
    # OPENAI_API_BASE_URL=your_openai_api_base_url (optional, for custom endpoints like LM Studio)
    OPENAI_MODEL_NAME=gpt-4-turbo-preview # Example model, adjust as needed
    OPENAI_API_KEY=your_openai_api_key

    # Your WhatsApp number for personal notifications (optional, e.g., 351XXXXXXXXX)
    # WHATSAPP_NUMBER=
    ```

### Running the Application

*   **With Streamlit (locally):**
    Ensure your virtual environment is activated and you are in the project root directory.
    ```bash
    streamlit run src/whatsapp_manager/presentation/web/app.py
    ```
    The application should open in your web browser (usually at `http://localhost:8501`).

*   **Running with Docker:**
    1.  Ensure Docker Desktop or Docker Engine is running.
    2.  From the project root, build and run the application using Docker Compose:
        ```bash
        docker-compose up --build
        ```
    3.  The application will typically be accessible at `http://localhost:8501` (or the port defined in your `docker-compose.yml`). Note that scheduled summaries within Docker rely on the script being triggered correctly by the OS scheduler *inside* the container or an equivalent mechanism if configured.

## Contributing

Please see our `CONTRIBUTING.md` file for details on how to contribute to the project.
