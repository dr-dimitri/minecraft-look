# Realismus-Abstimmung · 0.3.0

Ziel ist ein glaubwürdiger natürlicher Look innerhalb von Bedrock Vibrant Visuals, mit Schwerpunkt Wasser. „Natürlich“ ist die neutrale Variante; die drei Themenstile bleiben bewusst künstlerisch gefärbt. Es gab keinen Zugriff auf den Windows-Renderer. Die folgenden Entscheidungen sind anhand der dokumentierten Parameter begründet, aber noch nicht durch Vergleichsbilder oder GPU-Messungen bestätigt.

## Wasser

Die Einstellungen stehen zentral in `scripts/water_profiles.py`. Die Werte für CDOM, Chlorophyll und Sediment sind selbst gewählte Abstimmungen in den von Bedrock vorgegebenen Einheiten, keine Messungen oder wissenschaftlich kalibrierten Gewässermodelle.

| Profil | Typische Zuordnung | Oberflächencharakter | Zusammensetzung |
|---|---|---|---|
| See | Gemäßigte Landbiome | Kleine, ruhige Wellen | Geringe Konzentrationen |
| Klarer See | Kalte Landbiome, gefrorener Fluss | Sehr flache Kräuselung | Besonders geringe Konzentrationen |
| Fluss | Flussbiom | Feinere, schnellere Bewegung | Mehr gelöste organische Stoffe und Sediment |
| Küste | Strand, steiniger Strand, Pilzinsel-Ufer | Mittlere Wellen | Etwas mehr Sediment als offenes Meer |
| Meer | Normales, tiefes und lauwarmes Meer | Größere Wellen mit feinen Anteilen | Geringe Konzentrationen |
| Kaltes Meer | Kalte/gefrorene Meere, kalter Strand | Etwas ruhigere Meereswellen | Geringe Konzentrationen |
| Tropisch | Warmes und tiefes warmes Meer | Mäßige Wellen | Sehr wenig gelöste Stoffe |
| Sumpf | Sumpf und Mangroven | Fast ruhige Oberfläche | Mehr CDOM, Chlorophyll und Sediment |

Absorption und Streuung berechnet die Engine. `biome_water_color_contribution` ist null, damit sich die klassische blaue Biomfarbe nicht zusätzlich wie Farbstoff über das Ergebnis legt. Die Themen verändern weder Wasserzusammensetzung noch Wellen. Ihre Farben wirken über die Beleuchtung und das fertige Bild.

Die Wellen enthalten mehrere Frequenzen und Bewegungsraten. Pro Ebene dreht die Richtung um etwa 137,51 Grad; dadurch wiederholen sich die Richtungen nicht bereits nach fünf Ebenen wie zuvor. Wellenhöhe, Grundfrequenz, Geschwindigkeit und Schärfe unterscheiden sich je Gewässer. Quality verwendet 16 Ebenen mit `sampleWidth=0.055`, Balanced 8 mit `sampleWidth=0.11`. Mehr Ebenen erhöhen den möglichen Detailgrad, garantieren aber weder bessere Bildwirkung noch eine bestimmte Bildrate. Feine Details müssen in Bewegung auf Flimmern geprüft werden.

Für Caustics wird die eingebaute Animation mit 64 Bildern verwendet: 0,09 Sekunden pro Bild, Stärke 1, Skalierung 0,5. Das sind dezente Ausgangswerte; ein gleichzeitiger Vergleich bei Sonnenlicht ist nötig. Alle Biome verwenden dieselben Caustics, weil Bedrock diese Parameter nicht weich überblenden kann.

Die Zuordnung ist biombasiert. Ein künstliches Schwimmbecken im Ozeanbiom erhält dessen Wellenprofil, ein Bergsee keine automatisch erkannte Tiefe. Flusswellen folgen keiner ausgelesenen Fließrichtung. Brechung, Sichttiefe und winkelabhängige Reflexion bleiben Aufgabe der Engine. Es wurden keine erfundenen Optionen für Reflexionsauflösung, Brechungsindex, Brandung, Schaum oder Strömung hinzugefügt.

## Licht und Materialien

Die Sonne verwendet jetzt bis 110.000 Lux statt 115. Die alte Größenordnung passte nicht zur dokumentierten Einheit und reduzierte den Helligkeitsunterschied zu lokalen Lichtquellen stark. Die Kurve fällt über Abendlicht und Dämmerung bis auf null ab und schließt am Tageswechsel ohne Sprung. Der natürliche Mond erreicht 0,27 Lux; 0,02 Lux Umgebungslicht bleiben als niedriger Mindestwert erhalten. Diese Werte orientieren sich an der dokumentierten Pipeline und sind keine vollständige astronomische Simulation.

ACES ist in allen Stilen derselbe Tonemapping-Operator. Neutrale Sättigung, geringe zusätzliche Kontrastanhebung und weniger blaues Mondlicht sollen Überfärbung reduzieren. Der höhere Sonnenwert verlangt einen Sichttest der automatischen Belichtung, besonders beim Wechsel von Höhle zu Tageslicht. Nächte sollen dunkel bleiben, ohne Hindernisse unlesbar zu machen; das lässt sich mit Zahlenprüfungen allein nicht bestätigen.

Die drei Metallblöcke erhalten binäre Metalligkeit 255 und unterschiedliche Rauheit. Diamant verwendet Metalligkeit 0. Alle vier haben Emission und Subsurface 0. Die originalen 16-Pixel-Farbtexturen bleiben enthalten; es gibt keine neu erzeugten Normalmaps oder hochauflösenden Oberflächendetails. Für einen fotorealistischen Gesamtlook fehlen daher weiterhin flächendeckende hochauflösende Materialien.

## Enginegrenzen und Quellen

- [Wassereffekte](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/watercustomization?view=minecraft-bedrock-stable): dokumentierte Partikel, Wellen und Caustics. Wellen sind bildbasiert; sie verändern keine Eckpunkte der Wasserfläche.
- [Licht und Reflexionen](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/lightingcustomization?view=minecraft-bedrock-stable): Lux, Himmelslicht, IBL und SSR. Vollständige Spiegelungen außerhalb des Bildes und Spiegel des eigenen Spielermodells sind damit nicht herstellbar. Eine zusätzliche Raytracing-Pipeline lässt sich durch dieses Ressourcenpaket nicht einschalten.
- [Tonemapping](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/colorgradingtonemappingcustomization?view=minecraft-bedrock-stable): ACES und weitere vorgegebene Operatoren. Die Kurven sind nicht frei programmierbar.
- [Biomübergänge](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/biomecustomization?view=minecraft-bedrock-stable): räumliches Überblenden von Wasser sowie Grenzen bei Caustics und anderen diskreten Parametern.
- [Materialdefinitionen](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/texturesetsreference/texturesetsconcepts/texturesetsintroduction?view=minecraft-bedrock-stable): binäre Metalligkeit, Rauheit, MERS und Texturreferenzen.

Die Abnahme erfolgt mit den Szenen in `BENCHMARK.md`. Vor einem solchen Test darf das Paket weder als fotorealistisch nachgewiesen noch als auf 80 FPS optimiert bezeichnet werden.
