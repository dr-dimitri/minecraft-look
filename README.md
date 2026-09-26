# Lumen WQHD · Bedrock

Ein Grafikpaket für Minecraft Bedrock unter Windows mit vier auswählbaren Stilen: **Natürlich, Geheimnisvoll, Herbst und Halloween**. Acht Gewässerprofile, Tageslicht in realistischen Lux-Größenordnungen und filmische Helligkeitsdarstellung bilden die Grundlage. Für den möglichst natürlichen Look **Quality + Natürlich** wählen. Quality ist die vorgesehene erste Wahl für die RX 9060 XT mit 16 GB Grafikspeicher bei 2560 × 1440.

**Version 0.4.2 ist eine technisch geprüfte Testversion.** Rund 80 FPS sind das Entwicklungsziel, kein Messergebnis. Hier stand weder Minecraft für Windows noch die Zielgrafikkarte für eine Sicht- oder Leistungsprüfung zur Verfügung. Bildwirkung, Import, Stilauswahl und Leistung müssen deshalb noch im Spiel geprüft werden. Die neue Abstimmung zielt auf mehr Realismus; fotorealistische Ergebnisse sind noch nicht visuell bestätigt. Es gibt keine automatische GPU-Erkennung oder automatische FPS-Regelung.

## Installieren

1. `Lumen-WQHD-Quality-0.4.2.mcpack` aus dem vom Build ausgegebenen Artefaktverzeichnis beziehungsweise einem GitHub-Release herunterladen. „Source code.zip“ bei GitHub ist der Quellcode, nicht das Installationspaket.
2. Unter Windows die `.mcpack` doppelklicken. Falls nötig „Öffnen mit → Minecraft für Windows“ wählen und den erfolgreichen Import abwarten.
3. In der gewünschten Welt unter **Ressourcenpakete → Meine Pakete** Lumen WQHD aktivieren. Zum ersten Test nur dieses zusätzliche Grafikpaket verwenden.
4. Im Hauptmenü unter **Einstellungen → Video → Grafikmodus** **Vibrant Visuals** auswählen. Ein Ressourcenpaket schaltet den Grafikmodus nicht selbst um.
5. Welt öffnen. An einem Fluss, beim Sonnenuntergang und neben einer Laterne prüfen. Bei Problemen den Content-Log einschalten und Fehlermeldungen notieren.

Ziel ist Bedrock 26.50/26.51; das interne Manifest verwendet dazu `[1,26,50]`. Ein späteres Update kann eine erneute Prüfung erfordern. Keine Preview, experimentellen Welteinstellungen oder veränderten Spielprogramme erforderlich. Ein Marketplace-Kauf wird für dieses Paket nicht benötigt.

## Grafikstil wählen

1. Welt verlassen und ihre Einstellungen über das Stiftsymbol öffnen.
2. **Ressourcenpakete → Aktiv → Lumen WQHD → Zahnrad** öffnen.
3. Den Regler auf den gewünschten Stil stellen. Die Bezeichnung der gewählten Variante wird im Dialog angezeigt.
4. Welt wieder öffnen, damit die Ressourcen neu geladen werden.

Die Auswahl verwendet Bedrocks eingebaute Unterpakete (Subpacks). Die genaue Menüanordnung kann je nach Version abweichen. **Beide Pakete, Quality und Balanced, enthalten alle vier Stile.**

| Stil | Gestaltung |
|---|---|
| Natürlich | Standard für Realismus: neutrale Tagesfarben, warme Abendsonne, dezentes Mondlicht und natürliche Wasseroptik. |
| Geheimnisvoll | Kühlere Blau- und Türkistöne, gedämpftes Sonnenlicht und kühlere Himmelsfarben. |
| Herbst | Goldene Lichtfarben und orange-gelbe Laubtönungen in 15 ausgewählten Oberflächenbiomen. |
| Halloween | Orangefarbenes Sonnen- und Laternenlicht, violette Mond- und Himmelsfarben, stärkere Kontraste. |

Herbst färbt Laub, das seine Farbe vom Biom erhält. Blätter mit fester Texturfarbe können ihre ursprüngliche Farbe behalten; es ist kein Austausch sämtlicher Baumtexturen. Nachtlicht bleibt in den Einstellungen bei allen Stilen vorhanden; die tatsächliche Sichtbarkeit muss im Spiel geprüft werden. Die Auswahl verändert keine Spielregeln, Wetterabläufe oder Kreaturen und wechselt nicht automatisch mit dem Kalender.

Version 0.4.2 senkt die gemeinsame Bildhelligkeit in allen vier Stilen: Farbkorrektur-Gain 0,65 statt 1,0, bei „Natürlich“ zusätzlich neutraler Kontrast. Quality und Balanced übernehmen dieselbe Korrektur; die Stilfarben bleiben erhalten. Die genaue Helligkeit und Lesbarkeit bei Tag und Nacht müssen noch in Bedrock verglichen werden.

Die Auswahl hat bewusst keine Hardware-Sperren: Alle Stile verwenden dieselbe Wellenqualität und dieselbe Speicherstufe. „Natürlich“ steht als Standard am Ende der Manifestliste. Ein Stilwechsel ersetzt die vollständigen betroffenen Ressourcen, einschließlich der Biomfarben, damit zum Beispiel Herbstfarben beim Zurückwechseln nicht im Paket bestehen bleiben. Weitere Stile lassen sich in `scripts/themes.py` ergänzen.

Bei einem Update bleiben die Paket-UUIDs erhalten. Version 0.4.2 ist als Update von 0.4.1 für dasselbe Quality- beziehungsweise Balanced-Paket vorgesehen; der Importpfad muss noch in Bedrock geprüft werden. Danach die aktive Variante und den gewählten Stil kontrollieren.

## Galaxienhimmel in Version 0.4.0

Bei Nacht ergänzt eine eigene Himmelsgrafik ein Sternenband, zwei entfernte Galaxien und blau-violette Nebel. Die Gestaltung greift die gewünschte Fantasy-Stimmung auf; es wurden keine Texturen aus Oblivion verwendet. Der Himmel ist in allen vier Stilen enthalten, mit etwas stärkerer Leuchtkraft in „Geheimnisvoll“ und „Halloween“ und dezenterer in „Herbst“.

Die Beleuchtung der Himmelsgrafik steigt nach Sonnenuntergang allmählich an und fällt vor dem Tag wieder auf null. Direkte Sonnen- und Himmelsbeleuchtung der Grafik sind deaktiviert, atmosphärische Streuung und Nebel bleiben berücksichtigt. Das soll tagsüber den natürlichen Himmel erhalten. **Ob der Renderer dieses Zusammenspiel wie vorgesehen zeigt, muss unter Windows geprüft werden; das Einblenden ist bisher nur auf Ebene der Datenkurven getestet.**

Die Himmelstexturen werden einmal für alle Stile mitgeliefert: sechs Flächen à 1024 × 1024 Pixel, technisch aus einer generierten 1774 × 887-Pixel-Panoramagrafik umgerechnet. Das erhöht nicht die native Detailauflösung. Es gibt keine zusätzlichen Spielobjekte, Partikel oder Gameplay-Skripte. Die grafische Vorlage ist eine Texturvorschau, kein Screenshot aus Minecraft.

In 78 Oberflächenbiomen gelten die bisherigen vollständigen Grafikabstimmungen. Fünf weitere Overworld-Biome erhalten ausschließlich die Zuordnung zur Himmelsbeleuchtung, damit dort keine durchgehend helle Standard-Skybox greift. Nether und Ende werden nicht umgestellt. Details, Quellen und Sichtprüfung: `docs/NIGHT_SKY.md`; Erzeugungsprompts: `assets/night_sky/PROMPT.md`.

Optionale Gameplay-Erweiterungen werden unabhängig im Repository
[minecraft-addons](https://github.com/dr-dimitri/minecraft-addons) gepflegt.
Dieses Repository enthält ausschließlich die Grafikpakete.

## Wasser und Realismus seit Version 0.3.0

- Acht getrennte Gewässerprofile für See, klaren/kühlen See, Fluss, Küste, Meer, kaltes Meer, tropisches Meer und Sumpf. Die Zuordnung folgt dem Biom; sie erkennt keine Fließrichtung, Wassertiefe oder tatsächliche Gewässergröße.
- Größere, langsamere Wellenmuster auf dem Meer, flachere Kräuselung auf Seen und Sümpfen, schnellere Bewegung in Flüssen. Quality verwendet 16 Ebenen und eine feinere Abtastung als bisher. Die Drehung zwischen den Ebenen vermeidet ein regelmäßig wiederholtes Muster aus fünf Richtungen.
- Die Wasserfarbe entsteht aus Bedrocks Lichtabsorption und Streuung mit unterschiedlichen Anteilen gelöster Stoffe und Schwebstoffe. Die zusätzliche Vanilla-Biomfärbung ist ausgeschaltet. Auch Halloween und Herbst verwenden diese Wasserwerte; ihre Stimmung entsteht über Licht, Himmel und Farbkorrektur.
- Dezente, langsamer animierte Lichtmuster am Grund (Caustics). Einheitliche Werte verhindern nicht überblendbare Wechsel zwischen Gewässerprofilen.
- Sonnenlicht bis 110.000 Lux, Mondlicht bis 0,27 Lux im natürlichen Stil, kräftiger Beitrag des Himmels zu indirektem Licht und Reflexionen. ACES-Tonemapping und zurückhaltende Farbkorrektur sind auf die große Helligkeitsspanne abgestimmt.
- Eisen, Gold und Kupfer werden als Metalle mit jeweils eigener Rauheit behandelt; Diamant bleibt nichtmetallisch.

Die Wasserprofile sind gestaltete Ausgangswerte, keine Messdaten echter Gewässer. Spiegelungen und Brechung werden vom eingebauten Renderer berechnet. Die Wellen verändern die Wassergeometrie nicht, und Spiegelungen von Objekten außerhalb des Bildausschnitts sind durch das verwendete SSR-Verfahren begrenzt. Die Block-Farbtexturen bleiben auf Vanilla-Auflösung; dieses Paket enthält keine flächendeckenden Fototexturen. Technische Entscheidungen und Grenzen: `docs/REALISM.md`.

## Startprofil: Details vor maximalen FPS

Diese Werte sind ein vorgeschlagener Mess-Ausgangspunkt, keine auf der Zielhardware gemessene Empfehlung:

| Einstellung | Ausgangspunkt |
|---|---|
| Ausgabeauflösung | 2560 × 1440 |
| Pack | Quality |
| Stil | Natürlich |
| Vibrant-Visuals-Vorgabe | Grafikqualität bevorzugen / Favor Visuals |
| Interne Renderauflösung | Zunächst nativ / 100 %, sofern angeboten |
| Sichtweite | 16 Chunks |
| Simulationsdistanz | 6 Chunks |
| Bildratenlimit | Für Messungen deaktivieren; anschließend etwa 80 FPS, soweit einstellbar |

Die Menübezeichnungen können je nach Sprache und Version abweichen. Packwerte betreffen Licht, Farbe, Wasser und Materialeigenschaften. Schattenauflösung, Sichtweite, interne Auflösung und Bildratenlimit werden in Minecraft eingestellt und gehören nicht zum `.mcpack`.

Bei dauerhaft weniger als etwa 75–80 FPS zuerst die Sichtweite von 16 auf 12 Chunks testen. Bei starkem Einbruch an großen Wasserflächen anschließend **Balanced** probieren. Erst danach einzelne Engine-Effekte reduzieren oder die interne Auflösung geringfügig senken. Dabei immer denselben Weg und Blickwinkel vergleichen. Wenn hauptsächlich neue Chunks ruckeln, ist das kein ausreichender Beleg für ein GPU-Problem.

Quality und Balanced unterscheiden sich ausschließlich in der Wellenberechnung: 16 beziehungsweise 8 Ebenen und eine unterschiedliche Abtastbreite. Licht, Farben, Lichtmuster unter Wasser und Materialwerte bleiben gleich. Die Dateien haben unterschiedliche Paket-UUIDs; **immer nur eine Variante aktivieren**. Der mögliche Geschwindigkeitsgewinn wurde nicht gemessen. Die höhere Wellenqualität gegenüber 0.2.0 kann mehr GPU-Zeit benötigen; deshalb Bildrate und ruhige Bewegung erneut prüfen.

## Was enthalten ist

- 78 Oberflächenbiome mit erhaltenen Vanilla-Angaben für Nebel, Wassergrundfarbe, Geräusche und weitere unveränderte Eigenschaften. Übersicht: `docs/biome-map.json`.
- Vier Licht-/Himmelsabstimmungen für gemäßigte, warme, kalte und feuchte Gebiete; durchgängige Übergänge über den Tag.
- Acht Wasserprofile für Seen, Flüsse, Küsten, Meere und Sümpfe. Die Wellen sind der von Vibrant Visuals unterstützte Bildeffekt, keine geometrisch angehobene Wasseroberfläche.
- Warme Fackeln/Laternen und kühlere Seelenlichter; keine zusätzlichen Punktlicht-Blöcke.
- Angepasste Materialrauheit für Eisen, Gold, Kupfer und Diamant. Die vier originalen Farbtexturen sind unverändert; es ist kein vollständiges HD-Texturpaket.
- Pale Garden und vier Höhlenbiome erhalten nur die Galaxienhimmel-Zuordnung; deren sonstige Originalangaben bleiben erhalten. Nether und Ende erhalten keine neuen Biomzuordnungen. Die vier Material- und Laternen/Fackel-Anpassungen gelten überall.

## Bauen und für GitHub vorbereiten

Python ab 3.10 genügt; keine zusätzlichen Python-Pakete und kein Netzwerkzugriff beim Build nötig.

```text
python scripts/create_pack.py
python -m unittest discover -s tests -v
python scripts/build.py
```

Der Build erzeugt Ressourcen in einer temporären Kopie frisch aus den Quellen und prüft sie vor dem Verpacken. Auch Änderungen bei gleicher Versionsnummer werden übernommen; lokale Bearbeitungen in `pack/` und `docs/biome-map.json` bleiben erhalten und werden nicht eingepackt. Für mitzuversionierende Ausgaben weiterhin `create_pack.py` ausführen. Das Quellarchiv enthält nur die in `scripts/source_archive.py` deklarierten Projektdateien; lokale Umgebungen und versteckte Zusatzdateien werden ausgeschlossen.

Unter Windows kann bei Bedarf `py -3` statt `python` verwendet werden. Das Ergebnis liegt als vollständiger Satz unter `dist/<Version>/<Satz-SHA256>/`: zwei `.mcpack`, ein Quellcode-ZIP und SHA-256-Prüfsummen. Der Build gibt den Pfad aus; `dist/current.json` verweist auf den zuletzt erfolgreichen Satz. Alte Ausgaben bleiben erhalten. Dateien direkt unter `dist/` aus früheren Builds werden nicht mehr aktualisiert und dürfen nicht pauschal hochgeladen werden. Die Archive enthalten `manifest.json` direkt auf oberster Ebene.

Die Basiswerte werden in `scripts/create_pack.py`, die Wasserprofile in `scripts/water_profiles.py`, die Himmelsbeleuchtung in `scripts/night_sky.py` und die Stile in `scripts/themes.py` gepflegt; `pack/` und `docs/biome-map.json` sind daraus erzeugte Dateien. Die Himmelstexturen sind unter `assets/night_sky/` enthalten und werden beim normalen Build nur kopiert. Nur die optionale erneute Umrechnung der Panoramagrafik mit `scripts/convert_sky.py` benötigt FFmpeg. UUIDs bei normalen Updates beibehalten und die Version in `scripts/create_pack.py` erhöhen. Änderungen direkt in `pack/` würden beim Erzeugen überschrieben.

Dieses Projekt wird als [minecraft-look](https://github.com/dr-dimitri/minecraft-look) gepflegt. Der Workflow prüft auf Linux (Python 3.10 und 3.14.7) und Windows (Python 3.14.7). `python scripts/verify_build.py` führt auch lokal einen vollständigen Wiederholungsbuild und einen eigenständigen Neubau aus dem Source-ZIP aus und vergleicht alle drei Archive bytegenau. Dies gilt innerhalb derselben Python-/zlib-Umgebung, nicht als Garantie identischer Kompression zwischen Plattformen. Ein passender Tag (`vX.Y.Z`) erzeugt nach erfolgreichen Prüfungen einen GitHub-Release-Entwurf mit den passenden Artefakten. Die öffentliche Freigabe folgt erst nach der dokumentierten Abnahme. Automatische Tests erzeugen keine Minecraft-Leistungsmessungen.

Projektvorgaben stehen in [AGENTS.md](AGENTS.md), der vollständige Ablauf in [docs/RELEASING.md](docs/RELEASING.md). Die projektlokalen Skills `lumen-pack-development` und `lumen-release` liegen unter `.agents/skills/`. Änderungen werden in [CHANGELOG.md](CHANGELOG.md) gepflegt. Für die Freigabe gibt es eine [Abnahmevorlage](docs/releases/TEMPLATE.md) und das [Verfahren für eine feste Testwelt](docs/TEST_WORLD.md).

## Quellen und Prüfung

- [Vibrant Visuals und Aktivierung](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/introvibrantvisuals?view=minecraft-bedrock-stable)
- [Auswählbare Unterpakete und Standardauswahl](https://learn.microsoft.com/en-us/minecraft/creator/documents/buildingsubpacks?view=minecraft-bedrock-stable)
- [Laubfarben in Biomen](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/clientbiomesreference/examples/components/minecraftclientbiomes_foliage_appearance?view=minecraft-bedrock-stable)
- [Biomzuordnung](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/biomecustomization?view=minecraft-bedrock-stable)
- [Cubemap-Beleuchtung](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/cubemapcustomization?view=minecraft-bedrock-stable)
- [Licht](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/lightingcustomization?view=minecraft-bedrock-stable), [Atmosphäre](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/atmosphericscustomization?view=minecraft-bedrock-stable), [Farbe](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/colorgradingtonemappingcustomization?view=minecraft-bedrock-stable), [Wasser](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/watercustomization?view=minecraft-bedrock-stable)
- [Textursets](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/texturesetsreference/texturesetsconcepts/texturesetsintroduction?view=minecraft-bedrock-stable)
- Originalreferenzen mit festem Commit und Prüfsummen: `reference/source.json`; Rechtehinweise: `NOTICE.md`.
- Umfang und Grenzen der lokalen Prüfung: `docs/VALIDATION.md`; Vorgehen auf dem Ziel-PC: `docs/BENCHMARK.md`.
