# LinkedIn-Beitrag: Ablauf

Montags. Ein Beitrag pro Woche. Er erscheint donnerstags 09:15 Uhr (Luxemburg) auf dem Profil „René Schröder“. Nie sofort veröffentlichen, nie die Seite „PontoIt“.

1. **Thema wählen:** `themenplan.md` lesen. Vorrang hat eine Gesetzes- oder Katalogänderung der letzten 14 Tage (`KATALOG-AENDERUNGEN.md`), sonst das nächste Thema aus dem Vorrat. Vorher in Postiz die Beiträge der letzten vier Wochen ansehen und fehlende Themen unter „Bereits entworfen“ nachtragen. Kein Thema doppelt.
2. **Belegen:** Die Primärquelle der Kernaussage in diesem Lauf abrufen und jede Aussage am Wortlaut prüfen. Nicht belegbar heißt: nicht schreiben. Keine Quelle erreichbar: anderes Thema. Geht keines: nichts einplanen, im Bericht nennen.
3. **Schreiben:** Skills `schreibstil-rene` (auch `references/belegstellen.md`) und danach `humanize-writing` laden. 120 bis 220 Wörter, Regeln aus `themenplan.md`. Letzte Zeile: „Entstanden mit KI-Unterstützung.“
4. **Ablegen:** Text als `betrieb/linkedin/JJJJ-MM-TT.md` (Kopf: Thema, Quellen mit Abrufdatum, Status). In `themenplan.md` unter „Bereits entworfen“ eine Zeile ergänzen. Geht mit dem Pull Request des Laufs nach `main`.
5. **Einplanen in Postiz:** `https://api.postiz.com/mcp`, POST, Header `Content-Type: application/json` und `Accept: application/json, text/event-stream`, JSON-RPC 2.0, `method: tools/call`. Keinen eigenen Authorization-Kopf senden; der Schlüssel wird von der Umgebung angehängt. Antworten kommen als Zeile `data: {...}`.
   - `integrationList`: Kanal mit `platform` linkedin und Name René Schröder wählen (zuletzt id `cmvjx0rni024klh0yatdinpjg`, gegen die Liste prüfen). Nie `linkedin-page`.
   - `postsListTool` für den Donnerstag: liegt dort schon ein DutyKit-Beitrag, nichts doppelt einplanen.
   - `integrationSchedulePostTool` mit `{socialPost:[{integrationId:<id>, isPremium:false, date:<Donnerstag 08:15:00.000Z im Winter, 07:15:00.000Z im Sommer>, shortLink:false, type:'schedule', postsAndComments:[{content:<jeder Absatz in <p>…</p>>, attachments:[]}], settings:[{key:'post_as_images_carousel', value:false}]}]}`. Nie `type: 'now'`.
   - Erfolg: Antwort mit `output[0].postId`. Bei Fehler bis zu zweimal neu versuchen, vorher mit `postsListTool` auf Doppelte prüfen.
   - Danach prüfen: genau ein Beitrag, Zustand QUEUE, richtiger Kanal, richtige Zeit.
6. **Berichten:** Thema und Vorschau-Link in den Wochenbericht. Keine eigene Nachricht.

Grenzen: In Postiz nur dieser eine Beitrag. Keine anderen Beiträge ändern oder löschen, außer einem doppelten eigenen derselben Woche.
