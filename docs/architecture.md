# Architecture and Complexity Notes

## Components

- `crawler.py`: performs polite breadth-first crawling from the target website.
- `indexer.py`: builds and persists the positional inverted index.
- `search.py`: processes queries, intersects posting lists, detects phrases, and
  ranks results.
- `main.py`: exposes the required command-line shell.
- `text_processing.py`: centralises normalisation, tokenisation, and snippets.

## Data Structures

The main index is:

```text
dict[str, dict[str, Posting]]
term -> url -> Posting(url, frequency, positions)
```

This supports efficient lookup for the `print` command and efficient candidate
selection for the `find` command.

The index also stores:

- document metadata: title, text, crawl depth;
- token order per document for phrase matching;
- document lengths for TF-IDF ranking.

## Complexity

Let:

- `D` be the number of crawled pages;
- `T` be the total number of tokens across all pages;
- `Q` be the number of query terms;
- `P` be the number of candidate pages after posting-list intersection.

Index construction is `O(T)` because each token is normalised once and inserted
into dictionaries. Space usage is also `O(T)` because term positions are stored.

Single-term `print` lookup is `O(1 + R log R)`, where `R` is the number of pages
containing the term. The sort makes output deterministic and ranks by frequency.

Search candidate selection is approximately `O(Q * R)` for posting-list set
construction and intersection. Ranking is `O(P * Q)`. Exact phrase checking is
`O(P * L)`, where `L` is the document token length, because token slices are
checked for the phrase order.

For the coursework website this is intentionally simple and transparent. For a
large web corpus, the next optimisation would be phrase checking directly from
positional postings rather than scanning each candidate document's token list.

## Ranking

Results are ranked with smoothed TF-IDF:

```text
tf = term frequency in page / document length
idf = log((1 + document_count) / (1 + document_frequency)) + 1
score = sum(query_term_frequency * tf * idf)
```

Exact phrase matches receive a multiplier. This keeps all required behaviour
while demonstrating a realistic search-engine ranking idea beyond simple
keyword matching.

## Reliability

The crawler enforces the 6-second politeness window before successive requests,
restricts traversal to the target domain, canonicalises URLs, and skips failed
requests with a warning rather than terminating the whole crawl.

Tests mock HTTP responses so the suite is deterministic and can run without
network access. The real `build` command still uses live HTTP requests.

