# Projektvorgaben

## Aufbau und Quellen

`minecraft-look` enthält die Bedrock-Grafikpakete Lumen WQHD
(Quality und Balanced). Beide Varianten werden gemeinsam versioniert.

- Grafikquellen: `scripts/create_pack.py`, `themes.py`, `water_profiles.py`,
  `night_sky.py`, die festgehaltenen Referenzen unter `reference/` und
  `assets/night_sky/`. `pack/` und `docs/biome-map.json` sind generierte,
  mitzuversionierende Ausgaben. Änderungen an der Quelle vornehmen und neu erzeugen.
- Die Generatoren löschen ihre Ausgabeordner. Vorher `git status` und vorhandene
  Änderungen prüfen. Bei unbekannten direkten Änderungen an Ausgaben zunächst in
  einer vollständigen temporären Kopie vergleichen; ein Git-Export enthält keine
  unversionierten Dateien. Keine Nutzerarbeit durch Regeneration verwerfen.
- `dist/` bleibt Buildausgabe und wird nicht eingecheckt.
  Die Source-ZIPs sammeln Dateien rekursiv: Releasebuilds nur aus einem geprüften,
  sauberen Checkout ohne private Dateien, virtuelle Umgebungen oder lokale Logs.

## Änderungen und Prüfung

- Bestehende Paket- und Modul-UUIDs bei Updates erhalten. Quality und Balanced
  haben absichtlich eigene Identitäten.
- Änderungen an Referenzen benötigen nachvollziehbare Herkunft samt Commit,
  Prüfsummen und Rechtehinweisen. Prüfsummen nicht zur Umgehung eines Fehlers ändern.
- Normaler Build: Python ab 3.10. Keine
  zusätzlichen Pakete oder Downloads erforderlich. FFmpeg gehört ausschließlich
  zur optionalen erneuten Himmelskonvertierung.
- Für Grafikänderungen vom Repo-Root aus:
  `python3 scripts/create_pack.py`,
  `python3 -m unittest discover -s tests -v`, `python3 scripts/build.py`.
- Bei Änderungen an CI, Releasewerkzeugen oder gemeinsamen Vorgaben die
  Testsuite prüfen; Befehle und Freigabegates stehen in `docs/RELEASING.md`.
  Reine Textkorrekturen benötigen keinen erneuten Paketbuild.
- Lokale Validatoren und Mocks führen Minecraft nicht aus. Import, Content-Log,
  Darstellung, Audio und FPS nur mit tatsächlicher Messung als bestanden melden.
  Vorhandene historische Prüfberichte nicht nachträglich als neue Abnahme ausgeben.

## Release und Skills

Versionierung, Tags, Abnahme, Veröffentlichung und Hotfixes richten sich nach
`docs/RELEASING.md`. Änderungen zunächst im jeweiligen `CHANGELOG.md` erfassen.
Neue Arbeitsbranches verwenden `codex/` als Präfix. Externe Aktionen nur im
Umfang des Nutzerauftrags ausführen; eine Releasevorbereitung ist keine
Veröffentlichung. Bereits erteilte Autorisierung gilt weiter.

Projektlokale Skills unter `.agents/skills/`:

- `lumen-pack-development`: Grafikwerte, Stile, Biome und Paketressourcen ändern.
- `lumen-release`: Releasekandidaten prüfen, versionieren und veröffentlichen.

## Code Review Rules

Als Fehler behandeln: ausschließlich generierte Dateien geändert; rotierte
Bestands-UUIDs; inkonsistente Paketversionen; unaufgelöste Ressourcenverweise;
veränderte Vanilla-Komponenten außerhalb des erklärten Grafikumfangs;
unbelegte In-Game- oder Performancebehauptungen; Upload alter oder ungeprüfter
Artefakte; automatische öffentliche Freigabe vor der Abnahme.
