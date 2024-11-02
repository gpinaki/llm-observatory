import asyncio
import logging
import streamlit as st
from typing import Dict, Any
import pandas as pd
from datetime import datetime

from src.config.settings import settings
from src.llm.openai_llm import OpenAILLM
from src.llm.anthropic_llm import AnthropicLLM
from src.llm.gemini_llm import GeminiLLM  # Add this import

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
        """Configure Streamlit page with mobile-first design."""
        st.set_page_config(
            page_title="LLM Observatory",
            page_icon="🔭",
            layout="wide",
            initial_sidebar_state="collapsed"  # Changed to collapsed for mobile
        )
        st.markdown(
            """
            <style>
            /* Base Layout and Typography - Mobile First Approach */
            .main-title {
                font-family: 'Helvetica Neue', Arial, sans-serif;
                font-size: 1.8em;  /* Smaller base size for mobile */
                font-weight: 600;
                text-align: center;
                margin: 10px 5px;
                padding: 0 10px;
            }
            
            .subtitle-container {
                text-align: center;
                margin: 5px 0 15px 0;
                padding: 0 10px;
            }
            
            .main-subtitle {
                font-size: 1em;
                color: #4A5568;
                margin-bottom: 8px;
                line-height: 1.4;
            }
            
            /* Mobile-Optimized Feature Pills */
            .feature-pills {
                display: flex;
                justify-content: center;
                gap: 6px;
                flex-wrap: wrap;
                margin: 8px 5px;
                padding: 0 5px;
            }
            
            .feature-pill {
                background: linear-gradient(135deg, #E2E8F0, #EDF2F7);
                padding: 4px 8px;
                border-radius: 15px;
                font-size: 0.75em;
                color: #2D3748;
                border: 1px solid #E2E8F0;
                white-space: nowrap;
                margin: 2px;
            }

            /* Mobile-Optimized Metrics Cards */
            .metric-card {
                background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
                border-radius: 8px;
                padding: 12px;
                margin: 8px 0;
                width: 100%;
            }

            /* Mobile-Optimized Sidebar */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
                min-width: 250px !important;
                max-width: 100% !important;
            }

            [data-testid="stSidebar"] .stButton > button {
                width: 100%;
                border-radius: 8px;
                margin: 4px 0;
                padding: 8px 12px;
                font-size: 0.9em;
                min-height: 45px;  /* Larger touch target */
            }

            /* Improved Touch Targets */
            button, select, input, .stSelectbox {
                min-height: 45px;
                touch-action: manipulation;
            }

            /* Better Spacing for Mobile Inputs */
            .stTextInput input {
                padding: 8px 12px;
                margin: 4px 0;
            }

            /* Mobile-Optimized Tabs */
            .stTabs [data-baseweb="tab"] {
                padding: 10px;
                min-height: 45px;
                font-size: 0.9em;
            }

            /* Dark Mode Adjustments */
            @media (prefers-color-scheme: dark) {
                .main-subtitle { color: #E2E8F0; }
                .feature-pill {
                    background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
                    border-color: rgba(255,255,255,0.1);
                    color: #E2E8F0;
                }
                [data-testid="stSidebar"] {
                    background: linear-gradient(180deg, rgba(49,51,63,0.2) 0%, rgba(49,51,63,0.4) 100%);
                }
            }

            /* Responsive Design - Tablet and Desktop Enhancements */
            @media screen and (min-width: 768px) {
                .main-title {
                    font-size: 2.5em;
                    margin: 20px 0;
                }
                
                .main-subtitle {
                    font-size: 1.2em;
                }
                
                .feature-pill {
                    padding: 5px 12px;
                    font-size: 0.9em;
                }
                
                .feature-pills {
                    gap: 12px;
                    margin: 15px 0;
                }
                
                .metric-card {
                    padding: 16px;
                    border-radius: 12px;
                }

                [data-testid="stSidebar"] .stButton > button {
                    padding: 10px 15px;
                }
            }

            /* Hide Streamlit Branding for Cleaner Mobile View */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            
            /* Improved Scrolling */
            [data-testid="stVerticalBlock"] {
                gap: 0.5rem;
            }

            /* Better Touch Scrolling */
            .main .block-container {
                padding-top: 1rem;
                padding-bottom: 1rem;
                overflow-y: auto;
                -webkit-overflow-scrolling: touch;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Mobile-Optimized Title and Feature Pills
        st.markdown('<div class="main-title">🔭 LLM Observatory</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="subtitle-container">
                <div class="main-subtitle">
                    LLM Monitoring & Analysis Platform
                </div>
                <div class="feature-pills">
                    <span class="feature-pill">🤖 Multi-Model</span>
                    <span class="feature-pill">📊 Analytics</span>
                    <span class="feature-pill">💰 Cost</span>
                    <span class="feature-pill">⚡ Performance</span>
                    <span class="feature-pill">📈 Metrics</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
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
            st.markdown(
                '<h2 style="font-size: 1.3em;">Configuration</h2>', 
                unsafe_allow_html=True
            )
            
            # Application Settings
            st.subheader("Application Configuration")
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
            
            if not application_name:
                st.warning("⚠️ Please enter an application name")
            
            st.divider()
            
            # LLM Configuration
            st.subheader("LLM Configuration")
            provider = st.radio(
                "LLM Provider",
                options=["OpenAI", "Anthropic", "Gemini"],
                index=["OpenAI", "Anthropic", "Gemini"].index(st.session_state.get("provider", "OpenAI")),
                help="Choose the LLM provider to access different LLM models"
            )
            model = st.selectbox(
                "Select Model", 
                options=(
                    settings.LLM.OPENAI_MODELS if provider == "OpenAI"
                    else settings.LLM.ANTHROPIC_MODELS if provider == "Anthropic"
                    else settings.LLM.GEMINI_MODELS
                )
            )
            
            with st.expander("Advanced Settings"):
                temperature = st.slider(
                    "Temperature",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.7,
                    step=0.1,
                    help="Controls randomness in the response"
                )
                max_tokens = st.slider(
                    "Max Tokens",
                    min_value=50,
                    max_value=2000,
                    value=500,
                    step=50,
                    help="Maximum length of the response"
                )
            
            # Current Configuration Display
            # if application_name:
            #     st.divider()
            #     st.subheader("Current Settings")
            #     st.dataframe(
            #         pd.DataFrame({
            #             'Parameters': ['Application', 'Environment', 'Provider', 'Model'],
            #             'Value': [application_name, environment, provider, model]
            #         }),
            #         hide_index=True
            #     )
            
            try:
                self.download_summary()
            except Exception as e:
                st.error(f"Error preparing download summary of the session data.: {str(e)}")
        
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
        if provider not in ["OpenAI", "Anthropic", "Gemini"]:
            raise ValueError(f"Unknown provider: {provider}")
        try:
            if not application_name:
                raise ValueError("Application name cannot be empty.")

            if provider == "Anthropic" and model not in settings.LLM.ANTHROPIC_MODELS:
                raise ValueError(f"Model '{model}' is not available in Anthropic's model list.")
            
            if provider == "Gemini" and model not in settings.LLM.GEMINI_MODELS:
                raise ValueError(f"Model '{model}' is not available in Gemini's model list.")
            
            if provider == "OpenAI":
                async with OpenAILLM(
                    api_key=settings.OPENAI_API_KEY,
                    model=model,
                    application_id=application_name,
                    environment=environment
                ) as llm:
                    return await llm.generate_response(prompt=prompt, temperature=temperature, max_tokens=max_tokens)
                    
            elif provider == "Anthropic":
                llm = AnthropicLLM(
                    api_key=settings.ANTHROPIC_API_KEY,
                    model=model,
                    application_id=application_name,
                    environment=environment
                )
                return await llm.generate_response(prompt=prompt, temperature=temperature, max_tokens=max_tokens)
                
            elif provider == "Gemini":  # Add Gemini handler
                llm = GeminiLLM(
                    model=model,
                    application_id=application_name,
                    environment=environment
                )
                
                return await llm.generate_response(
                    prompt=prompt, 
                    temperature=temperature, 
                    max_tokens=max_tokens
                )
                
            else:
                raise ValueError(f"Unknown provider: {provider}")
                
        except ValueError as e:
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
        """Store LLM call in history with complete JSON data."""
        history_entry = {
            "timestamp": datetime.now(),
            "provider": response["metadata"]["model"].split("-")[0],
            "model": response["metadata"]["model"],
            "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "total_tokens": response["metadata"]["tokens"]["total_tokens"],
            "response_time": response["metadata"]["performance"]["response_time"],
            "total_cost": response["metadata"]["costs"]["total_cost"],
            "tokens_per_second": response["metadata"]["performance"]["tokens_per_second"],
            # Add full request/response JSON
            "full_prompt": prompt,
            "full_response": response["response"],
            "request_json": str({
                "provider": response["metadata"]["model"].split("-")[0],
                "model": response["metadata"]["model"],
                "prompt": prompt,
                "timestamp": datetime.now().isoformat()
            }),
            "response_json": str(response)
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
        """Provide consolidated download of session history and summary with JSON data."""
        try:
            # Create history DataFrame
            if st.session_state.llm_history:
                # Convert history to DataFrame
                history_df = pd.DataFrame(st.session_state.llm_history)
                
                # Format timestamp
                history_df['timestamp'] = pd.to_datetime(history_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                
                # Create summary row as a separate DataFrame
                # Note: Summary row won't have JSON data as it's a summary
                summary_df = pd.DataFrame([{
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'provider': 'SUMMARY',
                    'model': 'All Models',
                    'prompt': 'Session Summary',
                    'total_tokens': st.session_state.total_tokens,
                    'response_time': sum(st.session_state.response_times) / len(st.session_state.response_times) if st.session_state.response_times else 0,
                    'total_cost': st.session_state.total_cost,
                    'tokens_per_second': history_df['tokens_per_second'].mean(),
                    'full_prompt': '',  # Empty for summary row
                    'full_response': '',  # Empty for summary row
                    'request_json': '',  # Empty for summary row
                    'response_json': ''  # Empty for summary row
                }])
                
                # Concatenate history and summary
                final_df = pd.concat([history_df, summary_df], ignore_index=True)
                
                # Reorder columns to put JSON data at the end
                column_order = [
                    'timestamp',
                    'provider',
                    'model',
                    'prompt',
                    'total_tokens',
                    'response_time',
                    'total_cost',
                    'tokens_per_second',
                    'full_prompt',
                    'full_response',
                    'request_json',
                    'response_json'
                ]
                
                final_df = final_df[column_order]
                
                # Create download button with a more descriptive name
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"llm_session_data_{timestamp}.csv"
                
                st.sidebar.download_button(
                    "📥 Download Complete Session Data",
                    final_df.to_csv(index=False),
                    file_name=filename,
                    mime="text/csv",
                    help="Download complete session history including request/response data and summary"
                )
            
        except Exception as e:
            st.error(f"Error preparing download summary of the session data: {str(e)}")
            logging.error(f"Download summary error: {str(e)}", exc_info=True)

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
