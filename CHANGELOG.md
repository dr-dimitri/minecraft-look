# Änderungen · Lumen WQHD

## [Unreleased]

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
