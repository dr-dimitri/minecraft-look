---
name: lumen-pack-development
description: Grafikpakete von Lumen WQHD ändern und prüfen, insbesondere Licht, Wasser, Biome, Stile, Cubemap und Quality/Balanced.
---

# Lumen-Grafikpakete bearbeiten

Vom Repository-Root arbeiten und `AGENTS.md` lesen. Quellen sind
`scripts/create_pack.py`, `scripts/themes.py`, `scripts/water_profiles.py`,
`scripts/night_sky.py`, `assets/night_sky/` und `reference/`.
`pack/` und `docs/biome-map.json` werden vollständig neu erzeugt.

## Änderung umsetzen

1. Vor einer Regeneration vorhandene Änderungen im Arbeitsbaum prüfen. Der
   Generator löscht `pack/`. Bei unbekannten direkten Änderungen an Ausgaben
   zunächst eine vollständige temporäre Kopie einschließlich unversionierter
   Quelldateien vergleichen; nicht blind neu erzeugen.
2. Die passende Quelle ändern. Wasseroptik und Wellenbudget sind getrennt:
   Quality/Balanced unterscheiden sich derzeit nur durch `octaves` und
   `sampleWidth`. Stilwechsel müssen ursprüngliche Biom-/Laubwerte wiederherstellen.
3. Nur für den betroffenen Bereich weiterlesen: `docs/REALISM.md` für Wasser,
   Licht und Materialien; `docs/NIGHT_SKY.md` für Cubemap/Nachtkurven;
   `reference/source.json` und `NOTICE.md` bei Änderungen an Fremdressourcen.
   Bestehende Vanilla-Komponenten außerhalb des erklärten Umfangs erhalten.
4. Gegen den Fehler oder das neue Verhalten einen sinnvollen Regressionstest
   hinzufügen, wenn die Änderung ausführbares Verhalten betrifft. Quellen und
   generierte Ausgaben gemeinsam prüfen.

## Nachweis

```sh
python3 scripts/create_pack.py
python3 -m unittest discover -s tests -v
python3 scripts/build.py
```

Beide Installer und die betroffenen Stil-Overlays betrachten. Nicht nur die
Basisdateien prüfen. Python genügt; FFmpeg ist nur bei einer ausdrücklich
erforderlichen erneuten Panoramakonvertierung nötig.

Produktänderung im Root-`CHANGELOG.md` unter `Unreleased` erfassen. Keine
Versionsanhebung pro Entwicklungsänderung erzwingen. Bei Releasevorbereitung
`docs/RELEASING.md` verwenden: `VERSION`, sichtbare Manifestbeschreibung und
Anleitung synchron halten, alle Quality-/Balanced-UUIDs erhalten.

Im Ergebnis die Änderung, ausgeführten Prüfungen und offene Sichttests nennen.
Lichtwerte, Vorschauen und Python-Tests belegen weder Engine-Kompatibilität noch
Bildruhe oder FPS; dafür `docs/VALIDATION.md` und `docs/BENCHMARK.md` verwenden.
