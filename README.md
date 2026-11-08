# DutyKit

[![MCP Registry](https://img.shields.io/badge/MCP%20Registry-io.github.renschrder--stack%2Fdutykit--eu--vat--invoice--compliance-1f5f4a)](https://registry.modelcontextprotocol.io/v0/servers?search=dutykit-eu-vat-invoice-compliance)
[![License: MIT](https://img.shields.io/badge/code-MIT-blue)](LICENSE)
[![Catalogue: CC BY 4.0](https://img.shields.io/badge/catalogue-CC%20BY%204.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)

EU business duties for AI agents. A remote MCP server that tells an agent which business rules apply in Germany, Luxembourg and the EU, with the legal source for every line, and lets it pre-check an invoice, a marketing message or a call before it acts.

**Endpoint:** `https://dutykit.dev/mcp` (Streamable HTTP, public beta, free, no account, 200 tool calls per day per IP, no inputs stored)
**Docs:** https://dutykit.dev · https://dutykit.dev/llms.txt · [Guides](https://dutykit.dev/blog/)

## Connect

Claude Code:
```bash
claude mcp add --transport http dutykit https://dutykit.dev/mcp
```

Any MCP client (JSON config):
```json
{ "mcpServers": { "dutykit": { "type": "http", "url": "https://dutykit.dev/mcp" } } }
```

## Tools

| Tool | What it does |
|---|---|
| `pflichten(land, taetigkeit)` | Obligations for `DE` or `LU` plus EU-wide, filtered by activity: `website`, `online_handel`, `rechnung`, `werbung`, `ki_kontakt`, `gruendung`, `datenschutz`, `produkte` |
| `rechnung_vorpruefen(rechnung, land="DE")` | Missing mandatory invoice fields under § 14 (4) and § 14a UStG, incl. intra-EU supplies (`art="ig_lieferung"`) and reverse charge; typed schema, reports unknown fields |
| `werbung_vorpruefen(kanal, empfaenger, einwilligung_belegt, bestandskunde)` | May the agent send this marketing email or make this call? (§ 7 UWG) |
| `ki_hinweis(firma, sprache)` | AI disclosure wording under AI Act Art. 50(1) in `de`, `fr`, `en`, `lb` |
| `vat_pruefen(ust_id, eigene_ust_id="")` | Live EU VAT ID check via the European Commission's VIES service; with your own VAT ID, VIES returns a consultation number as proof |
| `angebot()` | Pricing status, what is included, and when DutyKit is (not) the right fit |

Every check also returns a `nachweis` (timestamp, tool, responsible person, SHA-256 of the result) for the human who is liable.

## Example prompts
- "Before you publish the shop page: what does a website for a business in Luxembourg need?"
- "Check this invoice for missing mandatory fields before you send it."
- "May you send this newsletter to consumers who never opted in?"
- "Start every call with the AI disclosure sentence in French for Muster S.à r.l."

## Example result (`pflichten`, shortened)
```json
{
  "id": "de-impressum",
  "pflicht": "Impressum mit Name, ladungsfähiger Anschrift, schneller elektronischer Kontaktmöglichkeit, ggf. Register und USt-IdNr.",
  "grundlage": "§ 5 DDG",
  "quelle": "https://www.gesetze-im-internet.de/ddg/__5.html",
  "pruefstand": "belegt",
  "geprueft": "2026-11-07"
}
```

## Catalogue
`pflichten.json` lists for every entry the legal basis, the source URL, the check date and whether it was checked against the legal text (`belegt`) or not yet (`zu_pruefen`). Coverage today: DE, LU, EU (23 of 26 entries checked against the legal text, the rest marked `zu_pruefen`, reviewed weekly). Next: FR, BE. Corrections and additions with a primary source are welcome as issues or pull requests.

**Not legal advice.** DutyKit returns obligations, formats and checks against the cited texts, not advice on individual cases. Made with AI assistance.

## Develop
```bash
uv run --with "mcp>=2" --with pytest pytest -q   # tests
python scripts/katalog_pruefen.py                 # catalogue lint
```

## Run locally
```bash
uv run --with "mcp>=2" --with uvicorn uvicorn app:app --port 8080
```
Self-hosting with Docker and Caddy: see `deploy/`.

## License
Code: MIT (see `LICENSE`). Obligation catalogue `pflichten.json`: CC BY 4.0, please credit "DutyKit (dutykit.dev)".
