# MOVIE COLLECTION BACKEND

The backend for my movie collection app. Just a fun way of learning Elasticsearch and Meilisearch.

[Frontend](https://github.com/srneha24/Movie-Collection-Frontend)

## Tech Stack

- **FastAPI** — API framework
- **Elasticsearch** — search engine
- **Meilisearch** — search engine
- **Pydantic** — data validation

## How It Works

The app dual-writes to both Elasticsearch and Meilisearch simultaneously. Reads are served by whichever engine is set via the `ENGINE_TO_USE` environment variable (`"elastic"` or `"meili"`). This makes it easy to compare both engines side by side.

## Setup

1. **Clone the repo and create a virtual environment:**

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your Elasticsearch and Meilisearch connection details.

3. **Start Elasticsearch and Meilisearch** — both must be running since writes go to both engines.

4. **Run the server:**

   ```bash
   fastapi dev main.py
   ```

## API Endpoints

| Method   | Endpoint            | Description                                        |
| -------- | ------------------- | -------------------------------------------------- |
| `POST`   | `/movie`            | Add a new movie                                    |
| `GET`    | `/movie`            | List movies (with search, filters, pagination)     |
| `GET`    | `/movie/{movie_id}` | Get a movie by ID                                  |
| `PATCH`  | `/movie/{movie_id}` | Update a movie                                     |
| `DELETE` | `/movie/{movie_id}` | Delete a movie                                     |
| `GET`    | `/directors`        | List all unique directors                          |

### Query Parameters (GET /movie)

| Parameter      | Type   | Description                                                |
| -------------- | ------ | ---------------------------------------------------------- |
| `page`         | int    | Page number (default: 1)                                   |
| `limit`        | int    | Results per page (default: 10)                             |
| `search`       | string | Full-text search across title, synopsis, review, director  |
| `release_year` | int    | Filter by release year                                     |
| `rating`       | int    | Filter by rating bracket (1-5)                             |
| `director`     | string | Filter by director name                                    |

## Environment Variables

| Variable                | Description                                                         |
| ----------------------- | ------------------------------------------------------------------- |
| `ELASTICSEARCH_API_KEY` | API key for Elasticsearch                                           |
| `ELASTICSEARCH_HOST`    | Elasticsearch URL (default: `http://localhost:9200/`)               |
| `MEILISEARCH_API_KEY`   | API key for Meilisearch                                             |
| `MEILISEARCH_HOST`      | Meilisearch URL (default: `http://localhost:7700/`)                 |
| `INDEX_NAME`            | Index name used in both engines (default: `movies`)                 |
| `ENGINE_TO_USE`         | `"elastic"` or `"meili"` — selects the read engine                  |
| `FRONTEND_URL`          | Frontend origin for CORS (default: `http://localhost:3000`)         |
