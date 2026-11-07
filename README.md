# DutyKit

EU business duties for AI agents. Remote MCP server: `https://dutykit.dev/mcp` (public beta, free, no account).

Tools: `pflichten`, `rechnung_vorpruefen`, `werbung_vorpruefen`, `ki_hinweis`, `vat_pruefen`. Docs: https://dutykit.dev · https://dutykit.dev/llms.txt

```bash
claude mcp add --transport http dutykit https://dutykit.dev/mcp
```

The obligation catalogue (`pflichten.json`) lists for every entry the legal basis, the source URL, the check date and whether it was checked against the legal text (`belegt`) or not yet (`zu_pruefen`).

**Not legal advice.** Made with AI assistance.

## Run locally
```bash
uv run --with "mcp>=2" --with uvicorn uvicorn app:app --port 8080
```

## License
Code: MIT (see `LICENSE`). Obligation catalogue `pflichten.json`: CC BY 4.0 – please credit "DutyKit (dutykit.dev)".
