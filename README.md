# 🔭 LLM Observatory: Enterprise LLM Monitoring & Cost Analysis Platform

A comprehensive LLM observability platform designed for enterprise environments, providing real-time monitoring, cost tracking, and performance analytics across multiple LLM providers (OpenAI and Anthropic).

## 🌟 Key Features

- **Multi-Provider Support**: 
  - OpenAI Integration (GPT-4, GPT-3.5)
  - Anthropic Integration (Claude-3 family)
  - Extensible architecture for additional providers

- **Enterprise-Grade Monitoring**:
  - Real-time cost tracking and analysis
  - Token usage monitoring
  - Performance metrics and latency tracking
  - Environment-specific configurations (Dev, Test, Int, Prod)

- **Cost Management**:
  - Granular cost tracking per request
  - Token-level cost breakdown
  - Usage trends and patterns
  - Budget monitoring and alerts

- **Performance Analytics**:
  - Response time monitoring
  - Token processing rates
  - Error rate tracking
  - Retry mechanism with exponential backoff

- **Enterprise Features**:
  - Environment segregation
  - Application-level tracking
  - Session-based monitoring
  - Comprehensive logging

## 🏗️ Architecture

```plaintext
LLM Observatory/
├── src/
│   ├── config/        # Configuration management
│   ├── llm/           # LLM provider implementations
│   ├── interface/     # Streamlit UI components
│   └── monitoring/    # Monitoring implementations
└── tests/            # Comprehensive test suite
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- OpenAI API Key
- Anthropic API Key
- Virtual Environment

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/llm-observatory.git
cd llm-observatory
```

2. **Set up virtual environment:**
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
# Create .env file
cp .env.example .env

# Add your API keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

## 💼 Enterprise Usage

1. **Start the application:**
```bash
streamlit run src/interface/app.py
```

2. **Configure your environment:**
   - Select environment (Dev/Test/Int/Prod)
   - Enter application identifier
   - Choose LLM provider and model

3. **Monitor costs and performance:**
   - Track real-time costs
   - Monitor response times
   - Analyze token usage
   - View detailed metrics

## 📊 Cost Analysis

The platform provides detailed cost tracking:

- **Per-Request Costs:**
  - Input token costs
  - Output token costs
  - Total cost calculation

- **Aggregated Metrics:**
  - Session-based totals
  - Application-level costs
  - Environment-specific tracking

## 🔍 Monitoring Capabilities

- **Real-time Metrics:**
  - Response latency
  - Token processing rates
  - Error rates
  - Retry statistics

- **Session Analytics:**
  - Token usage trends
  - Cost patterns
  - Performance metrics
  - Environmental impact

## 🛠️ Development

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/test_llm/test_openai.py -v
```

### Adding New LLM Providers

1. Implement the `BaseLLM` abstract class
2. Add provider configuration in `settings.py`
3. Create corresponding test suite

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 👤 Author

Pinaki Guha  
- LinkedIn: [https://www.linkedin.com/in/pinakiguha/]
- Email: [pinaki.guha@gmail.com]
- Portfolio: [https://github.com/gpinaki]

## 🌟 Enterprise Benefits

- **Cost Optimization:** Track and optimize LLM usage costs
- **Performance Monitoring:** Real-time performance metrics
- **Multi-Environment Support:** Development to Production coverage
- **Provider Agnostic:** Support for multiple LLM providers
- **Scalable Architecture:** Built for enterprise requirements

## 🔜 Roadmap

- [ ] Additional LLM provider integrations
- [ ] Advanced cost prediction models
- [ ] Custom alert configurations
- [ ] Database integration for historical analysis
- [ ] Enhanced security features


## 🙏 Acknowledgments

- OpenAI and Anthropic for their robust APIs
- Streamlit for the excellent UI framework
- The open-source community for inspiration and tools

