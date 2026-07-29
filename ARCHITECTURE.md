# digsigclt
Stand: 2026-07-29, geprüft gegen Commit f70c2fb

## Zweck
„Digital Signage Client" — läuft auf den Signage-Systemen (Windows und Linux)
und (1) empfängt/aktualisiert die anzuzeigenden Signage-Daten, (2) führt
Wartungs-RPC-Kommandos aus (Beep, Reboot …) und (3) liefert Systeminformationen
auf Anfrage. Der Python-Vorgänger des Rust-Programms `digsigctl`.

## Stack & Einstiegspunkte
Python 3 (portabel Windows/Linux). Package `digsigclt` mit Subpackages `os`,
`os.posix`, `request_handler`, `rpc`. Kernmodule: `server.py` (HTTP-Server),
`sync.py` (Datenabgleich), `network.py`, `lock.py`, `common.py`, `cli.py`.
Console-Script: `digsigclt = digsigclt.cli:main`. Dependency: `netifaces`.

## Schnittstellen
### Konsumiert
- Lokales Dateisystem (Signage-Daten), Betriebssystem (Reboot/Beep über
  `os`/`os.posix`). Netzwerk-Interfaces via `netifaces`.

### Bietet an
- **HTTP-Server** auf dem Gerät mit Request-Handlern für Daten-Sync und
  RPC-Kommandos (Beep, Reboot, Systeminfo) — angesprochen von der zentralen
  Verwaltung (`termgr`/`hwdb.ctrl`).

## Deployment / Laufzeit
Läuft als Dienst/Prozess auf jedem Signage-System. ⚠️ ANNAHME: als
System-Service eingerichtet (Windows-Dienst bzw. systemd unter Linux). Wird
zunehmend durch das Rust-Programm `digsigctl` abgelöst.

## Ersetzbarkeit
Kopplungsgrad: **mittel**. Das RPC-/Sync-Protokoll ist mit der zentralen
Steuerung (`hwdb.ctrl`, `termgr`) verzahnt; Ablösung ist real im Gange (Rust-
`digsigctl`). Ein Ersatz muss dasselbe HTTP-/RPC-Protokoll bedienen.

## Weitere Doku
- `README.md` (Zweck, Plattform-Hinweis Windows/Linux).
- Nachfolger: https://github.com/homeinfogmbh/digsigctl
- ⚠️ ANNAHME: Zentrales Repo `homeinfo-architektur` (Ordner `komponenten/`) noch
  nicht geprüft.
