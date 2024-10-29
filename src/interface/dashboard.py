import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any
from datetime import datetime

class DashboardComponents:
    """Dashboard components for LLM monitoring."""
    
    @staticmethod
    def render_overview_tab(df: pd.DataFrame):
        """Render overview metrics."""
        st.subheader("Quick Stats")
        
        # Provider-wise summary
        provider_metrics = df.groupby('provider').agg({
            'total_tokens': 'sum',
            'total_cost': 'sum',
            'response_time': 'mean'
        }).round(4)
        
        # Display metrics in columns
        cols = st.columns(len(provider_metrics))
        for idx, (provider, metrics) in enumerate(provider_metrics.iterrows()):
            with cols[idx]:
                st.metric(
                    f"{provider}",
                    f"${metrics['total_cost']:.4f}",
                    f"{metrics['total_tokens']} tokens"
                )
        
        # Cost trend chart
        fig = go.Figure()
        for provider in df['provider'].unique():
            provider_df = df[df['provider'] == provider]
            fig.add_trace(go.Scatter(
                x=provider_df['timestamp'],
                y=provider_df['total_cost'],
                name=f"{provider} Cost",
                mode='lines+markers'
            ))
        
        fig.update_layout(
            title="Cost Trends by Provider",
            xaxis_title="Time",
            yaxis_title="Cost ($)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def render_cost_analysis_tab(df: pd.DataFrame):
        """Render cost analysis."""
        st.subheader("Cost Analysis")
        
        # Cost comparison
        fig_cost = px.bar(
            df,
            x='model',
            y='total_cost',
            color='provider',
            title="Cost per Model",
            labels={'total_cost': 'Total Cost ($)'}
        )
        st.plotly_chart(fig_cost, use_container_width=True)
        
        # Cost per token
        df['cost_per_token'] = df['total_cost'] / df['total_tokens']
        fig_token = px.bar(
            df,
            x='model',
            y='cost_per_token',
            color='provider',
            title="Cost per Token",
            labels={'cost_per_token': 'Cost per Token ($)'}
        )
        st.plotly_chart(fig_token, use_container_width=True)

    @staticmethod
    def render_performance_tab(df: pd.DataFrame):
        """Render performance metrics."""
        st.subheader("Performance Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Response time comparison
            fig_resp = px.box(
                df,
                x='model',
                y='response_time',
                color='provider',
                title="Response Time Distribution"
            )
            st.plotly_chart(fig_resp, use_container_width=True)
        
        with col2:
            # Processing speed comparison
            fig_speed = px.box(
                df,
                x='model',
                y='tokens_per_second',
                color='provider',
                title="Processing Speed"
            )
            st.plotly_chart(fig_speed, use_container_width=True)

    @staticmethod
    def render_history_tab(df: pd.DataFrame):
        """Render call history."""
        st.subheader("Recent LLM Calls")
        
        # Format DataFrame for display
        display_df = df.copy()
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Select columns to display
        columns = [
            'timestamp', 'provider', 'model', 'prompt',
            'total_tokens', 'response_time', 'total_cost'
        ]
        
        st.dataframe(
            display_df[columns],
            use_container_width=True,
            hide_index=True
        )