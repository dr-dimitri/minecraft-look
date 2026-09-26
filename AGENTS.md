# Projektvorgaben

## Aufbau und Quellen

`minecraft-look` enthält die Bedrock-Grafikpakete Lumen WQHD
(Quality und Balanced). Beide Varianten werden gemeinsam versioniert.

- Grafikquellen: `scripts/create_pack.py`, `themes.py`, `water_profiles.py`,
  `night_sky.py`, `halloween_fog.py`, `leaf_motion.py`, die festgehaltenen Referenzen unter `reference/` und
  `assets/night_sky/`. `pack/` und `docs/biome-map.json` sind generierte,
  mitzuversionierende Ausgaben. Änderungen an der Quelle vornehmen und neu erzeugen.
- Die Generatoren löschen ihre Ausgabeordner. Vorher `git status` und vorhandene
  Änderungen prüfen. Bei unbekannten direkten Änderungen an Ausgaben zunächst in
  einer vollständigen temporären Kopie vergleichen; ein Git-Export enthält keine
  unversionierten Dateien. Keine Nutzerarbeit durch Regeneration verwerfen.
- `dist/` bleibt Buildausgabe und wird nicht eingecheckt.
  `build.py` regeneriert und validiert eine temporäre Quellkopie. Lokale
  `pack/`-Dateien und die Biomkarte bleiben unberührt und werden nicht als
  Paketquelle übernommen. Für Git weiterhin bewusst `create_pack.py` ausführen.
  Nur vollständige Sätze unter `dist/<Version>/<Satz-SHA256>/` verwenden;
  `dist/current.json` zeigt auf den zuletzt erfolgreichen Satz. Keine flachen
  Altdateien oder pauschalen `dist/*`-Globs veröffentlichen.
  `scripts/source_archive.py` begrenzt Source-ZIPs auf Projektverzeichnisse und
  unterstützte Dateitypen. Neue Quelltypen dort samt Test ergänzen.
  Releasebuilds nur aus einem geprüften,
  sauberen Checkout ohne private Dateien, virtuelle Umgebungen oder lokale Logs.

## Änderungen und Prüfung

- Bestehende Paket- und Modul-UUIDs bei Updates erhalten. Quality und Balanced
  haben absichtlich eigene Identitäten.
- Die am 26.09.2026 vom Nutzer bestätigte Helligkeit aus 0.4.3 ist festgeschrieben
  in `reference/approved_brightness.json`. Licht, Farbkorrektur, Atmosphäre,
  Cubemap, lokale Lichtquellen, Materialien und Biomzuordnungen nicht nebenbei
  verändern. Der Validator prüft diesen Stand in Basis und allen Stilen.
  Wasserbewegung darf unabhängig davon angepasst werden. Die danach ausdrücklich
  gewünschte Wasserabdunklung ist als eigene Ausnahme mit Herkunft vermerkt.
  Baseline niemals automatisch neu erzeugen oder zur Reparatur eines roten Tests
  nachziehen; Änderungen benötigen einen ausdrücklichen Nutzerauftrag und Review.
  Neue Effekte dürfen diese Schutzprüfung nicht abschalten.
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

Nach Fertigstellung einer beauftragten Änderung den Arbeitsbranch nach
erfolgreichem Review und grüner CI in den Standardbranch mergen. Anschließend
den vollständig gemergten Arbeitsbranch lokal und auf dem Remote löschen.
Commit, Push, Merge und diese Branchbereinigung gehören zum Abschluss der
Änderung; ein reiner Prüfauftrag bleibt ohne solche Änderungen. Standardbranch,
ungemergte Arbeit und Branches anderer laufender Aufgaben nicht löschen.

## Ablauf einer beauftragten Bugfix- und Releaserunde

1. Praxisrelevante Fehler anhand konkreter Auslöser suchen und reproduzieren;
   belegte Befunde von Vermutungen oder offenen Sichtprüfungen trennen.
2. Die Ursachen in den Quellen beheben und passende Regressionstests ergänzen.
   Version, generierte Ausgaben, Anleitung und Changelog konsistent aktualisieren.
3. Danach einen getrennten Reviewdurchgang über den vollständigen Diff machen:
   Nutzerverhalten, Regressionen, Paket-/Updatepfad, Dateiauswahl und CI prüfen.
   Befunde beheben und betroffene Prüfungen wiederholen. Selbstreview ausdrücklich
   als solchen benennen, wenn kein unabhängiger Reviewer beteiligt war.
4. Tests, vollständigen Build, Wiederholungsbuild und Wiederaufbau aus dem
   Quellarchiv ausführen (`python3 scripts/verify_build.py`). Alle drei Archive
   müssen innerhalb derselben Python-/zlib-Umgebung bytegleich sein. Die CI
   prüft Linux mit minimaler und fester Release-Python-Version sowie Windows;
   ein Release benötigt alle Prüfläufe. Ergebnisse und Grenzen dokumentieren.
   Für die reale Abnahme `docs/TEST_WORLD.md` und die Szenenvorlage verwenden:
   exportierte Welt samt SHA-256, Kameras/Routen und Belege aller Varianten/Stile
   festhalten. Eine vorbereitete Vorlage ist keine erstellte oder geprüfte Welt.
5. Die zusammengehörigen Änderungen committen und pushen; anschließend die CI
   des exakten Commits abwarten und Fehler beheben. Den geprüften Arbeitsbranch
   in den Standardbranch mergen und danach lokal sowie auf dem Remote löschen.
   Vor einem Release zusätzlich die CI des endgültigen Commits im Standardbranch
   abwarten.
6. Bei beauftragtem Release den geprüften Commit im Standardbranch taggen, CI-Artefakte übernehmen,
   Releasehinweise ergänzen und veröffentlichen. Ohne tatsächliche Bedrock-Abnahme
   nur als ausdrücklich gekennzeichnete Testversion/Pre-release veröffentlichen;
   keine stabile Engine- oder Leistungsfreigabe behaupten. Danach die
   veröffentlichten Dateien herunterladen und ihre SHA-256-Werte kontrollieren.

Der Auftrag für diese gesamte Runde autorisiert Commit, Push und Release;
keine erneute Bestätigung für bereits beauftragte Schritte verlangen. Ein
reiner Prüf- oder Änderungsauftrag löst keine Veröffentlichung aus.

Projektlokale Skills unter `.agents/skills/`:

- `lumen-pack-development`: Grafikwerte, Stile, Biome und Paketressourcen ändern.
- `lumen-release`: Releasekandidaten prüfen, versionieren und veröffentlichen.

## Code Review Rules

Als Fehler behandeln: ausschließlich generierte Dateien geändert; rotierte
Bestands-UUIDs; inkonsistente Paketversionen; unaufgelöste Ressourcenverweise;
veränderte Vanilla-Komponenten außerhalb des erklärten Grafikumfangs;
unbelegte In-Game- oder Performancebehauptungen; Upload alter oder ungeprüfter
Artefakte; automatische öffentliche Freigabe vor der Abnahme.
