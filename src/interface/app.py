import asyncio
import streamlit as st
from typing import Dict, Any
import pandas as pd
from datetime import datetime

from src.config.settings import settings
from src.llm.openai_llm import OpenAILLM
from src.llm.anthropic_llm import AnthropicLLM

# Add new imports for dashboard components
import plotly.express as px
import plotly.graph_objects as go
from src.interface.dashboard import DashboardComponents

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
            page_title="LLM Observatory",
            page_icon="🔭",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        st.markdown(
            """
            <style>
            /* Main title styling */
            .main-title {
                font-family: 'Helvetica Neue', Arial, sans-serif;
                font-size: 2.8em;
                font-weight: 600;
                color: #2C3E50;
                background: linear-gradient(to right, #E8F4F8, #F8F9FA);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 10px;  /* Reduced from 30px to bring subtitle closer */
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            
            /* Subtitle styling */
            .subtitle {
                font-family: 'Helvetica Neue', Arial, sans-serif;
                font-size: 1.2em;
                font-weight: 400;
                color: #5D6D7E;
                text-align: center;
                margin-bottom: 30px;
                padding: 0 20px;
                line-height: 1.5;
                letter-spacing: 0.3px;
            }
            
            /* Highlight key terms in subtitle */
            .highlight {
                color: #3498DB;
                font-weight: 500;
            }
            
            /* General page styling */
            .stApp {
                background-color: #FAFBFC;
            }
            
            /* Subheader styling */
            .subheader {
                color: #34495E;
                font-family: 'Helvetica Neue', Arial, sans-serif;
                padding: 5px 0;
            }
            
            /* Metric cards styling */
            .stMetric {
                background-color: #FFFFFF;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                padding: 10px;
            }
            
            /* Sidebar styling */
            .css-1d391kg {
                background-color: #F8F9FA;
            }
            
            /* Button styling */
            .stButton>button {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                transition: all 0.3s ease;
            }
            
            .stButton>button:hover {
                background-color: #2980B9;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            /* Chat interface styling */
            .stChatMessage {
                background-color: #FFFFFF;
                border-radius: 8px;
                padding: 10px;
                margin: 5px 0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        # Title and subtitle
        st.markdown('<div class="main-title">🔭 LLM Observatory</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="subtitle">Unlock Model Insights: '
            '<span class="highlight">Track Performance</span>, '
            '<span class="highlight">Control Costs</span>, '
            '<span class="highlight">Drive Results</span></div>', 
            unsafe_allow_html=True
        )
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
        # Add these new initializations for dashboard components
        if "llm_history" not in st.session_state:
            st.session_state.llm_history = []
        if "show_dashboard" not in st.session_state:
            st.session_state.show_dashboard = False

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
    
    def store_llm_call(self, prompt: str, response: Dict[str, Any]):
        """Store LLM call in history."""
        history_entry = {
            "timestamp": datetime.now(),
            "provider": response["metadata"]["model"].split("-")[0],
            "model": response["metadata"]["model"],
            "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "total_tokens": response["metadata"]["tokens"]["total_tokens"],
            "response_time": response["metadata"]["performance"]["response_time"],
            "total_cost": response["metadata"]["costs"]["total_cost"],
            "tokens_per_second": response["metadata"]["performance"]["tokens_per_second"]
        }
        
        st.session_state.llm_history.append(history_entry)
        if len(st.session_state.llm_history) > 10:
            st.session_state.llm_history.pop(0)

    def render_dashboard(self):
        """Render the performance dashboard."""
        if not st.session_state.llm_history:
            st.info("No LLM calls recorded yet. Start chatting to see analytics!")
            return
        
        # Convert history to DataFrame
        df = pd.DataFrame(st.session_state.llm_history)
    
        # Create dashboard tabs
        overview_tab, cost_tab, perf_tab, history_tab = st.tabs([
            "Overview",
            "Cost Analysis",
            "Performance Metrics",
            "Call History"
        ])
    
        with overview_tab:
            DashboardComponents.render_overview_tab(df)
    
        with cost_tab:
            DashboardComponents.render_cost_analysis_tab(df)
    
        with perf_tab:
            DashboardComponents.render_performance_tab(df)
    
        with history_tab:
            DashboardComponents.render_history_tab(df)

    async def run_async(self):
        """Run the Streamlit application asynchronously."""
        provider, model, temperature, max_tokens, application_name, environment = self.render_sidebar()
    
        with st.sidebar:
            st.sidebar.divider()
            if st.button(
                "📊 Toggle Performance Dashboard",
                help="Show/Hide performance analytics"
            ):
                st.session_state.show_dashboard = not st.session_state.show_dashboard

        # Add this section after the toggle button
        if st.session_state.show_dashboard:
            st.header("📊 Performance Analytics")
            self.render_dashboard()
            st.divider()

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
                self.store_llm_call(prompt, response)
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
