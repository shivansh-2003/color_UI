# 🎨 AI Color Suggester API

![AI Color Suggester Banner](https://via.placeholder.com/1200x300/3498db/ffffff?text=AI+Color+Suggester+API)

A sophisticated color suggestion system that uses Google's Gemini and Groq's LLM to analyze UI images and project descriptions to generate optimal color palettes for designers and developers.

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Python 3.10](https://img.shields.io/badge/Python-3.10-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/Gemini_AI-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [Local Setup](#local-setup)
  - [Docker Setup](#docker-setup)
- [Configuration](#-configuration)
- [API Endpoints](#-api-endpoints)
- [Response Models](#-response-models)
- [Usage Examples](#-usage-examples)
  - [cURL](#curl)
  - [Python](#python)
  - [Android (Kotlin)](#android-kotlin)
- [Detailed Analysis](#-detailed-analysis)
- [Deployment](#-deployment)
  - [Render Deployment](#render-deployment)
  - [Other Cloud Platforms](#other-cloud-platforms)
- [Performance Considerations](#-performance-considerations)
- [Error Handling](#-error-handling)
- [Security Considerations](#-security-considerations)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)
- [Contact](#-contact)

## 🔍 Overview

The AI Color Suggester API is a powerful tool that combines state-of-the-art AI technologies to help designers and developers select optimal color palettes for their UI designs. By analyzing both UI images and project descriptions, the system provides comprehensive color recommendations tailored to the specific needs of each project.

### How It Works

1. **Image Analysis**: Uploads a UI/app image to Google's Gemini 1.5 Flash API for dominant color extraction
2. **Description Analysis**: Processes project descriptions through Groq's LLama 3 70B model via LangChain to generate contextually appropriate colors
3. **Intelligent Palette Organization**: Combines both sources to create a harmonious, accessible color palette
4. **Detailed Analysis**: Provides reasoning and comparisons between current and suggested colors
5. **UI Component Recommendations**: Suggests specific colors for common UI elements like buttons, headers, etc.

## ✨ Features

- **Dual AI Analysis**: Combines image-based color extraction with description-based color suggestions
- **Detailed Color Analysis**: Provides reasoning for color suggestions with accessibility considerations
- **UI Component Color Mapping**: Recommends specific colors for common UI elements
- **Perfect Match Detection**: Identifies when current colors already match ideal suggestions
- **Accessibility Compliance**: Ensures color palettes maintain proper contrast ratios
- **Docker Support**: Easy containerization for consistent deployment
- **Android Integration**: Ready-to-use Kotlin code for Android apps
- **Comprehensive API Documentation**: Interactive Swagger UI documentation

## 🏗 System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Client (Web,   │     │  FastAPI        │     │  AI Services    │
│  Mobile, etc.)  │◄────┤  Application    │◄────┤  (Gemini &      │
│                 │     │                 │     │  Groq/LangChain) │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        ▲                       ▲                       ▲
        │                       │                       │
        └───────────────────────┴───────────────────────┘
                       Communication Flow
```

## 🔧 Tech Stack

- **Backend Framework**: FastAPI
- **AI Image Analysis**: Google Gemini 1.5 Flash
- **AI Text Processing**: Groq's LLama 3 70B via LangChain
- **Containerization**: Docker
- **Environment Management**: python-dotenv
- **Image Processing**: Pillow
- **HTTP Requests**: Requests
- **API Client (Android)**: Retrofit with OkHttp

## 📋 Prerequisites

- Python 3.10+
- Google Gemini API key (obtain from [Google AI Studio](https://ai.google.dev/))
- Groq API key (obtain from [Groq Console](https://console.groq.com/))
- Docker and Docker Compose (for containerized deployment)

## 🚀 Installation

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-color-suggester.git
   cd ai-color-suggester
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. Run the FastAPI application:
   ```bash
   uvicorn main:app --reload
   ```

6. Access the API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Docker Setup

1. Create a `.env` file with your API keys as described above.

2. Build and start the Docker container:
   ```bash
   docker-compose up -d
   ```

3. Access the API at [http://localhost:8000](http://localhost:8000)

## ⚙️ Configuration

The application uses environment variables for configuration:

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `GROQ_API_KEY` | Groq API key | Yes |
| `ENVIRONMENT` | Set to "production" for production mode | No |
| `PORT` | Port to run the server on (default: 8000) | No |

## 📚 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint with API info |
| `/api/suggest-colors` | POST | Generate color suggestions |
| `/health` | GET | API health check |
| `/docs` | GET | API documentation (Swagger UI) |

### Detailed Endpoint Descriptions

#### `GET /`
Returns basic API information and available endpoints.

#### `POST /api/suggest-colors`
Analyzes a UI image and project description to generate color suggestions.

**Request Parameters:**
- `image` (file, required): UI/App image file
- `description` (form, required): Project description text

**Supported Image Formats:**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)

#### `GET /health`
Returns the health status of the API, including API key configuration.

## 📊 Response Models

### ColorPaletteWithAnalysis

```json
{
  "image_based": ["#f2f2f2", "#e0e0e0", ...],
  "description_based": ["#4567b7", "#8bc34a", ...],
  "organized_palette": {
    "primary": "#f2f2f2",
    "secondary": "#e0e0e0",
    "accent": "#4567b7",
    "background": "#f2f2f2",
    "text": "#333333",
    "additional": ["#3e54ac", "#6d82c6", "#90a9d9"],
    "ui_components": {
      "button": "#f2f2f2",
      "button_hover": "#e0e0e0",
      "header": "#f2f2f2",
      "card_background": "#ffffff",
      "border": "#e0e0e0"
    }
  },
  "all_colors": ["#6495ed", "#6d82c6", ...],
  "color_analysis": {
    "primary": {
      "color": "#f2f2f2",
      "suggested_color": "#2196F3",
      "is_perfect_match": false,
      "reason": "The suggested color better aligns with your project's theme and enhances user experience"
    },
    "secondary": {
      "color": "#e0e0e0",
      "suggested_color": "#4CAF50",
      "is_perfect_match": false,
      "reason": "The suggested color provides better contrast and visual hierarchy"
    },
    // More color analyses...
  },
  "ui_recommendations": [
    {"component": "Button", "color": "#f2f2f2"},
    {"component": "Button hover", "color": "#e0e0e0"},
    // More recommendations...
  ],
  "additional_notes": [
    "All suggested colors have been checked for accessibility compliance",
    // More notes...
  ]
}
```

### ErrorResponse

```json
{
  "error": "Error message",
  "details": "Detailed error information",
  "request_id": "req_1681234567"
}
```

## 🧪 Usage Examples

### cURL

```bash
curl -X 'POST' \
  'http://localhost:8000/api/suggest-colors' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'image=@/path/to/your/ui_image.jpg;type=image/jpeg' \
  -F 'description=A modern e-commerce website for selling organic products with a focus on sustainability and eco-friendliness.'
```

### Python

```python
import requests

url = "http://localhost:8000/api/suggest-colors"

# Project description
description = "A modern e-commerce website for selling organic products with a focus on sustainability and eco-friendliness."

# Image file to analyze
files = {
    'image': ('ui_image.jpg', open('path/to/your/ui_image.jpg', 'rb'), 'image/jpeg')
}

# Form data
data = {
    'description': description
}

# Make the API request
response = requests.post(url, files=files, data=data)

# Print the results
if response.status_code == 200:
    result = response.json()
    print("Color Analysis:")
    for color_type, analysis in result["color_analysis"].items():
        print(f"\n{color_type.capitalize()}:")
        if analysis["is_perfect_match"]:
            print(f"  Color: {analysis['color']} (Perfect match!)")
        else:
            print(f"  Current: {analysis['color']} → Suggested: {analysis['suggested_color']}")
            print(f"  Reason: {analysis['reason']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### Android (Kotlin)

See the full implementation in the repository's `android-client` directory.

```kotlin
// Make sure to update the BASE_URL with your API endpoint
val repository = ColorSuggesterRepository(context)

// URI of the image to analyze
val imageUri = Uri.parse("content://path/to/your/image.jpg")

// Project description
val description = "A modern e-commerce website for selling organic products with a focus on sustainability and eco-friendliness."

// Make API call
viewModel.suggestColors(imageUri, description)

// Observe the results
viewModel.colorPalette.observe(this) { palette ->
    // Handle the color palette
    updateUI(palette)
}

viewModel.error.observe(this) { error ->
    // Handle any errors
    showError(error)
}
```

## 🔍 Detailed Analysis

The system performs a thorough analysis of your UI colors:

1. **Extraction**: Identifies dominant colors from your UI image
2. **Suggestion**: Generates contextually appropriate colors based on your project description
3. **Comparison**: Analyzes each color category (primary, secondary, accent, etc.)
4. **Reasoning**: Provides specific reasons for suggested improvements
5. **Accessibility**: Ensures all colors meet accessibility standards
6. **UI Mapping**: Maps colors to specific UI components for immediate application

## 📦 Deployment

### Render Deployment

Follow these steps to deploy to Render:

1. Create a new Web Service in Render
2. Connect your GitHub repository
3. Set as Python 3 environment
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables for `GEMINI_API_KEY` and `GROQ_API_KEY`
7. Set `ENVIRONMENT` to `production`

### Other Cloud Platforms

The application is compatible with any cloud platform that supports Docker containers or Python applications, including:

- AWS Elastic Beanstalk
- Google Cloud Run
- Azure App Service
- Heroku

## ⚡ Performance Considerations

- **Cold Start**: Initial API calls may take longer (5-10 seconds) due to AI model loading
- **Timeout Settings**: Set client timeouts to at least 30 seconds for reliable operation
- **API Quotas**: Be aware of usage limits for Gemini and Groq APIs
- **Caching**: Consider implementing caching for frequent requests with similar inputs
- **Image Size**: Large images are automatically resized for optimal processing

## 🔄 Error Handling

The API implements comprehensive error handling:

- **Input Validation**: Validates file types and required parameters
- **Structured Errors**: Returns consistent error responses with request IDs
- **Graceful Degradation**: Falls back to regex parsing if JSON extraction fails
- **Logging**: Detailed logging for debugging and auditing
- **Cleanup**: Ensures temporary files are removed even if processing fails

## 🔒 Security Considerations

- **API Keys**: Store API keys securely in environment variables, never in code
- **CORS**: Configure CORS settings for production to limit allowed origins
- **Input Sanitization**: All inputs are validated before processing
- **File Handling**: Temporary files are securely created and cleaned up
- **Error Messages**: Detailed error information is only provided in development mode

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [Google Gemini API](https://ai.google.dev/)
- [Groq API](https://console.groq.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://python.langchain.com/)
- [Docker](https://www.docker.com/)

## 📞 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter) - email@example.com

Project Link: [https://github.com/yourusername/ai-color-suggester](https://github.com/yourusername/ai-color-suggester)

---

*Made with ❤️ by Shivansh Mahajan*