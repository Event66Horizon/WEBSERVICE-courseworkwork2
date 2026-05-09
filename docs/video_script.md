# Five-Minute Video Script

## 0:00-2:00 Live Demonstration

Open the terminal in the repository root.

1. Run `python -m src.main`.
2. Run `build` and explain that the crawler waits at least 6 seconds between
   HTTP requests to satisfy the politeness requirement.
3. Run `load` to prove the JSON index can be restored from disk.
4. Run `print good` and point out URL, frequency, and positions.
5. Run `find indifference` for a single-word query.
6. Run `find good friends` for a multi-word query.
7. Show `find` with an empty query and a missing word to demonstrate edge cases.

## 2:00-3:30 Code Walkthrough and Design Decisions

Show:

- `src/crawler.py`: breadth-first crawling, domain restriction, URL
  canonicalisation, and 6-second politeness enforcement.
- `src/indexer.py`: positional inverted index structure:
  `term -> url -> frequency and positions`.
- `src/search.py`: posting-list intersection, phrase detection, and TF-IDF
  ranking with phrase boost.
- `src/main.py`: required shell commands.

Explain the trade-off: JSON is readable and easy to mark; a database would be
more scalable but unnecessary for this coursework website.

## 3:30-4:00 Testing

Run:

```bash
pytest --cov=src --cov-report=term-missing
```

Explain that crawler tests use fake responses and local HTML fixtures so tests
are deterministic and do not hit the real website.

## 4:00-4:30 Version Control

Run:

```bash
git log --oneline --decorate --graph
```

Explain that commits were made incrementally: crawler, indexer, search, CLI,
tests, and documentation.

## 4:30-5:00 GenAI Critical Evaluation

State which GenAI tool was used and for what. Include concrete examples:

- Helpful: planning the module separation, generating candidate edge cases,
  reviewing whether the index stored enough statistics.
- Risky or limiting: AI suggestions must be verified because generated crawler
  code may ignore politeness delays or over-simplify phrase search.
- Learning impact: using AI helped compare designs faster, but understanding
  came from debugging tests, checking data structures, and explaining each
  module in my own words.

