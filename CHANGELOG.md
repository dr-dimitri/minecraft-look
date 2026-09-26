# Änderungen · Lumen WQHD

## [Unreleased]

- Ungültige Balanced-Wellenbudgets (z. B. `octaves = 0`, nicht endliche Werte
  oder zusätzliche optische Parameter) brechen den Build ab, bevor ein neuer
  Artefaktsatz bereitgestellt wird. Alle 40 Wasserdateien bleiben abgedeckt.
- Veröffentlichte Paket- und Modul-UUIDs beider Varianten werden fest geprüft,
  damit versehentliche Identitätswechsel den Updatepfad nicht beschädigen.
- Der optionale Himmelsexport erzeugt und prüft zunächst alle sechs Flächen in
  einem temporären Verzeichnis. FFmpeg-Fehler lassen die bisherigen Dateien
  erhalten; Schreibfehler beim Übernehmen lösen eine Wiederherstellung aus.
  Falls auch diese scheitert, bleiben Originaldateien zur Wiederherstellung
  erhalten. Zusätzliche lokale PNG-Vorschauen gelangen nicht in die strikte
  Prüfsummenliste der Himmelsressourcen.

- Builds erzeugen Ressourcen aus einer temporären Quellkopie neu, auch bei
  unveränderter Version. Lokale generierte Dateien bleiben erhalten und werden
  nicht als Paketquelle verwendet; das Source-ZIP enthält frische Ausgaben.
- Vollständige, geprüfte Artefaktsätze unter `dist/<Version>/<Satz-SHA256>/`;
  `dist/current.json` wird erst nach Erfolg atomar umgeschaltet. Abgebrochene
  Builds mischen keine Dateien mit früheren Ausgaben. Frühere flache Dateien in
  `dist/` bleiben Altbestand; den ausgegebenen Satzpfad verwenden.
- Wiederholungsbuild und eigenständiger Source-ZIP-Neubau mit Hashvergleich als
  lokaler Befehl und verpflichtender CI-Schritt; Linux mit Python 3.10/3.14.7
  und Windows mit Python 3.14.7. Releaseartefakte stammen aus Linux/3.14.7;
  der Releasejob wartet auf alle drei Prüfläufe.
- Feste LF-Zeilenenden für Quellen und generiertes JSON verhindern veränderte
  Referenzprüfsummen durch Windows-Checkouts.
- Verfahren und Szenenvorlage für eine wiederholbare Bedrock-Abnahme mit
  festgehaltener Welt, Kameras, Updatepfad, Aufnahmen, Logs und Messdaten.
  Referenzwelt und tatsächliche Spielabnahme sind weiterhin offen.

## [0.4.1] - Testversion

- Quellarchive enthalten nur ausgewählte Projektdateien; lokale `.env`-Dateien,
  virtuelle Umgebungen, Caches und fremde Verzeichnisse werden ausgeschlossen.
  Symlinks in ausgewählten Quellen führen zu einem Fehler statt Daten mitzupacken.
- Ein direkter Build mit veralteter generierter Paketversion bricht ab.
  Die im Spiel sichtbare Versionsbeschreibung wird aus `VERSION` erzeugt.
- Fehlende Materialdefinitionen, falsche Farbtexturverweise und beschädigte oder
  veränderte Block-Farbtexturen verhindern jetzt einen Paketbuild.
- Die abschließenden Installerprüfungen bleiben auch mit `python -O` aktiv.
- Bugreproduktion, Behebung, Review, Tests, Commit, Push und Release als
  beauftragten Wartungsablauf in `AGENTS.md` festgehalten.
- Eigenständiges Grafikrepository `minecraft-look`; Gameplay-Erweiterungen
  werden separat in `minecraft-addons` gepflegt.
- Projektvorgaben und zwei lokale Skills für Grafikentwicklung und Releases.
- CI für beide Grafikvarianten, Versions-/Tagprüfung und
  Release-Entwürfe vor der manuellen Veröffentlichung.

Automatisch geprüft; Windows-Import, Bildwirkung und Zielhardwaremessungen
bleiben offen. Deshalb Veröffentlichung als Pre-release. Die Grafikabstimmung
und bestehenden Paket-UUIDs bleiben erhalten.

## [0.4.0] - Kandidat, Veröffentlichung nicht nachgewiesen

Bestandsbeschreibung beim Einführen dieses Changelogs, keine nachträgliche
Releasebestätigung: Quality/Balanced, vier Grafikstile, acht Wasserprofile und
Galaxien-Nachthimmel. Siehe README und `docs/VALIDATION.md` für Umfang und Grenzen.
Windows-Import, Bildwirkung und Zielhardwaremessungen sind noch offen.
