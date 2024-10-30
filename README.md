# 🔭 LLM Observatory: Enterprise LLM Monitoring & Cost Analysis Platform

A comprehensive observability platform designed for enterprise environments, providing real-time monitoring, cost analysis, and performance tracking across multiple LLM providers (OpenAI and Anthropic).

[Insert main dashboard screenshot here - showing all tabs]

## ⚡️ Quick Start
```bash
# Clone repository
git clone https://github.com/gpinaki/llm-observatory.git
cd llm-observatory

# Set up virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables

# Add your API keys to .env

# Run application
streamlit run src/interface/app.py
```

## 🎯 Core Features

### 1. Multi-Provider Cost Analysis
- Real-time cost tracking across providers
- Token-level cost breakdown
- Historical cost trends
- Cost comparison visualizations

[Insert cost analysis dashboard screenshot]

### 2. Performance Monitoring
- Response time tracking
- Token processing rates
- Error rate monitoring
- Provider performance comparison

[Insert performance metrics screenshot]

### 3. Robust Control Panel
- Support for Dev/Test/Int/Prod environments
- Enable passing application name for auditing
- Provision to choose LLM and models
- Provision to modify temperature and max token limits

[Insert control panel]

### 4. Interactive Dashboard
- Toggle-able analytics dashboard
- Historical data visualization (last 10 calls)
- Provider comparison metrics
- Detailed call history

[Insert dashboard tabs screenshot]

## 💡 Usage Guide

### Cost Monitoring
```python
# Example integration in your code
from llm_observatory import OpenAILLM

async with OpenAILLM(
    api_key="your-key",
    model="gpt-4",
    application_id="your-app",
    environment="production"
) as llm:
    response = await llm.generate_response(
        prompt="Hello!",
        temperature=0.7
    )
    print(f"Cost: ${response['metadata']['costs']['total_cost']}")
```

### Performance Tracking
```python
# Track performance metrics
metrics = response["metadata"]["performance"]
print(f"Response Time: {metrics['response_time']}s")
print(f"Processing Speed: {metrics['tokens_per_second']} tokens/sec")
```

### Environment Management
```python
# Example environment-specific configuration
llm = OpenAILLM(
    api_key=settings.OPENAI_API_KEY,
    model="gpt-4",
    application_id="enterprise-app",
    environment="production"  # dev/test/int/prod
)
```

## 🚀 Implementation Roadmap

### Current Implementation
- ✅ Multi-provider support (OpenAI, Anthropic)
- ✅ Cost tracking and analysis
- ✅ Performance monitoring
- ✅ Environment management
- ✅ Interactive dashboard
- ✅ Historical data tracking (last 10 calls)

### Future Enhancements
- 🔄 Database integration for extended history
- 🔄 Custom alert configurations
- 🔄 Cost prediction modeling


## 📊 Benefits

- **Cost Optimization**: Track and optimize LLM usage costs across providers
- **Performance Monitoring**: Real-time performance metrics and alerts
- **Multi-Environment**: Development to Production coverage
- **Provider Agnostic**: Support for multiple LLM providers
- **Scalable Architecture**: Built for enterprise requirements

## 📝 License

This project is licensed under the MIT License - see [LICENSE.md](LICENSE.md) for details.

## 👤 Author

Pinaki Guha  
- LinkedIn: [https://www.linkedin.com/in/pinakiguha/]
- Email: [pinaki.guha@gmail.com]
- Portfolio: [https://github.com/gpinaki]

## 🙏 Acknowledgments

This project was developed by Pinaki Guha, with supplementary support from AI-based code assistance tools like ChatGPT, Claude, and GitHub Copilot, to streamline specific parts of the development process.

