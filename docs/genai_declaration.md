# GenAI Declaration and Critical Evaluation Notes

## Declaration

GenAI was used as a development assistant for planning, code review,
documentation drafting, and identifying edge cases. All submitted code was
reviewed and adapted to fit the coursework requirements. I understand the code
structure, data structures, command behaviour, and tests.

## Specific Benefits

- Helped break the project into crawler, indexer, search, and CLI modules.
- Suggested edge cases such as empty queries, missing words, and missing index
  files.
- Helped compare simple keyword search with a positional index that can support
  phrase queries.
- Helped draft README and video structure so the demonstration covers the
  marking criteria within five minutes.

## Specific Limitations and Risks

- AI-generated crawler examples often omit explicit politeness enforcement.
  This was checked manually because the brief requires at least 6 seconds
  between requests.
- AI-generated search code can claim to support phrase queries while only
  intersecting word sets. This implementation checks token order using stored
  positions/token lists.
- AI can generate plausible but untested code. The project therefore includes
  deterministic unit tests using fixtures and fake HTTP responses.

## Learning Reflection

Using GenAI accelerated design comparison and documentation, but it did not
replace understanding. The most important learning came from reasoning about
the inverted index, verifying case-insensitive tokenisation, testing search
edge cases, and ensuring each command maps directly to the coursework brief.

