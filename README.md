# Genbook

A Tkinter desktop app for AI-powered chat with Gemini, with built-in note-taking and PDF export.

---

## Requirements

Install dependencies before running:

```
pip install google-generativeai markdown-pdf beautifulsoup4 markdown
```

---

## How to Run

```
python "Cookbook GUI_Whole_init.py"
```

---

## How to Use

### 1. Connect to Gemini
1. On launch, an API key dialog appears.
2. Enter your **Gemini API key**.
3. Click **Load Models** — the app queries the Gemini API and populates the model dropdown.
4. Select a model, or leave it on **Auto (Recommended)** to use the best available model automatically.
5. Click **Confirm** to connect. The active model is shown at the top of the chat window.

> Your last model selection is saved and restored on the next launch via `genbook_config.json`.

---

### 2. Chat
- Type your question in the input box at the bottom.
- Press **Ctrl+Enter** to send and receive a response.
- Responses are displayed in the chat area above.

---

### 3. Take Notes (PDF)

| Button | Action |
|---|---|
| **New Note** | Start a new PDF note session |
| **Edit Context** | Open the latest Q&A in an editor to review or modify before saving |
| **Note down current answer** | Append the current (or edited) Q&A to the PDF |
| **Save Note** | Enter a title and author name, then export as `.pdf` |

> Only the most recent Q&A is added per "Note down" click. Use **Edit Context** to adjust content before saving.

---

## File Structure

| File | Purpose |
|---|---|
| `Cookbook GUI_Whole_init.py` | Main GUI application |
| `Cookbook_Func_init.py` | Backend: Gemini API, model discovery, PDF generation, Markdown utilities |
| `genbook_config.json` | Auto-generated config storing last model selection |

---

## Notes

- A Gemini API key is required. Get one at [Google AI Studio](https://aistudio.google.com/).
- The PDF is only saved when **Save Note** is clicked. Closing the app before saving will lose unsaved notes.
- **Do not commit your API key** to version control.
