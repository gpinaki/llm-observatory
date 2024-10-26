import asyncio
import streamlit as st
from typing import Dict, Any
import pandas as pd
from datetime import datetime

from src.config.settings import settings
from src.llm.openai_llm import OpenAILLM
from src.llm.anthropic_llm import AnthropicLLM

class LLMInsightsHub:
    """Streamlit interface for LLM Insights Hub."""
    
    ENVIRONMENTS = ["Development", "Test", "Integration", "Production"]
    ENV_MAP = {
        "Development": "dev",
        "Test": "test",
        "Integration": "int",
        "Production": "prod"
    }

    def __init__(self):
        """Initialize the application."""
        self.setup_page_config()
        self.initialize_session_state()

    def setup_page_config(self):
        """Configure Streamlit page."""
        st.set_page_config(
            page_title="LLM Insights Hub",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        st.title("🔍 LLM Insights Hub")
        st.sidebar.header("Control Panel")

    def initialize_session_state(self):
        """Initialize session state variables."""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "total_tokens" not in st.session_state:
            st.session_state.total_tokens = 0
        if "total_cost" not in st.session_state:
            st.session_state.total_cost = 0.0
        if "response_times" not in st.session_state:
            st.session_state.response_times = []
        if "application_name" not in st.session_state:
            st.session_state.application_name = "app-llm-insights"
        if "environment" not in st.session_state:
            st.session_state.environment = "Development"

    def render_sidebar(self) -> tuple:
        """Render sidebar configuration options."""
        with st.sidebar:
            st.subheader("Application Settings")
            application_name = st.text_input(
                "Application Name",
                value=st.session_state.application_name,
                placeholder="Enter your application name",
                help="Unique identifier for your application"
            )
            environment = st.selectbox(
                "Environment",
                options=self.ENVIRONMENTS,
                index=self.ENVIRONMENTS.index(st.session_state.environment),
                help="Select the deployment environment"
            )
            st.session_state.application_name = application_name
            st.session_state.environment = environment
            if not application_name:
                st.sidebar.warning("⚠️ Please enter an application name")
            st.sidebar.divider()
            st.subheader("LLM Configuration")
            provider = st.selectbox("Select LLM Provider", options=["OpenAI", "Anthropic"])
            model = st.selectbox("Select Model", options=settings.LLM.OPENAI_MODELS if provider == "OpenAI" else settings.LLM.ANTHROPIC_MODELS)
            with st.expander("Advanced Settings"):
                temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1, help="Controls randomness in the response")
                max_tokens = st.slider("Max Tokens", min_value=50, max_value=2000, value=500, step=50, help="Maximum length of the response")
            if application_name:
                st.sidebar.divider()
                st.sidebar.subheader("Current Configuration")
                config_df = pd.DataFrame({
                    'Setting': ['Application', 'Environment', 'Provider', 'Model'],
                    'Value': [application_name, environment, provider, model]
                })
                st.sidebar.dataframe(config_df, hide_index=True)
            return provider, model, temperature, max_tokens, application_name, self.ENV_MAP[environment]

    async def get_llm_response(self, 
                         provider: str,
                         model: str,
                         prompt: str,
                         temperature: float,
                         max_tokens: int,
                         application_name: str,
                         environment: str) -> Dict[str, Any]:
        """Get response from selected LLM."""
        if not application_name:
            raise ValueError("Application name is required")
        if provider == "OpenAI":
            async with OpenAILLM(
                api_key=settings.OPENAI_API_KEY,
                model=model,
                application_id=application_name,
                environment=environment
            ) as llm:
                return await llm.generate_response(prompt=prompt, temperature=temperature, max_tokens=max_tokens)
        else:
            # AnthropicLLM does not support async context manager, so we instantiate it without `async with`
            llm = AnthropicLLM(
                api_key=settings.ANTHROPIC_API_KEY,
                model=model,
                application_id=application_name,
                environment=environment
            )
            return await llm.generate_response(prompt=prompt, temperature=temperature, max_tokens=max_tokens)


    def display_metrics(self, metadata: Dict[str, Any]):
        """Display basic metrics in the Streamlit app."""
        st.markdown("### Performance Overview", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tokens", metadata["tokens"]["total_tokens"])
        with col2:
            st.metric("Total Cost", f"${metadata['costs']['total_cost']:.4f}")
        with col3:
            st.metric("Response Time", f"{metadata['performance']['response_time']:.2f}s")

    def display_detailed_metrics(self, metadata: Dict[str, Any]):
        """Display detailed metrics in the Streamlit app."""
        with st.expander("Detailed Metrics"):
            st.json(metadata)

    async def run_async(self):
        """Run the Streamlit application asynchronously."""
        provider, model, temperature, max_tokens, application_name, environment = self.render_sidebar()
        if not application_name:
            st.info("👈 Please enter an application name in the sidebar to begin")
            return
        st.subheader("Chat Console")
        st.caption(f"Application: {application_name} | Environment: {environment} | Model: {model}")
        if prompt := st.chat_input("Enter your message...", disabled=not application_name):
            st.session_state.messages.append({
                "role": "user",
                "content": prompt,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = await self.get_llm_response(
                        provider=provider,
                        model=model,
                        prompt=prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        application_name=application_name,
                        environment=environment
                    )
                    st.markdown(response["response"])
                    self.display_metrics(response["metadata"])
                    self.display_detailed_metrics(response["metadata"])
                    st.session_state.total_tokens += response["metadata"]["tokens"]["total_tokens"]
                    st.session_state.total_cost += response["metadata"]["costs"]["total_cost"]
                    st.session_state.response_times.append(response["metadata"]["performance"]["response_time"])
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["response"],
                        "metadata": response["metadata"],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
        if st.session_state.messages:
            st.sidebar.divider()
            st.sidebar.subheader("Session Summary")
            st.sidebar.metric("Total Tokens Used", value=st.session_state.total_tokens)
            st.sidebar.metric("Total Cost", value=f"${st.session_state.total_cost:.4f}")
            if st.session_state.response_times:
                st.sidebar.metric("Average Response Time", value=f"{sum(st.session_state.response_times) / len(st.session_state.response_times):.2f}s")

    def run(self):
        """Entrypoint for the Streamlit application."""
        asyncio.run(self.run_async())

if __name__ == "__main__":
    app = LLMInsightsHub()
    app.run()
