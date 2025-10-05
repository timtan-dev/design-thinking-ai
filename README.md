# Design Thinking AI Agent

An AI-powered application that guides users through the complete Design Thinking process with intelligent assistance at every stage.

## Overview

The Design Thinking AI Agent helps teams and individuals systematically innovate and solve problems using the proven Design Thinking methodology. With integrated AI assistance, automated template generation, and comprehensive project management, this tool streamlines the entire creative process from empathy research to implementation.

## Features

- **6-Stage Design Thinking Process**: Empathise, Define, Ideate, Prototype, Test, Implement
- **AI-Powered Generation**: Automatic creation of interview questions, personas, journey maps, and more
- **Research Data Management**: Upload and analyze interviews, surveys, observations
- **Template Library**: Pre-built templates for all research and analysis methods
- **Progress Tracking**: Save and resume projects at any stage
- **Export Capabilities**: Generate comprehensive PDF and DOCX reports
- **Database Integration**: SQLite (development) and PostgreSQL (production) support

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Git (optional)

### Installation

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd design-thinking-ai
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env` to create your configuration
   - Add your OpenAI API key: `OPENAI_API_KEY=sk-...`
   - Update other settings as needed

5. **Initialize the database**
   ```bash
   python scripts/init_database.py
   ```

6. **Optional: Load sample data**
   ```bash
   python scripts/seed_data.py
   ```

## Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Workflow

1. **Home Page**: Create a new project by entering the area and goal
2. **Empathise**:
   - Collect data using various research methods (interviews, surveys, observations)
   - Analyze data with empathy maps, personas, journey maps
3. **Define**: Create problem statements and "How Might We" questions
4. **Ideate**: Brainstorm and evaluate ideas using structured methods
5. **Prototype**: Design user flows and define features
6. **Test**: Generate test scenarios and collect feedback
7. **Implement**: Create implementation roadmap and export final report

### Project Structure

```
design-thinking-ai/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration
├── config/                     # Application configuration
│   ├── settings.py
│   └── database.py
├── database/                   # Database models and operations
│   ├── models.py
│   ├── migrations/
│   └── crud/
├── pages/                      # Streamlit multi-page app
│   ├── 1_🏠_Home.py
│   ├── 2_💭_Empathise.py
│   ├── 3_📋_Define.py
│   ├── 4_💡_Ideate.py
│   ├── 5_🔨_Prototype.py
│   ├── 6_🧪_Test.py
│   └── 7_🚀_Implement.py
├── components/                 # Reusable UI components
├── services/                   # Business logic and AI services
├── prompts/                    # AI prompt templates
├── utils/                      # Utility functions
├── assets/                     # Static files (CSS, templates)
├── tests/                      # Unit tests
└── scripts/                    # Database and utility scripts
```

## Configuration

### Database

By default, the application uses SQLite for local development. To switch to PostgreSQL:

1. Update `DATABASE_URL` in `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost/design_thinking
   ```

2. Ensure PostgreSQL is running and the database exists

### OpenAI API

The application uses OpenAI's GPT models for AI generation. Ensure your API key has sufficient credits and quota.

## Development

### Running Tests

```bash
pytest tests/
```

### Adding New Features

1. Create new service in `services/` for business logic
2. Add prompt templates in `prompts/` for AI generation
3. Create UI components in `components/` for reusability
4. Update relevant page in `pages/` to integrate the feature

## Troubleshooting

- **Database errors**: Run `python scripts/init_database.py` to recreate tables
- **OpenAI API errors**: Check API key and rate limits
- **File upload issues**: Verify `data/uploads/` directory exists and has write permissions
- **Import errors**: Ensure virtual environment is activated and dependencies are installed

## License

MIT License - feel free to use and modify for your projects.

## Support

For issues and questions, please create an issue in the repository or contact the development team.
