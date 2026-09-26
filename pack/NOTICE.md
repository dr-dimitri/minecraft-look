# Quellen und Rechte

Lumen WQHD ist ein unabhängiges Ressourcenpaket für Minecraft Bedrock. Es ist kein offizielles Produkt von Mojang, Microsoft oder AMD.

Die vollständigen Client-Biomdefinitionen (mit angepassten Grafikverweisen), Licht-/Farbprofilgrundlagen und vier unveränderte Farbtexturen für Eisen-, Gold-, Kupfer- und Diamantblöcke stammen aus Mojang/bedrock-samples. Die Referenzkopien unter reference/ stammen ebenfalls daraus.

Quelle: https://github.com/Mojang/bedrock-samples
Stand: 46ba6ea985fb5a92d79a9419198f10dda14c199d, abgerufen am 25.09.2026.
Die Standardprofile `resource_pack/lighting/global.json` und
`resource_pack/color_grading/color_grading.json` wurden am 26.09.2026 vom
selben Commit ergänzt. Einzelprüfsummen und Abrufprotokoll: `reference/source.json`.
Die Spieler-Grafikdefinition `resource_pack/entity/player.entity.json` wurde
ebenfalls am 26.09.2026 von diesem Commit ergänzt. Nur der Halloween-Stil
erweitert sie um den rein visuellen Nebel-Emitter; die übrigen Spieleranimationen
werden übernommen. Die weiche Nebeltextur wird durch eigene mathematische
Kurven in `scripts/halloween_fog.py` erzeugt.
Am selben Datum wurden die Atlasreferenz `textures/terrain_texture.json` und
28 Blatttexturen (PNG/TGA) desselben Commits ergänzt. Die daraus erzeugten
Animationsstreifen ordnen Originalpixel um; Farben und Transparenz stammen
weiterhin von Mojang. Pfade und Einzelprüfsummen stehen in `reference/source.json`.

(c) Mojang AB. All rights reserved.
By downloading the files in this repository, you agree to the Minecraft End User License Agreement (https://www.minecraft.net/en-us/eula) and that these files are subject to its terms.

Eigene Bestandteile: Build-/Prüfskripte, Dokumentation und Anpassungen der unter lumen: benannten Grafikabstimmungen. Die mitgelieferten Mojang-Dateien und übernommenen Standardprofile werden nicht als eigene oder pauschal frei lizenzierte Inhalte ausgewiesen. Für die Verwendung gelten die Minecraft-Nutzungsbedingungen.

Die Galaxiengrafik wurde mit dem eingebauten image_gen-Werkzeug neu erzeugt und überarbeitet. Die gewünschte Oblivion-Stimmung diente als gestalterischer Bezug; es werden keine Originalgrafiken aus The Elder Scrolls IV: Oblivion verwendet. Quelle, Prompts und Prüfsummen: assets/night_sky/ im Quellarchiv. Der Export in sechs Himmelsflächen erfolgte durch technische Projektionsumrechnung mit FFmpeg.
