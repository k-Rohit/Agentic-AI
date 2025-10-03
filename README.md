# The AI You - Chatbot

A Streamlit-based AI chatbot that represents you professionally, answering questions about your background, skills, and experience.

## Features

- 🤖 AI-powered chatbot using OpenAI GPT-4o-mini
- 💬 Interactive chat interface with message history
- 📝 Example questions to get started
- 📧 Contact form integration
- 🔔 Pushover notifications for user interactions
- 📄 PDF summary integration for context

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Secrets

Streamlit uses secrets management for secure API key storage. You have two options:

#### Option A: Local Development (.streamlit/secrets.toml)

1. Copy the secrets template:
```bash
cp .streamlit/secrets.toml .streamlit/secrets.toml.local
```

2. Edit `.streamlit/secrets.toml.local` and replace the placeholder values:
```toml
OPENAI_API_KEY = "your_actual_openai_api_key"
PUSHOVER_USER = "your_actual_pushover_user_key"
PUSHOVER_TOKEN = "your_actual_pushover_app_token"
```

3. Use the local secrets file:
```bash
streamlit run chatbot.py --secrets .streamlit/secrets.toml.local
```

#### Option B: Streamlit Cloud Deployment

1. In your Streamlit Cloud dashboard, go to your app settings
2. Navigate to "Secrets" section
3. Add the following secrets:
   ```
   OPENAI_API_KEY = "your_openai_api_key"
   PUSHOVER_USER = "your_pushover_user_key"
   PUSHOVER_TOKEN = "your_pushover_app_token"
   ```

### 3. Prepare Your Summary

Place your professional summary in `summary.pdf` in the root directory. This will be used as context for the chatbot.

### 4. Run the Application

```bash
streamlit run chatbot.py
```

The application will open in your browser at `http://localhost:8501`.

## API Keys Required

- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Pushover Credentials**: Get from [Pushover](https://pushover.net/) for notifications

## Project Structure

```
├── chatbot.py          # Main Streamlit application
├── tools.py            # Tool functions for user interactions
├── utils.py            # Utility functions (PDF reading, notifications)
├── summary.pdf         # Your professional summary
├── requirements.txt    # Python dependencies
└── .streamlit/
    ├── secrets.toml    # Secrets template
    └── config.toml     # Streamlit configuration
```

## Usage

1. Start the app with `streamlit run chatbot.py`
2. Ask questions about your background, skills, or experience
3. Use the example questions to get started
4. The chatbot will answer based on your PDF summary
5. Users can submit contact information through the "Get in touch" section

## Security Notes

- Never commit actual API keys to version control
- Use Streamlit's secrets management for production
- The `.streamlit/secrets.toml` file is gitignored by default
- For local development, use a separate secrets file as shown above
