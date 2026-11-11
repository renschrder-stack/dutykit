---
name: sicherheitscheck
description: Fuehrt den Sicherheitscheck fuer ein Projekt aus (Geheimnisse in Dateien und Git-Historie, Skills, Grundpruefung) und fasst den Bericht auf Deutsch zusammen. Verwenden, wenn der Nutzer "Sicherheitscheck", "Security-Check" oder "pruef das Projekt auf Sicherheit" sagt.
---

# Sicherheitscheck

Ablauf, wenn der Nutzer "Sicherheitscheck" sagt:

1. Projektordner bestimmen: der aktuelle Arbeitsordner, sofern der Nutzer keinen anderen nennt.
2. Ausfuehren: `sicherheitscheck "<Projektordner>"` (einmalig installiert mit `pip install -e <Pfad zu diesem Repo>`). Ohne Installation: `python -m sicherheitscheck "<Projektordner>"` mit `PYTHONPATH=<Repo>/src`.
3. Den Bericht (`bericht.md`, Pfad steht in der Ausgabe) lesen. Rueckgabecodes: 0 alles geprueft ohne Funde, 1 Funde, 2 Bedienfehler, 3 keine Funde, aber Stufen liefen nicht.
4. Antwort kurz und auf Deutsch:
   - Gesamturteil in einem Satz.
   - Stufen, die NICHT liefen, ausdruecklich nennen. "Keine Funde" bei uebersprungenen Stufen ist kein Freispruch.
   - Funde nach Schwere, je Fund Ort und was zu tun ist.
5. Gefundene Geheimnisse sind schon in Berichten geschwaerzt. Niemals versuchen, den Klartext herauszuholen oder auszugeben. Gefundene Schluessel gelten als kompromittiert: beim Aussteller widerrufen, nicht nur aus dem Code loeschen (die Git-Historie behaelt sie).
6. Nichts im Projekt aendern, solange der Nutzer das nicht ausdruecklich verlangt.

Zusaetzlich zum Werkzeug darfst du den Code selbst auf typische Schwachstellen durchsehen (Eingabepruefung, Zugriffskontrolle, unsichere Abhaengigkeiten). Trenne im Bericht klar: "Werkzeug hat gefunden" und "meine eigene Durchsicht".

Optional: `--verifizieren` laesst TruffleHog gefundene Schluessel bei den Diensten auf Aktivitaet pruefen und sendet sie dorthin. Nur nach ausdruecklicher Zustimmung des Nutzers verwenden.
