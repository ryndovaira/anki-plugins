# Fill the Blanks — Anki Plugin

Type-in-the-answer cloze cards for [Anki](https://apps.ankiweb.net/).

Adds a `fill-blanks:` template filter: write `{{fill-blanks:cloze:Field}}` on the front and each cloze part becomes its own input field.

Originally developed by [ssricardo](https://github.com/ssricardo/anki-plugins). This fork is maintained by [ryndovaira](https://github.com/ryndovaira).

See [fill-the-blanks/README.md](fill-the-blanks/README.md) for full documentation.

## Development

```bash
cd fill-the-blanks
uv sync
uv run pytest
```
