# Biocore Feedback

Simple and universal feedback widget for Slack across Biocore CRG web applications.

Allows users across any application (Django, R Shiny, Vue/React, FastAPI, or static HTML) to send suggestions, bug reports, and questions directly to a team Slack channel via an unobtrusive floating badge.

Can be used in two modes:
1. **As an embedded Django plugin/package (No extra servers!)**: Runs directly inside your existing Django app.
2. **As an embeddable Web Component (`widget.js`) with optional central microservice**: For static HTML or non-Python apps.

---

## Mode 1: Embedded in a Django App (Zero Extra Servers)

### 1. Installation

Install directly from GitHub via `pip`:

```bash
pip install git+https://github.com/biocorecrg/biocore_feedback.git
```

Or add to your `requirements.txt`:
```text
git+https://github.com/biocorecrg/biocore_feedback.git
```

### 2. Configure Django `settings.py`

Add `"biocore_feedback"` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...,
    "biocore_feedback",
]
```

Configure your Slack Incoming Webhook in your `.env` file (or `settings.py`):

```ini
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/T000.../B000.../XXXX..."
```

*(Optional settings)*:
```python
# Rate limit per IP address (default: 10 submissions/minute)
BIOCORE_FEEDBACK_RATE_LIMIT = 10
```

### 3. Add URLs in your project's `urls.py`

```python
from django.urls import include, path

urlpatterns = [
    ...,
    path("api/feedback/", include("biocore_feedback.urls")),
]
```

### 4. Add the Widget to Your Template (`base.html`)

Load the template tag and place `{% biocore_feedback %}` right before `</body>`:

```html
{% load biocore_feedback %}

...
    {% biocore_feedback app_name="Genomics Apps" %}
  </body>
</html>
```

That's it! Your Django app serves the static widget script and relays feedback directly to Slack using its existing server process.

---

## Mode 2: Central Microservice / Standalone Container (Optional)

If you have non-Python apps (e.g. R Shiny, pure static pages) that need a central relay server:

### Quick Setup
1. Clone this repository on your server:
   ```bash
   git clone git@github.com:biocorecrg/biocore_feedback.git
   cd biocore_feedback
   ```
2. Copy `.env.example` to `.env` and set your `SLACK_WEBHOOK_URL`.
3. Run with Docker Compose:
   ```bash
   docker compose up -d --build
   ```

### Embed in any Web Page
```html
<script src="https://feedback.crg.es/widget.js" defer></script>
<biocore-feedback app-name="My CRG App"></biocore-feedback>
```

---

## Features

- **Zero CSS Clashes**: Built with native **Shadow DOM** so it never breaks or overrides Bootstrap, Tailwind, or custom app styles.
- **Auto Context**: Captures the application name and current page URL automatically.
- **Name Persistence**: Remembers the user's name in `localStorage` for future feedback.
- **Built-in Rate Limiting**: Protects your Slack channel from spam or accidental floods.
- **Rich Slack Block Kit Notifications**: Formats submissions into clear, readable Slack cards with links to the page.

---

## Running Tests

```bash
python -m pytest -v
```
