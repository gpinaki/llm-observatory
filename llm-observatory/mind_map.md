# Project Mind Map

## 1. Main Application (`app.py`)
   - **Purpose**: The entry point for running the LLM-based application.
   - **Key Functions**:
     - `run`: Runs the application asynchronously.
     - `render_sidebar`: Renders the sidebar settings for configuring model providers (OpenAI, Anthropic, etc.).
     - `get_llm_response`: Calls the appropriate LLM provider and retrieves responses.
     - **Session Management**:
       - Initializes session states like total tokens, costs, and response times.
       - Tracks history of LLM calls and stores session information.
   - **Related Files**:
     - **`settings-1.py`**: Loads configuration parameters (API keys, model lists).
     - **`dashboard.py`**: Displays analytics based on model interactions and costs.

## 2. Settings (`settings.py`)
   - **Purpose**: Central configuration and settings management for the project.
   - **Key Classes and Variables**:
     - `LLM`: Stores configurations for different LLM providers, including model lists and default parameters (temperature, max tokens, etc.).
     - API Keys: Includes API keys for `OpenAI`, `Anthropic`, and potentially other providers.
   - **Related Modules**:
     - Used throughout the project for accessing LLM configurations and setting defaults.
     - Accessed by each LLM handler for model and parameter configurations.

## 3. LLM Providers (Modular Implementations)
   ### 3.1 OpenAI LLM (`openai_llm.py`)
      - **Purpose**: Manages interactions with OpenAI's API.
      - **Key Functions**:
        - `generate_response`: Sends a prompt to the OpenAI API and retrieves a response.
      - **Cost Tracking and Error Handling**:
        - Logs API usage statistics like tokens and costs for each response.
        - Handles API exceptions with retries and timeout strategies.

   ### 3.2 Anthropic LLM (`anthropic_llm.py`)
      - **Purpose**: Manages interactions with Anthropic's LLM (Claude models).
      - **Key Functions**:
        - `generate_response`: Asynchronously sends a prompt to Anthropic's API.
      - **Setup and Cleanup**:
        - Initializes and validates the model before API calls.
        - Cleans up resources (e.g., closing connections) after each session.
      - **Performance Tracking**:
        - Logs metrics like response time and tokens used.
        - Tracks costs using settings from `settings-1.py`.
      - **Exception Handling**:
        - Custom error handling using `LLMException` for API errors and retries.

   ### 3.3 Base LLM (`base.py`)
      - **Purpose**: Abstract base class defining the LLM interface for all providers.
      - **Abstract Methods**:
        - `setup`: Initializes provider-specific configurations.
        - `generate_response`: Abstract function for generating responses, implemented by subclasses (e.g., OpenAI, Anthropic).
        - `get_model_info`: Retrieves information on model configurations and capabilities.
      - **Session Management**:
        - Tracks metrics across sessions, such as tokens used and costs incurred.
        - Logs interactions and validates responses.
      - **Related Classes**:
        - Used as a base for `AnthropicLLM` and `OpenAILLM` classes.

## 4. Dashboard and Analytics (`dashboard.py`)
   - **Purpose**: Provides a UI dashboard in Streamlit to visualize metrics and analytics.
   - **Key Components**:
      - `render_overview_tab`: Displays quick metrics for tokens, cost, and provider usage.
      - `render_cost_analysis_tab`: Shows cost comparison between models.
      - `render_performance_tab`: Visualizes response time and processing speed per model.
      - `render_history_tab`: Lists recent LLM calls with detailed statistics.
   - **Dependencies**:
      - Relies on Streamlit for UI and Plotly for data visualization.
      - Takes data from `app-2.py` to display usage and performance statistics.
