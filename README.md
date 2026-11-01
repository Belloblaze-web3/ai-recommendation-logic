# SignalMatch — AI Recommendation Logic

**DecodeLabs Internship · Project 3**

SignalMatch is an explainable, content-based recommendation system that matches a user's interests with relevant learning resources. It demonstrates how transparent similarity logic can convert simple preference data into useful, ranked recommendations without requiring a complex machine-learning model.

> **Project goal:** collect user interests, compare them with item attributes, and return recommendations with a clear explanation of why each item was selected.

## Highlights

- **Explainable ranking:** every result includes a score, matched interests, and component-level score details.
- **Hybrid similarity model:** combines tag similarity, keyword overlap, rating alignment, and popularity.
- **Two user interfaces:** interactive command-line application and responsive Flask web UI.
- **JSON API:** exposes recommendations for integration with other applications.
- **Reusable architecture:** the CLI and web app both call the same recommendation engine.
- **Tested implementation:** 11 automated tests cover the engine, validation, Flask routes, API responses, and route manifest.
- **Zero external AI services:** runs locally with Python and Flask.

## Demo flow

```text
User interests
      │
      ▼
Normalize and tokenize input
      │
      ▼
Compare interests with catalog attributes
      │
      ▼
Calculate transparent weighted score
      │
      ▼
Return ranked recommendations + explanation
```

Example input:

```text
python, machine learning, data visualization
```

Example output:

```text
1. Practical Machine Learning [AI]
   Score: 0.483 | Rating: 4.8/5
   Why: matches your interests: data, learning, machine, python
```

## Recommendation algorithm

The system uses a deterministic weighted score for each catalog item:

```text
final_score = 0.55 × tag_similarity
            + 0.25 × keyword_similarity
            + 0.15 × rating_alignment
            + 0.05 × popularity
```

| Component | Weight | Purpose |
|---|---:|---|
| Tag similarity | 55% | Measures overlap between user interests and item tags using Jaccard similarity. |
| Keyword similarity | 25% | Compares interests with the item's title, description, and category. |
| Rating alignment | 15% | Rewards items close to an optional user-preferred rating. |
| Popularity | 5% | Provides a lightweight tie-breaker between otherwise similar items. |

This is intentionally a **content-based** recommender. It aligns a user profile with item attributes rather than learning from a large user-item interaction history.

## Architecture

```text
┌─────────────────┐      ┌──────────────────────┐
│ CLI: app.py     │─────▶│                      │
└─────────────────┘      │                      │
                          │ recommender.py      │────▶ catalog.json
┌─────────────────┐      │ RecommendationEngine│
│ Flask: web_app  │─────▶│                      │
└─────────────────┘      └──────────────────────┘
          │
          ├── HTML interface: templates/index.html
          └── JSON API: /api/recommend
```

## Repository structure

```text
.
├── app.py                       # Command-line interface
├── web_app.py                   # Flask application and JSON API
├── recommender.py               # Tokenization, scoring, and ranking engine
├── catalog.json                 # Sample learning-resource catalog
├── requirements.txt             # Python dependencies
├── templates/index.html         # Web UI template
├── static/styles.css            # Responsive web styling
└── tests/
    ├── test_recommender.py     # Core-engine tests
    └── test_web_app.py          # Flask route and API tests
```

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/Belloblaze-web3/ai-recommendation-logic.git
cd ai-recommendation-logic
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

## Run the application

### Flask web UI

```bash
python3 web_app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) and enter interests such as `Python, machine learning, data visualization`.

### Command-line interface

```bash
python3 app.py --interests "python, machine learning" --top 5
```

Optional preferred rating:

```bash
python3 app.py --interests "data, analytics" --rating 4.5 --top 3
```

## API usage

Request recommendations with a GET request:

```bash
curl "http://127.0.0.1:5000/api/recommend?interests=python,machine%20learning"
```

The API returns ranked items with their score, category, matched interests, and score breakdown:

```json
{
  "recommendations": [
    {
      "id": "ml-foundations",
      "title": "Practical Machine Learning",
      "category": "AI",
      "score": 0.483,
      "matched_interests": ["learning", "machine", "python"],
      "breakdown": {
        "tag_similarity": 0.2143,
        "keyword_similarity": 0.1875,
        "rating_alignment": 0.75,
        "popularity": 0.92
      }
    }
  ]
}
```

## Run tests

```bash
python3 -m unittest discover -s tests -v
```

Expected result: **11 tests passing**.

## Design decisions

- **Explainability over complexity:** the scoring method is easy to inspect, debug, and communicate.
- **Shared core, multiple interfaces:** recommendation logic is isolated from presentation and transport concerns.
- **Graceful validation:** empty or meaningless interests return a clear error instead of a misleading recommendation list.
- **Extensible catalog:** new resources can be added to `catalog.json` without changing the engine.

## Future improvements

- Collect explicit user feedback and ratings to tune score weights.
- Add Precision@K, Recall@K, and user-feedback evaluation metrics.
- Introduce collaborative filtering after collecting interaction history.
- Add a cold-start strategy for new users and new catalog items.
- Persist user profiles and recommendation history.
- Add authentication and a production deployment configuration.

## Project context

This project was completed as **Project 3 during my DecodeLabs Artificial Intelligence internship**, focusing on recommendation logic, pattern matching, and practical AI engineering fundamentals.

## License

This project is provided for educational and portfolio purposes.
