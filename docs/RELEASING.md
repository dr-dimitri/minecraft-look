# Entwicklung und Release · minecraft-look

Der Ablauf lautet: Änderung → Review und CI → versionierter Kandidat →
Release-Entwurf → Prüfung in Minecraft → bewusste Veröffentlichung. Ein grüner
Build ist eine technische Paketprüfung und ersetzt die Prüfung im Spiel nicht.

## Grafikvarianten und Versionen

| Produkt | Versionsquelle | Zusätzliche Versionsstellen | Tag | Artefakte |
|---|---|---|---|---|
| Lumen WQHD | `scripts/create_pack.py`: `VERSION` | Manifestbeschreibung, README, CHANGELOG | `vX.Y.Z` | Quality-/Balanced-`.mcpack`, Source-ZIP, `SHA256SUMS.txt` |

Manifest und Modul werden aus der Versionsquelle erzeugt. Quality und Balanced
erscheinen gemeinsam in derselben Version. `format_version` und
`min_engine_version` sind davon unabhängige Kompatibilitätsangaben.

Projektkonvention: `X.Y.Z` mit drei nichtnegativen Ganzzahlen ohne führende
Nullen. Patch für kompatible Fehlerkorrekturen, Minor für neue Funktionen und
Stile, Major für inkompatible Änderungen. Auch vor 1.0 inkompatible Änderungen
ausdrücklich dokumentieren und mindestens Minor erhöhen. Neue Mindestversionen
und Welt-/Installationsmigrationen in den Releasehinweisen nennen. Eine bereits
veröffentlichte Version wird nicht erneut verwendet. UUIDs bleiben bei Updates
erhalten; neue Identitäten bedeuten ein neues, bewusst separat installierbares Paket.

Für Testkandidaten dient der Release-Entwurf. Eine öffentliche Testversion erhält
zusätzlich GitHubs Pre-release-Markierung und klare Einschränkungen; die
Bedrock-Version und der Tag bleiben `X.Y.Z` bzw. produktbezogenes `vX.Y.Z`.
Keine erfundenen `-rc`-Werte in den ganzzahligen Bedrock-Versionsarrays.

## Änderungen vorbereiten

1. Arbeitsbaum prüfen. Fremde Änderungen bewahren. Änderungen in einem passenden
   Arbeitsbranch entwickeln; bei neuen Agent-Branches `codex/` verwenden.
2. Quellen bearbeiten, erforderliche Regressionstests ergänzen und betroffene
   Pakete regenerieren. Ausgabeverzeichnisse nicht als alleinige Quelle behandeln.
3. Nutzerrelevante Änderungen im `Unreleased`-Abschnitt des Produkt-Changelogs
   dokumentieren. Erst beim Zusammenstellen des Kandidaten die Version erhöhen
   und Änderungen in `## [X.Y.Z] - Kandidat` verschieben. Keine Versionsanhebung
   für jeden einzelnen Entwicklungscommit erzwingen.
4. Anleitung, Kompatibilität und bekannte Grenzen abgleichen. Alte Prüfberichte
   bleiben historische Belege; neue Ergebnisse erhalten einen eigenen Beleg.
5. Quellen, generierte Dateien, Tests und Dokumentation gemeinsam reviewen und
   committen. Releasequellen müssen vollständig in Git vorliegen. `dist/` gehört
   nicht in Git. Vor einem Tag muss `git status --porcelain` leer sein.
6. Nach erfolgreichem Review und grüner CI des exakten Arbeitsbranch-Commits in
   den Standardbranch mergen. Anschließend den vollständig gemergten Arbeitsbranch
   lokal und auf dem Remote löschen; laufende oder ungemergte Arbeit erhalten.
   Den lokalen Standardbranch aktualisieren. Ein Release wird erst nach grüner
   CI des endgültigen Commits im Standardbranch getaggt.

## Lokale automatische Gates

Alle Befehle laufen vom Repository-Root mit Python ab 3.10.
Es sind keine zusätzlichen Bibliotheken oder weiteren Checkouts nötig.

**Achtung:** `scripts/create_pack.py` löscht den Ausgabeordner `pack/`. Bei unbekannten oder unversionierten Änderungen
eine vollständige temporäre Kopie einschließlich dieser Dateien verwenden.
Die vorhandenen `dist/`-Ordner und lokale Umgebungen dabei auslassen. Erst nach
dem Vergleich neue Ausgaben gezielt übernehmen.

```sh
python3 scripts/create_pack.py
python3 scripts/check_release.py
python3 -m unittest discover -s tests -v
python3 -O -m unittest discover -s tests -p test_build_guards.py -v
python3 scripts/verify_build.py
git status --porcelain --untracked-files=all -- pack docs/biome-map.json
```

Die letzte Ausgabe muss bei einem eingecheckten Kandidaten leer sein. Für eine
noch nicht eingecheckte Änderung die erwarteten Diffs prüfen und gemeinsam mit
den Quellen committen. Die CI verlangt einen unveränderten Checkout und erkennt
auch neu erzeugte, nicht versionierte Dateien.

`build.py` erzeugt und validiert Ressourcen in einer temporären Kopie der
kuratierten Quellen. Lokale `pack/`-Dateien und die lokale Biomkarte werden
weder überschrieben noch als Eingabe verwendet. Im Source-ZIP liegen die frisch
erzeugten Ausgaben. `create_pack.py` bleibt für die in Git gepflegten Ausgaben
zuständig; deshalb bleibt auch die Driftprüfung verpflichtend.

`verify_build.py` führt zwei vollständige Builds sowie einen eigenständigen
Build aus dem entpackten Source-ZIP durch. Alle drei Archive und die Prüfsummen
müssen innerhalb derselben Python-/zlib-Umgebung bytegleich sein. Das Skript
protokolliert beide Runtime-Versionen und läuft auch in jedem CI-Prüfjob.

Ein erfolgreicher Build gibt den vollständigen Satzpfad unter
`dist/<Version>/<SHA256-der-Prüfsummendatei>/` aus. `dist/current.json` wird erst
nach Prüfung aller Archive atomar auf diesen Satz umgeschaltet. Leser müssen
diesen Verweis einmal auflösen und danach denselben Satz verwenden, nicht den
Verweis zwischen einzelnen Dateien erneut lesen. `artifacts.current_bundle()`
löst ihn auf und prüft Vollständigkeit und Hashes. Frühere Sätze bleiben
unverändert. Ein Abbruch beim Umschalten kann einen unreferenzierten vollständigen
Satz hinterlassen; der vorherige Verweis bleibt gültig. Eine Garantie bei
Stromausfall wird nicht behauptet.

Vor einem Kandidaten zusätzlich:

- Den ausgegebenen Satzpfad verwenden, keine fremden Altversionen aus `dist/*`
  veröffentlichen. Flache Ausgaben älterer Buildskripte werden nicht aktualisiert.
- Root-Manifest, Versionen, UUIDs und Artefaktauswahl im Review prüfen.
  `scripts/source_archive.py` erlaubt nur deklarierte Projektverzeichnisse und
  Dateitypen. Lokale Umgebungen, versteckte Zusatzdateien, Logs und Caches werden
  ausgeschlossen; Symlinks und Lesefehler in ausgewählten Quellen brechen ab.
  Neue benötigte Verzeichnisse/Dateitypen samt Regressionstest ergänzen. Der
  Filter ersetzt keine Inhaltsprüfung bewusst gepflegter Quellen.

## CI und Release-Entwurf

`.github/workflows/build.yml` prüft bei Push und Pull Request Versionen und
generierte Ausgaben auf Ubuntu 24.04 mit Python 3.10 und 3.14.7 sowie Windows
2022 mit Python 3.14.7. Jeder Job prüft beide Installer, den Wiederholungsbuild
und den Source-ZIP-Neubau. Nur der feste Linux-/Python-3.14.7-Job lädt den
exakten geprüften Satz als CI-Artefakt hoch. Der Releasejob wartet auf den Erfolg
aller drei Jobs. Windows-CI prüft Python und Dateiverarbeitung, nicht Minecraft. Auf einem Release-Tag kommt die strikte Tag-/Changelogprüfung
hinzu. Erfolgreiche Tags erzeugen einen **Entwurf**, keine öffentliche Freigabe.
Die Pakete werden aus dem geprüften CI-Lauf übernommen und nicht im Releasejob
neu gebaut. Prüfsummen werden mitgeliefert und vor dem Entwurf geprüft.

Beispiel für die lokale Tagprüfung (Version an den Kandidaten anpassen):

```sh
python3 scripts/check_release.py --tag v0.4.2
```

Vor dem Tag das Review und die grüne CI des vorgesehenen Commits prüfen. Ein
autorisierter Releaseauftrag umfasst das Erstellen/Pushen des zugehörigen
annotierten Tags und die Erstellung des Entwurfs. Ein bloßer Auftrag zur
Vorbereitung endet lokal, sofern Tag-Push oder ein entfernter Entwurf nicht
ebenfalls beauftragt sind. Bestehende Tags, Releases
und Dateien vor Mutationen prüfen; bekannte Autorisierung nicht erneut erfragen.

Nach Tag-Push den Workflowlauf und Entwurf prüfen. Ein fehlgeschlagener oder
teilweise ausgeführter Upload bleibt ein Entwurf. Bei erneutem Lauf vorhandene
Dateien und Prüfsummen abgleichen, nur fehlende identische Kandidatenartefakte
ergänzen. Keine Tags verschieben und kein `--clobber` zur Fehlerbehebung nutzen.
Der Workflow überschreibt vorhandene Releases nicht und kann dann gezielt eine
manuelle Wiederaufnahme erfordern.

## Prüfung im Spiel und Freigabe

Den Entwurf auf Windows mit der vorgesehenen Bedrock-Version prüfen. Vorlage:
[`releases/TEMPLATE.md`](releases/TEMPLATE.md). Der Beleg bindet Ergebnisse an
Quellcommit, Dateinamen und SHA-256 der **tatsächlich getesteten** CI-Artefakte.
Belege als Releaseanhang/-text oder späteren Dokumentationscommit speichern;
den Kandidatentag zum Ergänzen eines Belegs nicht verschieben oder neu bauen.

- Referenzwelt und Szenen gemäß [TEST_WORLD.md](TEST_WORLD.md) festhalten;
  Weltdatei samt SHA-256 und ausgefüllte Szenenvorlage am Beleg referenzieren.
- WQHD: [VALIDATION.md](VALIDATION.md), [BENCHMARK.md](BENCHMARK.md) und
  [NIGHT_SKY.md](NIGHT_SKY.md) verwenden. Quality/Balanced jeweils einzeln,
  alle vier Stile und Rückwechsel, Wasser/Biomwechsel, Tag/Nacht/Wetter,
  Cubemap-Nähte und Ressourcen-Neuladen prüfen.
- Bestehende Welt vor einem Update sichern und das Update von der letzten
  veröffentlichten Version prüfen; beim Erst-Release ist dieser Punkt nicht anwendbar.
- Für eine stabile Freigabe dürfen keine offenen Import-, Script- oder
  Darstellungsblocker bleiben. Behauptungen zur Zielhardware oder FPS benötigen
  Messdaten. Offene Engineprüfungen schließen eine stabile Freigabe aus; eine
  ausdrücklich gewünschte öffentliche Testversion benennt sie sichtbar.

Vor der öffentlichen Freigabe Releasehinweise aus dem Produkt-Changelog,
Kompatibilität, Installation/Update, Prüfumfang und bekannte Grenzen ergänzen.
Nur die geprüften Dateien veröffentlichen. Danach Release herunterladen und
Prüfsummen sowie sichtbare Version/Tag/Status kontrollieren. Automatische Tests
erzwingen die technische Seite; Review, Tagberechtigung und reale Abnahme
benötigen zusätzlich den eingehaltenen Prozess bzw. Repository-Einstellungen.

## Fehler nach einem Release

Bei einer fehlerhaften Veröffentlichung Nutzungshinweise und bekannte Probleme
am Release ergänzen. Reparatur als neue Patchversion vom betroffenen Stand
erstellen, alle relevanten Gates einschließlich Updatepfad erneut durchlaufen.
Veröffentlichte Tags und Binärdateien nicht stillschweigend ersetzen. Ein
Git-Revert ist kein sicheres Downgrade einer bereits aktualisierten Bedrock-Welt;
Wiederherstellung aus einer Sicherung oder eine vorwärts gerichtete Korrektur
mit höherer Version vorsehen.

## Einmalige Repository-Einrichtung

Diese Dateien konfigurieren keine entfernten GitHub-Einstellungen. Nach dem
ersten erfolgreichen CI-Lauf Review vor Merge und den Prüfjob als erforderlichen
Statuscheck im Standardbranch hinterlegen; Force-Push/Branchlöschung begrenzen.
Tag-Erstellung und Änderungen an `v*` auf die Releaseverantwortlichen
beschränken. Die tatsächliche Verfügbarkeit und Einrichtung der Regeln im
Repository prüfen; nicht allein aufgrund dieser Dokumentation als aktiv melden.

## Projektlokale Skills

`AGENTS.md` enthält die dauerhaften Vorgaben; `.agents/skills/` enthält die
aufgabenspezifischen Abläufe. Beispiele: `$lumen-pack-development`,
`$lumen-release`. Die Ablage folgt der offiziellen
[Skill-Dokumentation](https://learn.chatgpt.com/docs/build-skills) und den
[Projektanweisungen](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
Die Entwurfserstellung nutzt die dokumentierten Optionen von
[`gh release create`](https://cli.github.com/manual/gh_release_create).
