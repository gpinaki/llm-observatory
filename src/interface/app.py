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
                margin-bottom: 10px;
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
                color: #2C3E50;
            }
            # Sidebar style 
            
            /* Sidebar background and text styling */
            [data-testid="stSidebar"] {
                background-color: #E0F7FA;  /* Light blue background */
                color: #1E1E1E; /* Dark font color for contrast */
            }

            /* Sidebar headers and paragraphs text color */
            [data-testid="stSidebar"] h1, 
            [data-testid="stSidebar"] h2, 
            [data-testid="stSidebar"] h3, 
            [data-testid="stSidebar"] p {
                color: #1E1E1E;
            }

            /* Advanced Settings button styling */
            [data-testid="stSidebar"] .streamlit-expanderHeader {
                background-color: #FFFFFF !important; /* Light background for visibility */
                color: #333333 !important; /* Dark text color */
            }

            /* Show/Hide Performance Analytics button */
            [data-testid="stSidebar"] .stButton > button {
                background-color: #007BFF;  /* Bright blue for contrast */
                color: #FFFFFF !important;  /* White text */
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: 500;
            }

            /* Button hover effect */
            [data-testid="stSidebar"] .stButton > button:hover {
                background-color: #0056b3;
                color: #FFFFFF;
            }
            
            # sidebar style ends 
            
            
            
            /* Keep existing main content styles */
            .stMetric {
                background-color: #FFFFFF;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                padding: 10px;
                color: #2C3E50;
            }
            
            .stChatMessage {
                background-color: #FFFFFF;
                border-radius: 8px;
                padding: 10px;
                margin: 5px 0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                color: #2C3E50;
            }
            /* Chat Interface Text Styling */
            .stChatMessage p {
                color: #2C3E50 !important;
                font-size: 1rem;
            }

            /* Chat Message Background */
            .stChatMessage {
                background-color: #FFFFFF !important;
                border-radius: 8px;
                padding: 10px;
                margin: 5px 0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }

            /* Dashboard and Metrics Text */
            .element-container div {
                color: #2C3E50 !important;
            }

           /* Complete Advanced Settings Panel Fix */
            /* Main expander header */
            [data-testid="stSidebar"] .streamlit-expanderHeader {
                color: #ECF0F1 !important;
                background-color: #2C3E50 !important;
            }

            /* Expander content background */
            [data-testid="stSidebar"] .streamlit-expanderContent {
                background-color: #34495E !important;
                color: #ECF0F1 !important;
                padding: 15px !important;
                border-radius: 8px !important;
            }

            /* All text within Advanced Settings */
            [data-testid="stSidebar"] .streamlit-expanderContent p,
            [data-testid="stSidebar"] .streamlit-expanderContent span,
            [data-testid="stSidebar"] .streamlit-expanderContent label {
                color: #ECF0F1 !important;
            }

            /* Slider specific styles */
            [data-testid="stSidebar"] .stSlider label,
            [data-testid="stSidebar"] .stSlider label > div {
                color: #ECF0F1 !important;
            }

            /* Slider value and range text */
            [data-testid="stSidebar"] [data-testid="stTickBarMin"],
            [data-testid="stSidebar"] [data-testid="stTickBarMax"],
            [data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"] {
                color: #ECF0F1 !important;
            }

            /* Help text for sliders */
            [data-testid="stSidebar"] .stSlider > div > div > div[data-baseweb="tooltip"] {
                color: #ECF0F1 !important;
            }

            /* Temperature and token labels */
            [data-testid="stSidebar"] .stSlider > div:first-child {
                color: #ECF0F1 !important;
            }

            /* Make sure slider numbers are visible */
            [data-testid="stSidebar"] .stSlider [role="slider"] {
                color: #ECF0F1 !important;
                background-color: #3498DB !important;
            }
            
            /* Advanced Settings Header Specific - Title and Hover Effect */
            [data-testid="stSidebar"] button[kind="secondary"] {
                color: #ECF0F1 !important;
                transition: color 0.3s ease;
            }

            [data-testid="stSidebar"] button[kind="secondary"]:hover {
                color: #E74C3C !important;  /* Red color on hover */
            }

            /* Slider Min/Max Values and Labels */
            [data-testid="stSidebar"] .stSlider [data-testid="stTickBarMin"],
            [data-testid="stSidebar"] .stSlider [data-testid="stTickBarMax"],
            [data-testid="stSidebar"] .stSlider div[role="slider"],
            [data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"] {
                color: #ECF0F1 !important;
                font-weight: 400;
            }

            /* Make sure the numbers in the slider are clearly visible */
            [data-testid="stSidebar"] .stSlider div[data-baseweb="slider"] div {
                color: #ECF0F1 !important;
            }

            /* Performance Dashboard Toggle Text */
            [data-testid="stSidebar"] .stButton div {
                color: #ECF0F1 !important;
            }

            /* Fix for all expandable sections in sidebar */
            [data-testid="stSidebar"] button[kind="secondary"] {
                color: #ECF0F1 !important;
            }

            /* Dashboard Metrics and Text */
            .stMarkdown div p {
                color: #2C3E50 !important;
            }

            /* Dashboard Tab Labels */
            .stTabs button[role="tab"] {
                color: #2C3E50 !important;
            }

            /* Metrics Values */
            .stMetric [data-testid="stMetricValue"] {
                color: #2C3E50 !important;
            }

            /* Metric Labels */
            .stMetric [data-testid="stMetricLabel"] {
                color: #2C3E50 !important;
            }

            /* JSON and Code blocks */
            pre {
                color: #2C3E50 !important;
                background-color: #F8F9FA !important;
            }

            /* DataFrame Text */
            .dataframe {
                color: #2C3E50 !important;
            }

            /* All text in main content area */
            .main .block-container {
                color: #2C3E50 !important;
            }
            
            </style>
            """,
            unsafe_allow_html=True
        )
        # Keep these lines exactly as they are
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
        defaults = {
            "messages": [],
            "total_tokens": 0,
            "total_cost": 0.0,
            "response_times": [],
            "application_name": "app-llm-insights",
            "environment": "Development",
            "llm_history": [],
            "show_dashboard": False
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

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
            

            # Add the download summary button here
            # Session Summary Metrics added on 11/1
            try:
                self.download_summary()
            except Exception as e:
                st.error(f"An error occurred while preparing the download summary: {str(e)}")
                
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
        try:
            if not application_name:
                raise ValueError("Application name cannot be empty.")

            if provider == "Anthropic" and model not in settings.LLM.ANTHROPIC_MODELS:
                raise ValueError(f"Model '{model}' is not available in Anthropic's model list.")
            
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
        except  ValueError as e:
            st.error(f"Model Error: {str(e)}")
        except Exception as e:
            st.error("An unexpected error occurred. Please check your configurations.")
            raise e

    def display_metrics(self, metadata: Dict[str, Any]):
        """Display basic metrics in the Streamlit app."""
        st.markdown("### Performance Overview", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tokens", metadata["tokens"]["total_tokens"], help="The total number of tokens used in the session.")
        with col2:
            st.metric("Total Cost", f"${metadata['costs']['total_cost']:.4f}", help="The cumulative cost based on usage.")
        with col3:
            st.metric("Response Time", f"{metadata['performance']['response_time']:.2f}s", help="Average response time per request.")


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
            
    def download_summary(self):
        """Provide a download button for session summary as CSV."""
        summary = {
            "Application Name": st.session_state.application_name,
            "Environment": st.session_state.environment,
            "Total Tokens": st.session_state.total_tokens,
            "Total Cost": f"${st.session_state.total_cost:.4f}",
            "Average Response Time": (sum(st.session_state.response_times) / len(st.session_state.response_times)) if st.session_state.response_times else 0
        }
        summary_df = pd.DataFrame([summary])
        st.sidebar.download_button("Download Summary", summary_df.to_csv(index=False), file_name="LLM_summary.csv", mime="text/csv")

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
