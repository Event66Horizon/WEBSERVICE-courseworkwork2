# XJCO3011 Coursework 2: Search Engine Tool

This project implements a Python command-line search engine for
`https://quotes.toscrape.com/`. It crawls the target site politely, builds a
positional inverted index, saves/loads that index from disk, and supports
single-word and multi-word search queries.

## Features

- Polite crawler with a mandatory 6-second minimum delay between requests.
- In-domain breadth-first crawling from `https://quotes.toscrape.com/`.
- Positional inverted index storing frequency and token positions per page.
- Case-insensitive tokenisation.
- `build`, `load`, `print`, and `find` shell commands.
- Multi-word query support with exact phrase boosting.
- TF-IDF style ranking for search results.
- JSON index persistence in `data/index.json`.
- Unit tests for crawler, indexer, search, tokenisation, persistence, and edge cases.
- Strict project tooling configuration for `pytest`, coverage, `ruff`, and `mypy`.

## Repository Structure

```text
xjco3011-search-engine-tool/
  src/
    crawler.py
    indexer.py
    search.py
    main.py
    models.py
    text_processing.py
  tests/
    fixtures/
    test_crawler.py
    test_indexer.py
    test_search.py
    test_text_processing.py
  data/
    index.json
  docs/
    architecture.md
    genai_declaration.md
    submission_checklist.md
    video_script.md
  .github/workflows/
    ci.yml
  requirements.txt
  pyproject.toml
  README.md
```

## Installation

Use Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Usage

Start the interactive shell from the repository root:

```bash
python -m src.main
```

Then run the required commands:

```text
search> build
search> load
search> print nonsense
search> find indifference
search> find good friends
search> exit
```

The `build` command crawls the target site, creates the inverted index, and
saves it to `data/index.json`. The crawler deliberately waits at least 6 seconds
between requests, so the full crawl is expected to take time.

You can choose a different index path if needed:

```bash
python -m src.main --index data/index.json
```

## Command Behaviour

- `build`: crawls the website, builds the index, and saves it.
- `load`: loads the saved index from disk.
- `print <word>`: prints the inverted index for one word, including page URL,
  frequency, and token positions.
- `find <query phrase>`: returns ranked pages containing all query terms.

Invalid commands, empty queries, missing index files, and absent words are
reported clearly instead of crashing.

## Testing

Run the automated tests:

```bash
pytest
```

The project is configured to report coverage and fail below 85%:

```bash
pytest --cov=src --cov-report=term-missing
```

Optional quality checks:

```bash
ruff check .
mypy src tests
```

The crawler tests use local HTML fixtures and fake HTTP responses, so they do
not depend on external network access.

The repository includes a GitHub Actions workflow in `.github/workflows/ci.yml`
to run linting, type checking, and tests automatically after pushing to GitHub.

## Design Notes

The crawler uses breadth-first traversal and restricts itself to the original
domain. It canonicalises URLs by removing fragments and query strings to avoid
duplicate indexing. It extracts quote blocks when available and falls back to
page text for other HTML structures.

The inverted index is stored as:

```text
term -> url -> { frequency, positions }
```

This supports both the required `print` command and more advanced search
behaviour. The search engine intersects posting lists for all query terms,
checks exact phrase order using positional token lists, and ranks results using
a smoothed TF-IDF score with an exact-phrase boost.

See `docs/architecture.md` for complexity analysis and further design rationale.

## Referenced Libraries

- Requests: HTTP requests.
- Beautiful Soup: HTML parsing.
- pytest and pytest-cov: testing and coverage.
- ruff and mypy: static quality checks.
