# M4: AI-News Bot

## Description

AI-News Bot is an automated service that collects news from various sources (websites and Telegram channels), uses AI to generate engaging and concise posts, and publishes them to a Telegram channel. The system includes scheduled collection, filtering, AI generation, and publication with API management.

## Features

- **News Collection**: Collects news from websites and Telegram channels.
- **AI Post Generation**: Uses OpenAI GPT-4 to create posts from news summaries.
- **Telegram Publishing**: Publishes generated posts to Telegram channels.
- **Keyword Filtering**: Filters news by keywords before AI generation.
- **API Management**: REST API for managing sources, keywords, and posts.
- **Scheduled Tasks**: News collection runs every 30 minutes via Celery Beat.
- **Manual Generation**: API endpoint for manual post generation.
- **API Documentation**: Automatic documentation via FastAPI (`/docs`).

## Tech Stack

- **Python 3.14**
- **FastAPI** - API framework
- **Celery** - Task queue
- **Redis** - Broker for Celery
- **OpenAI API** - AI generation
- **Telethon** - Telegram integration
- **BeautifulSoup** - Web scraping
- **SQLAlchemy** - ORM
- **Docker** - Containerization

## Installation

### Prerequisites

- Docker
- Docker Compose

### Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd aibot
   ```
2. **Create `.env` file** (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```
   
   Fill in the required values:

   - `TELEGRAM_API_ID`
   - `TELEGRAM_API_HASH`
   - `TELEGRAM_PHONE`
   - `OPENAI_API_KEY`
   - `TELEGRAM_CHANNEL`

3. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```
   
4. **Access the API**:

   - API: `http://localhost:8000`
   - Documentation: `http://localhost:8000/docs`

   API Endpoints:

   - `GET /api/v1/sources/` - Get all sources
   - `POST /api/v1/sources/` - Create a source
   - `PUT /api/v1/sources/{id}` - Update a source
   - `DELETE /api/v1/sources/{id}` - Delete a source
   - `GET /api/v1/keywords/` - Get all keywords
   - `POST /api/v1/keywords/` - Create a keyword
   - `PUT /api/v1/keywords/{id}` - Update a keyword
   - `DELETE /api/v1/keywords/{id}` - Delete a keyword
   - `GET /api/v1/posts/` - Get all posts
   - `POST /api/v1/generate/` - Manually generate a post for a news item

## Architecture

- **News Collection**: Runs every 30 minutes via Celery Beat.
- **AI Generation**: Processes news summaries via OpenAI.
- **Telegram Publishing**: Sends posts to specified channels.
- **Database**: SQLite for storage (can be changed via `DATABASE_URL`).

## Configuration

- **News Collection Schedule**: Every 30 minutes (1800 seconds).
- **Timezone**: UTC.
- **Celery Pools**: `--pool=solo` for Windows compatibility.
