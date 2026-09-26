# Galaxienhimmel · 0.4.0

Eine selbst erzeugte Fantasy-Himmelsgrafik ergänzt nächtliche Galaxien und Nebel, angelehnt an die vom Nutzer gewünschte Oblivion-Stimmung. Die Datei `assets/night_sky/source-v2.png` ist die gewählte Bildvorlage. Sie ist kein Minecraft-Testbild. Erzeugt und gezielt an den Polen überarbeitet mit dem eingebauten image_gen-Werkzeug; beide vollständigen Prompts stehen in `assets/night_sky/PROMPT.md`. Originalmaterial aus Oblivion wird nicht mitgeliefert.

## Aufbau

- Sechs PNGs unter `textures/environment/overworld_cubemap/cubemap_0.png` bis `cubemap_5.png`, jeweils 1024 × 1024 RGB. Eine gemeinsame Vorlage verhindert sechs voneinander unabhängig gestaltete Himmelsflächen. Die Auflösung der Vorlage beträgt 1774 × 887; die Umrechnung erzeugt keine zusätzlichen nativen Details.
- Die Dateien sind gemeinsam unter `textures/textures_list.json` registriert. Sie werden nicht in vier Unterpaketen vervielfacht.
- `cubemaps/galaxy.json` nutzt ausschließlich dokumentierte Felder mit Schema `1.21.130` und der Kennung `lumen:galaxy`. Alle 83 vorhandenen Overworld-Biome verweisen darauf. Die Formatversion älterer Biomdateien wird auf mindestens `1.21.130` angehoben.
- In 78 Biomen bleiben die Licht-/Wasserabstimmungen aus 0.3.0 bestehen. Pale Garden, Deep Dark, Lush Caves, Dripstone Caves und Sulfur Caves erhalten nur die Cubemap-Zuordnung; deren weitere Komponenten werden aus den festgehaltenen Originaldateien übernommen. Nether und Ende sind ausgenommen.
- Alle vier Unterpakete enthalten eine eigene Helligkeitskurve und vollständige Biomdateien. Natürlich erreicht 0,8 Lux Cubemap-Umgebungslicht, Geheimnisvoll 0,96, Herbst 0,68 und Halloween 0,88. Das sind gestalterische Ausgangswerte, keine bestätigten Bildschirmhelligkeiten.

## Tagesverlauf

In Bedrocks Tageskurve ist 0/1 Mittag, 0,25 Sonnenuntergang und 0,5 Mitternacht. Die Grafik erhält bis 0,30 kein eigenes Licht, wird bis 0,45 eingeblendet, bleibt bis 0,58 am Maximum und ist ab 0,73 wieder unbeleuchtet. Sonnen- und Himmelslicht tragen zusätzlich jeweils null zur Cubemap bei. So soll sie vor allem in dunklen Nächten sichtbar werden. Der Renderer kann die Wahrnehmung durch Belichtung, Wetter und Nebel verändern.

Atmosphärische und volumetrische Streuung sind eingeschaltet, damit die Kulisse als vom Boden beobachteter Nachthimmel hinter Luft und Nebel liegt. Insbesondere die Verbindung aus schwarzer Tages-Cubemap und atmosphärischem Tageshimmel muss noch im Spiel abgenommen werden: Null Lux in einer JSON-Datei beweist keine korrekte Sichtbarkeit oder Unsichtbarkeit im Renderer. Eine frei animierte Deckkraft wird vom verwendeten Schema nicht angeboten.

Die Grafik selbst ist statisch. Das zeitliche Erscheinen wird durch Beleuchtung gesteuert; es gibt keine zusätzlichen Galaxien-Entities, Partikel, Spielbefehle oder Behavior-Packs. Eine Spiegelung der Galaxien auf Wasser ist nicht als getestete Funktion ausgewiesen.

## Grafikprüfung und Export

Die erste Vorlage wurde nach der Umrechnung an der oberen Würfelfläche geprüft. Ihre Sterne bildeten dort zu starke Streifen. Die ausgewählte zweite Vorlage reduziert scharfe Sterne an den Polen; die originale erste Vorlage bleibt zur Nachvollziehbarkeit erhalten. Alle sechs endgültigen Flächen werden aus derselben Vorlage mit FFmpeg `v360` exportiert. Die Formatumrechnung bearbeitet weder Motiv noch Farben kreativ.

Der verwendete Export ordnet die Flächen als vorne/rechts/hinten/links/oben/unten an (`frblud`, keine zusätzliche Drehung). Die Implementierung von [PackAnvil](https://packanvil.com/en/use-cases/custom-skybox) beschreibt die entsprechende Bedrock-Reihenfolge. Die tatsächliche Orientierung und insbesondere Ober-/Unterseitenanschlüsse sind ohne Renderer nicht bestätigt. Im Spiel alle Richtungen, den Zenit und die Naht am Panorama-Umlauf prüfen. Automatische Hash- und Strukturprüfungen sind kein Nachweis für sichtbare Nahtfreiheit.

Der normale Build benötigt weiterhin nur Python. `scripts/convert_sky.py` ist eine optionale Neu-Exportierung mit FFmpeg; die geprüften sechs PNGs sind bereits Teil des Quellarchivs. Bildvorlagen, Flächen und Prüfsummen liegen gemeinsam in `assets/night_sky/`.

Der Export schreibt zunächst in ein temporäres Verzeichnis und prüft alle sechs
PNG-Dateien, bevor bestehende Flächen ersetzt werden. Bei einem FFmpeg-Abbruch
bleiben die bisherigen Flächen und `source.json` erhalten. Bei Schreibfehlern
während der Übernahme versucht das Skript, die Originaldateien zurückzusetzen.
Schlägt auch diese Wiederherstellung fehl, meldet es den erhaltenen Sicherungspfad;
die Originaldateien dort bewahren und nach Behebung des Dateisystemfehlers
wiederherstellen. Das Verfahren garantiert keine atomare Mehrdateiänderung bei
Stromausfall oder erzwungenem Prozessabbruch.

Die Prüfsummenliste enthält ausschließlich die beiden benannten Vorlagen und
sechs Würfelflächen. Zusätzliche PNG-Vorschauen bleiben als lokale Dateien erhalten
und werden nicht in diese Liste aufgenommen. Nach einem erfolgreichen neuen
Export Paketquellen regenerieren und die vollständigen Prüfungen ausführen.

## Quellen und Windows-Abnahme

- [Microsoft: Cubemaps](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/cubemapcustomization?view=minecraft-bedrock-stable): Beleuchtung, Tageskurven, Streuung und Beschränkung auf die Overworld.
- [Microsoft: Cubemap-Biomkomponente](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/clientbiomesreference/examples/components/minecraftclientbiomes_cubemap_identifier?view=minecraft-bedrock-stable): Kennung und erforderliche Formatversion.
- [Microsoft: Biomzuordnung](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/biomecustomization?view=minecraft-bedrock-stable): individuelle Zuordnung statt ausschließlicher globaler Datei.

Zur Abnahme in einer Testwelt bei freiem Blick nach oben Mittag, Sonnenuntergang, Mitternacht und Sonnenaufgang vergleichen. Bei Regen und Nebel prüfen, ob die Himmelsgrafik zu stark durchscheint. Anschließend alle vier Stile und Übergänge in Pale Garden sowie Höhlenbiome prüfen. Nahtfreiheit, natürlicher Tageshimmel, Lesbarkeit bei Nacht und Bildrate sind auf macOS nicht in Minecraft Bedrock getestet worden.
