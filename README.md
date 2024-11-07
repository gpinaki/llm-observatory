# 🔭 LLM Observatory
### _Unified Platform for multi-vendor LLM Analytics & Observability_

A comprehensive AI Observability Platform designed for enterprise-scale LLM operations. Enable data-driven decisions through real-time cost analysis, performance monitoring, and cross-provider model response analytics (OpenAI, Anthropic, and Google's Gemini).

![clean-chat](assets/screenshots/clean_chat_interface.png)

## Features

### Multi-Provider Model Integration
![Feature-1](assets/screenshots/chat_interface.png)
- Unified Interface: Single interface for OpenAI, Anthropic, and Gemini models (more to come!).
- Advanced Control Panel: Tailored monitoring for each provider's unique characteristics.
- Cross-Provider Analytics: Compare performance and costs across providers
### Enterprise-Grade Analytics
![Feature-2](assets/screenshots/dashboard-cost.png)
- Real-Time Cost Tracking: Monitor costs as they occur across all providers.
- Token-Level Analysis: Detailed breakdown of input/output token usage and costs
- Metric Comparison Tools: Get real-time metrics with option to download for offline research
### Scalable & Modular Architecture 
- Enterprise-grade scalability: Offers extendable UI and API to instrument metrics across sessions, applications, and environemnts.
- Modular architecture: Esaily scalable for production deployment. 
- Download feature: Download session history in csv formart for offline research.


## ⚡️ Quick Start 

```
# Clone repository
git clone https://github.com/gpinaki/llm-observatory.git
cd llm-observatory

# Set up virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Add your API keys to .env:
# OPENAI_API_KEY=your-key
# ANTHROPIC_API_KEY=your-key
# VERTEX_API_KEY=your-key

# Launch application
streamlit run src/interface/app.py
```

## 💡 Usage Guide
### 1. Control Panel Configuration 
Use the Coniguration section in the sidebar to do the following.
- **Application and Environment Tracking**: Enter application name and choose environment for auditing.

   <img src="assets/screenshots/select_config.png" width="550" height="450">

- **Provider and Model Selection**: Choose provider, then select specific model for that provider.

    ![Main Interface](assets/screenshots/select_model.png)

- **Advanced Configuration**: Adjust token limits and temprature. 

    ![Select-Model](assets/screenshots/advanced_config.png)

- **Easily switch to dashboard**: Toggle to view performance analytics

    ![toggle-for-analytics](assets/screenshots/toggle_performance.png)

### 2. Interactive unified chat interface
- Real-time interaction with selected LLM provider.

    ![clean-chat](assets/screenshots/clean_chat_interface.png)

- Performance insight of a single request: View token usage and costs as you chat

    ![single-request](assets/screenshots/query_level_stat.png)

- Double-click detailed response: Click to get detailed response 

    ![detailed-response](assets/screenshots/detailed_response.png)

### 3. Analytics Dashboard 
Comprehensive analytics for decision-making.

- **Overview Tab**: Show a quick compaision of all models used.

    ![dashboard-1](assets/screenshots/dashboard-overview.png)

- **Cost Analysis Tab**: Monitor and compare provider costs

    ![dashboard-2](assets/screenshots/dashboard-cost.png)

- **Performance Tab**: Track and analyze response metrics

    ![dashboard-3](assets/screenshots/dashboard-response-metrics.png)

- **History Tab**: Review detailed interaction history

    ![dashboard-4](assets/screenshots/dashboard-call_history.png)

### 4. Download Capability 
- Click on "Download Complete Session Data" button to export all session metrics and interactions.

    ![download-csv][download-csv]


### Project Structure
```
llm-observatory/
├── src/
│   ├── llm/                    # LLM Provider Implementations
│   │   ├── base.py            # Abstract Base Class
│   │   ├── openai_llm.py      
│   │   ├── anthropic_llm.py   
│   │   └── gemini_llm.py      
│   ├── interface/             # UI Components
│   └── config/                # Configuration Management
├── tests/                     # Test Suite
└── assets/                    # Static Resources
```

## 🚀 Implementation Roadmap

### Current Implementation
- ✅ Multi-provider support (OpenAI, Anthropic,Gemini)
- ✅ Cost tracking and analysis
- ✅ Performance monitoring
- ✅ Environment and application instrumentation    
- ✅ Interactive dashboard
- ✅ Download Session  Summary

### Future Enhancements
- 🔄 Database integration
- 🔄 Custom alert configurations 
- 🔄 API Gateway integration
- 🔄 Additional model and vendor support 

## 📊 Benefits

- **Unified Interface**: Single UI and API to run queries and compare models across multiple providers.
- **Cost Optimization**: Model usage cost tracking across providers.
- **Metrics Dashboard**: Real-time performance metrics dashboard.
- **Download Capability**: Support CSV download for offline analysis.
- **Scalable Architecture**: Built for enterprise requirements, can be used in multi-environments and multi-application scenario.

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 👤 Author

Pinaki Guha  
- LinkedIn: [LinkedIn Profile][linkedin]
- Email: [pinaki.guha@gmail.com](mailto:pinaki.guha@gmail.com)
- Project Link: [LLM Observatory Repo][git-repo-url]
- Portfolio: [Github Link][Portfolio]

## 🙏 Acknowledgments

This project was developed by Pinaki Guha, with supplementary support from AI-based code assistance tools like ChatGPT, Claude, and GitHub Copilot, to streamline specific parts of the development process.

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job.)

   [git-repo-url]: <https://github.com/gpinaki/llm-observatory>
   [download-csv]: <assets/screenshots/download_csv.png>
   [download-button]: <assets/screenshots/download_history.png>
   [Portfolio]: <https://github.com/gpinaki>
   [linkedin]: <https://www.linkedin.com/in/pinakiguha/>
   
 
