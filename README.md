# Biocore Feedback

Simple wrapper to send feedbacks via Slack.

A lightweight, standalone central Slack feedback microservice and zero-dependency embeddable Web Component for Biocore CRG web applications.

Allows users across any application (Django, R Shiny, Vue/React, FastAPI, or static HTML) to send suggestions, bug reports, and questions directly to a team Slack channel via an unobtrusive floating badge.

---

## Architecture Overview

```
Any Web App (Django, Shiny, Vue, etc.)
  │
  ├─► Loads: <script src="https://feedback.crg.es/widget.js" defer></script>
  │          <biocore-feedback app-name="Genomics Apps"></biocore-feedback>
  │
  └─► Submits feedback directly to Central Microservice:
        POST https://feedback.crg.es/api/feedback
        │
        └─► Formats Block Kit & delivers to Slack Incoming Webhook
```

- **Zero App Dependencies**: Host apps don't need any backend code or Slack tokens.
- **Isolated Styles**: The widget uses native **Shadow DOM**, preventing any CSS interference with Bootstrap, Tailwind, or custom styles.
- **Auto Context**: Captures the application name and current page URL automatically.
- **Privacy & Security**: Slack Webhook secrets stay on the central server; built-in IP rate limiting prevents channel spam.

---

## 1. Quick Setup & Running the Server

### Prerequisites
1. Create a Slack App in your workspace with an **Incoming Webhook** pointing to your feedback channel (e.g. `#app-feedback`).
2. Clone this repo:
   ```bash
   git clone git@github.com:biocorecrg/biocore_feedback.git
   cd biocore_feedback
   ```
3. Copy `.env.example` to `.env` and fill in your webhook URL:
   ```bash
   cp .env.example .env
   # Edit .env:
   # SLACK_WEBHOOK_URL="https://hooks.slack.com/services/T000.../B000.../XXXX..."
   ```

### Running Locally with Python
```bash
uv venv .venv
source .venv/bin/activate
uv pip install -e .
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### Running with Docker / Docker Compose
```bash
docker compose up -d --build
```
Health check endpoint: `http://localhost:8080/health`.

---

## 2. Embedding in Any Web Application

Just add two lines before `</body>` in your HTML or template:

```html
<script src="https://feedback.crg.es/widget.js" defer></script>
<biocore-feedback app-name="My CRG App"></biocore-feedback>
```

*(For local development testing, replace `https://feedback.crg.es/` with `http://127.0.0.1:8080/`)*.

### Optional Attributes

| Attribute | Default | Description |
| :--- | :--- | :--- |
| `app-name` | `document.title` | Name of the app shown in the feedback form and sent to Slack |
| `api-url` | Origin of `widget.js` + `/api/feedback` | Custom API endpoint URL if needed |

---

## 3. Running Tests

```bash
python -m pytest -v
```
