# Realismus-Abstimmung · 0.5.1

Ziel ist ein glaubwürdiger natürlicher Look innerhalb von Bedrock Vibrant Visuals, mit Schwerpunkt Wasser. „Natürlich“ ist die neutrale Variante; die drei Themenstile bleiben bewusst künstlerisch gefärbt. Es gab keinen Zugriff auf den Windows-Renderer. Die folgenden Entscheidungen sind anhand der dokumentierten Parameter begründet, aber noch nicht durch Vergleichsbilder oder GPU-Messungen bestätigt.

## Wasser

Die Einstellungen stehen zentral in `scripts/water_profiles.py`. Die Werte für CDOM, Chlorophyll und Sediment sind selbst gewählte Abstimmungen in den von Bedrock vorgegebenen Einheiten, keine Messungen oder wissenschaftlich kalibrierten Gewässermodelle.

| Profil | Typische Zuordnung | Oberflächencharakter | Zusammensetzung |
|---|---|---|---|
| See | Gemäßigte Landbiome | Kleine, ruhige Wellen | Geringe Konzentrationen |
| Klarer See | Kalte Landbiome, gefrorener Fluss | Sehr flache Kräuselung | Besonders geringe Konzentrationen |
| Fluss | Flussbiom | Feinere, schnellere Bewegung | Mehr gelöste organische Stoffe und Sediment |
| Küste | Strand, steiniger Strand, Pilzinsel-Ufer | Flache Wellen | Etwas mehr Sediment als offenes Meer |
| Meer | Normales, tiefes und lauwarmes Meer | Flache, etwas breitere Wellen | Geringe Konzentrationen |
| Kaltes Meer | Kalte/gefrorene Meere, kalter Strand | Etwas ruhigere Meereswellen | Geringe Konzentrationen |
| Tropisch | Warmes und tiefes warmes Meer | Flache weiche Wellen | Sehr wenig gelöste Stoffe |
| Sumpf | Sumpf und Mangroven | Fast ruhige Oberfläche | Mehr CDOM, Chlorophyll und Sediment |

Für die ausdrücklich gewünschte leichte Abdunklung werden seit 0.5.0 die ursprünglichen CDOM- und Chlorophyllwerte mit 1,10 multipliziert. Sediment und Caustics bleiben gleich. Der Nutzer hat diese Näherung für das Ziel „10 % dunkler“ akzeptiert; 10 % mehr Konzentration sind keine gemessenen 10 % weniger Bildhelligkeit. Absorption und Streuung berechnet die Engine. `biome_water_color_contribution` ist null, damit sich die klassische blaue Biomfarbe nicht zusätzlich wie Farbstoff über das Ergebnis legt. Die Themen verändern weder Wasserzusammensetzung noch Wellen. Ihre Farben wirken über die Beleuchtung und das fertige Bild.

Seit 0.5.0 sind weiche, nahezu sinusförmige Wellen abgestimmt. In 0.5.1 ist ihr `depth`-Parameter in allen acht Gewässerprofilen gegenüber 0.5.0 verdreifacht: 0,135–0,54 statt 0,045–0,18. Das verstärkt Bedrocks bildbasierten Welleneffekt; die Wasseroberfläche erhält keine geometrisch dreimal höheren Wellen. Die sichtbare Wirkung muss im Spiel geprüft werden. Geschwindigkeit 0,30–0,70, Form 1,04–1,14 und geringer Zug 0,10 bleiben gleich. Die Frequenz steigt pro Ebene um Faktor 1,16, die Geschwindigkeit nur um 1,01. Die Wellen enthalten mehrere Frequenzen und Bewegungsraten. Pro Ebene dreht die Richtung um etwa 137,51 Grad; dadurch wiederholen sich die Richtungen nicht bereits nach fünf Ebenen wie zuvor. Grundfrequenz, Geschwindigkeit und Schärfe unterscheiden sich je Gewässer. Quality verwendet 16 Ebenen mit `sampleWidth=0.055`, Balanced 8 mit `sampleWidth=0.11`. Mehr Ebenen erhöhen den möglichen Detailgrad, garantieren aber weder bessere Bildwirkung noch eine bestimmte Bildrate. Feine Details müssen in Bewegung auf Flimmern geprüft werden.

Für Caustics wird die eingebaute Animation mit 64 Bildern verwendet: 0,09 Sekunden pro Bild, Stärke 1, Skalierung 0,5. Das sind dezente Ausgangswerte; ein gleichzeitiger Vergleich bei Sonnenlicht ist nötig. Alle Biome verwenden dieselben Caustics, weil Bedrock diese Parameter nicht weich überblenden kann.

Die Zuordnung ist biombasiert. Ein künstliches Schwimmbecken im Ozeanbiom erhält dessen Wellenprofil, ein Bergsee keine automatisch erkannte Tiefe. Flusswellen folgen keiner ausgelesenen Fließrichtung. Brechung, Sichttiefe und winkelabhängige Reflexion bleiben Aufgabe der Engine. Es wurden keine erfundenen Optionen für Reflexionsauflösung, Brechungsindex, Brandung, Schaum oder Strömung hinzugefügt.

## Licht und Materialien

Die Helligkeitsgrundlage stammt seit 0.4.3 direkt aus Mojangs tatsächlichen Paketdateien am festgehaltenen Commit `46ba6ea985fb5a92d79a9419198f10dda14c199d`. Neu enthalten sind `reference/resource_pack/lighting/global.json` und `reference/resource_pack/color_grading/color_grading.json`; Abrufdatum und SHA-256 stehen in `reference/source.json`, Rechtehinweise in `NOTICE.md`.

Die Sonnenkurve erreicht dort **100**, während Lumen bis 0.4.2 **110.000** verwendete. Dieser Faktor 1.100 ist ein belegter Unterschied der Parameter, keine Messung der Bildschirmhelligkeit. Die Learn-Dokumentation beschreibt auch physikalische Beispiele über 100.000 Lux; diese sind kein identisches Preset zur ausgelieferten Mojang-Datei. Nach der erneuten Rückmeldung zur Überhelligkeit werden jetzt die vollständigen Sonnen- und Mondhelligkeitskurven der Paketreferenz übernommen. Nur Reihenfolge und Schreibweise der Zeitschlüssel werden vereinheitlicht; weder Zeitpunkte noch Werte werden umskaliert. Das Sonnenlicht bleibt zwischen 0,292 und 0,709 auf null, das Mondmaximum beträgt 0,4. Umgebungslicht 0,02, Emissionsentsättigung 0 und Sonnenbahnversatz 0 stammen ebenfalls aus der Referenz. Die Lumen-Lichtfarben und gedämpften Sonnen-/Himmelsfaktoren der Themen bleiben erhalten; das Mondlicht wird durch Themen nicht verstärkt.

Natürlich übernimmt die vollständige originale Farbkorrektur: **Generic-Tonemapping**, Kontrast 1,15, Gain 1,0, Gamma 2,2, Offset 0, Sättigung 1,05 und Farbtemperatur 6500 K. Damit entfällt die pauschale Gain-Absenkung auf 0,65 aus 0.4.2. Alle Themen behalten den Standardkontrast und Gamma; ihre RGB-Tönungen werden relativ zum stärksten Kanal normalisiert, sodass kein Kanal über den Standard-Gain angehoben wird. Quality und Balanced enthalten dieselben Werte. Generic ist Mojangs angepasste Tonemapping-Kurve; eine allgemeingültige Empfehlung für jede Szene oder jeden Monitor wird damit nicht behauptet.

Regressionstests vergleichen alle 20 exportierten Lichtdateien und fünf Farbkorrekturen mit den festgehaltenen Referenzen und prüfen beide Installer. Der Validator weist die frühere 110.000-Spitze und ACES zurück. Die tatsächliche Belichtung und Lesbarkeit bei Mittag auf Schnee/Wasser, bei Nacht und beim Wechsel von Höhle zu Tageslicht bleiben offene Bedrock-Sichttests. Die Galaxiengrafik und ihre eigenständige Nachtkurve werden durch diese Korrektur nicht neu gestaltet.

Die drei Metallblöcke erhalten binäre Metalligkeit 255 und unterschiedliche Rauheit. Diamant verwendet Metalligkeit 0. Alle vier haben Emission und Subsurface 0. Die originalen 16-Pixel-Farbtexturen bleiben enthalten; es gibt keine neu erzeugten Normalmaps oder hochauflösenden Oberflächendetails. Für einen fotorealistischen Gesamtlook fehlen daher weiterhin flächendeckende hochauflösende Materialien.

## Enginegrenzen und Quellen

- [Wassereffekte](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/watercustomization?view=minecraft-bedrock-stable): dokumentierte Partikel, Wellen und Caustics. Wellen sind bildbasiert; sie verändern keine Eckpunkte der Wasserfläche.
- [Licht und Reflexionen](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/lightingcustomization?view=minecraft-bedrock-stable): Lux, Himmelslicht, IBL und SSR. Vollständige Spiegelungen außerhalb des Bildes und Spiegel des eigenen Spielermodells sind damit nicht herstellbar. Eine zusätzliche Raytracing-Pipeline lässt sich durch dieses Ressourcenpaket nicht einschalten.
- [Mojang-Lichtprofil](https://github.com/Mojang/bedrock-samples/blob/46ba6ea985fb5a92d79a9419198f10dda14c199d/resource_pack/lighting/global.json) und [Mojang-Farbprofil](https://github.com/Mojang/bedrock-samples/blob/46ba6ea985fb5a92d79a9419198f10dda14c199d/resource_pack/color_grading/color_grading.json): konkrete Basiswerte dieses Pakets.
- [Tonemapping](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/colorgradingtonemappingcustomization?view=minecraft-bedrock-stable): Generic und weitere vorgegebene Operatoren. Die Kurven sind nicht frei programmierbar.
- [Biomübergänge](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/biomecustomization?view=minecraft-bedrock-stable): räumliches Überblenden von Wasser sowie Grenzen bei Caustics und anderen diskreten Parametern.
- [Materialdefinitionen](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/texturesetsreference/texturesetsconcepts/texturesetsintroduction?view=minecraft-bedrock-stable): binäre Metalligkeit, Rauheit, MERS und Texturreferenzen.

Die Abnahme erfolgt mit den Szenen in `BENCHMARK.md`. Vor einem solchen Test darf das Paket weder als fotorealistisch nachgewiesen noch als auf 80 FPS optimiert bezeichnet werden.

## Geschützte Helligkeit

Am 26.09.2026 bestätigte der Nutzer die Helligkeit von 0.4.3.
`reference/approved_brightness.json` speichert davon unabhängige Fingerprints
für alle vier Stile. Validator, Build und CI stoppen auch bei kleinen, sonst
gültigen Änderungen an Licht, Farbkorrektur, Atmosphäre, Cubemap, lokalen
Lichtern, Materialdefinitionen und Grafikzuordnungen. Die Wasserabdunklung ist
als später ausdrücklich beauftragte Ausnahme dokumentiert; Wellenparameter
sind unabhängig. Keine automatische Regeneration dieser Referenz.
Die Rückmeldung ist keine vollständige Engine- oder Leistungsabnahme.
Die Blatt- und Nebelbewegung ist in [MOTION.md](MOTION.md) beschrieben.
