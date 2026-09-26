# Änderungen · Lumen WQHD

## [Unreleased]

## [0.5.0] - Testversion

- Bestätigte Helligkeit aus 0.4.3 durch eine unabhängige Referenzdatei und
  Build-/CI-Prüfungen gegen unbeabsichtigte Änderungen geschützt. Die
  Projektvorgaben untersagen ein automatisches Nachziehen dieser Referenz.
- Flache, weichere Wasserwellen mit leichter Bewegung in allen acht Profilen,
  vier Stilen und beiden Qualitätsstufen. Die Wellenbudgets bleiben erhalten.
- Auf Wunsch leicht dunkleres Wasser: CDOM und Chlorophyll um 10 % erhöht,
  Sediment und Caustics unverändert. Die angenommene Abdunklung ist eine vom
  Nutzer akzeptierte Näherung, keine gemessene Verringerung der Bildhelligkeit.
- Halloween erhält langsam ziehende, weich ein-/ausblendende Nebelschwaden.
  Rein lokale, beleuchtete Partikel in den 78 vollständig gestalteten
  Overworld-Biomen; keine Emission unter Wasser, im Inventar, beim Schlafen,
  als Zuschauer oder durch entfernte Spieler. Die ursprüngliche
  Spieler-Grafikdefinition bleibt bis auf den Nebel-Auslöser erhalten.
- Dezente Blattbewegung als viersekündige Texturanimation mit höchstens einem
  Pixel Versatz. 28 transparente/undurchsichtige Blatttexturen einschließlich
  der Pappeln, 40 aktuelle/ältere Atlaszuordnungen; Originalfarben und
  Pixelanzahlen jeder Transparenzstufe bleiben pro Bild erhalten.
- Neue Mojang-Referenzen mit Commit und SHA-256 festgehalten; portabler
  PNG-/TGA-Import ohne zusätzliche Bibliotheken. Beide Installer und der
  Neubau aus dem Quellarchiv enthalten die neuen Ressourcen.

Die Helligkeit aus 0.4.3 wurde vom Nutzer bestätigt. Die neuen Bewegungen,
Nebelpartikel, Wasserabdunklung, der Update-Import und FPS bleiben im Spiel
zu prüfen. Blattbewegung verändert die Textur, nicht die Baumgeometrie.

## [0.4.3] - Testversion

- Helligkeit an Mojangs festgehaltenes Standardprofil angepasst: Sonnenkurve
  mit Maximum 100 statt 110.000, originale Mondkurve und Generic-Tonemapping.
  Der pauschale Gain-Eingriff aus 0.4.2 entfällt zugunsten der originalen
  Farbkorrekturwerte. Alle Stile und beide Varianten übernehmen die Grundlage;
  Stil-Gain und Mondlicht übersteigen die Standardwerte nicht.
- Die verwendeten Licht- und Farbprofilreferenzen sind mit Herkunft, Commit,
  SHA-256 und Rechtehinweisen festgehalten. Prüfungen sichern die vollständigen
  Kurven und verhindern eine erneute Anhebung auf 110.000.

Die bisherige Gain-Absenkung in 0.4.2 reichte laut Nutzerrückmeldung nicht aus.
Die neue Grundlage stammt aus den tatsächlichen Mojang-Paketdateien; die
Bildwirkung und der Update-Import von 0.4.2 bleiben im Spiel zu prüfen.

## [0.4.2] - Testversion

- Überhelle Darstellung: gemeinsamer Farbkorrektur-Gain von 1,0 auf 0,65
  reduziert und Zusatzkontrast im natürlichen Stil entfernt. Alle vier Stile
  übernehmen die Helligkeitskorrektur in Quality und Balanced; ihre Farbtönung
  bleibt erhalten. Die tatsächliche Bildhelligkeit bleibt im Spiel zu prüfen.
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
- Abgeschlossene Arbeitsbranches nach Review und grüner CI in den Standardbranch
  mergen und anschließend lokal sowie auf dem Remote löschen.

Windows-Import, Update von 0.4.1, tatsächliche Helligkeit aller Stile und
Leistungsmessungen bleiben offen. Deshalb Veröffentlichung als Pre-release;
Paket-UUIDs und technische Mindestversion bleiben erhalten.

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
