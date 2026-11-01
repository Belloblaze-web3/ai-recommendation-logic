
## Web interface

Install Flask and start the browser UI:

```bash
python3 -m pip install -r requirements.txt
python3 web_app.py
```

Then open `http://127.0.0.1:5000`. Enter interests such as `Python, machine learning, data visualization` and optionally provide a preferred rating.

The app also exposes a JSON endpoint:

```bash
curl "http://127.0.0.1:5000/api/recommend?interests=python,machine%20learning"
```

The web UI is implemented in `web_app.py`, `templates/index.html`, and `static/styles.css`. It uses the same `RecommendationEngine` as the CLI, so both interfaces share one source of recommendation logic.
