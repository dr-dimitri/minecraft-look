# Bewegungseffekte · 0.5.1

Die Helligkeit aus 0.4.3 wurde vom Nutzer bestätigt und bleibt festgeschrieben.
Neue Bewegungen und die gewünschte Wasserabdunklung sind getrennte Änderungen;
ihre tatsächliche Darstellung wurde noch nicht in Bedrock geprüft.

## Wasser

Acht Wasserprofile verwenden weiche, nahezu sinusförmige Wellen. In 0.5.1 ist
der `depth`-Wert jedes Profils genau dreimal so hoch wie in 0.5.0; er liegt
jetzt zwischen 0,135 und 0,54. Frequenz, Geschwindigkeit und Wellenform sind
unverändert. Quality behält 16 Wellenebenen, Balanced 8. Die übrige Bewegung
und die Wasseroptik sind in beiden Varianten und allen vier Stilen gleich.
`depth` verstärkt einen Bildeffekt und ist keine geometrische Wellenhöhe;
wie stark die Wellen sichtbar wirken, bleibt in Bedrock zu prüfen.

Für das Ziel „10 % dunkler“ hat der Nutzer eine Näherung über Lichtabsorption
akzeptiert: CDOM und Chlorophyll werden mit 1,10 multipliziert. Sediment,
Caustics und der ausgeschaltete zusätzliche Biomfarbbeitrag bleiben gleich.
Eine exakt zehnprozentige Verringerung der Bildschirmhelligkeit lässt sich
daraus nicht ableiten; Tiefe, Licht und Wellenreflexe beeinflussen das Ergebnis.
Die bestätigten Licht-/Gradingwerte werden dafür nicht verändert.

## Halloween-Nebelschwaden

`scripts/halloween_fog.py` erzeugt nur im Halloween-Unterpaket eine Erweiterung
der festgehaltenen Vanilla-Spielergrafik. Vorhandene Modelle, Materialien,
Skins, Ausrüstung und Animationsskripte bleiben erhalten. Hinzu kommen ein
eigener Controller, ein Partikeleffekt und eine prozedurale Alpha-Textur.
Es gibt kein Behavior-Pack, keine Commands und keinen Schaden.

Der lokale Spieler löst maximal 16 kleine Partikelflächen aus: zwei pro
Sekunde, je acht Sekunden Lebensdauer, langsame Drift mit 0,35 Blöcken/s.
Sie entstehen vier bis acht Blöcke um den Spieler, blenden weich ein und aus
und bewegen sich nach der Emission unabhängig von Kamera und Spieler weiter.
Alpha-Blending und normale Partikelbeleuchtung vermeiden additives Leuchten.
Die Einstellung ist keine flächendeckende volumetrische Nebelsimulation.

Der Auslöser ist auf 78 vollständig gestaltete Overworld-Biome begrenzt.
Pale Garden und die vier speziellen Höhlenbiome bleiben ausgenommen, ebenso
Nether und Ende. Unter Wasser, beim Schlafen, als Zuschauer und bei der
Spielerfigur in der Benutzeroberfläche ist die Emission aus; entfernte Spieler
starten keine zusätzlichen Emitter. Nach einem Stilwechsel die Welt neu öffnen.
Andere Ressourcenpakete mit eigener `entity/player.entity.json` können den
Nebeleffekt oder ihre eigene Spieleranpassung verdrängen; die Stapelreihenfolge
und Verträglichkeit müssen mit diesen Paketen geprüft werden.

## Blattbewegung

`scripts/leaf_motion.py` erzeugt zehn Frames pro Originaltextur. Zwei mittlere
Reihenbänder folgen einander zeitversetzt nach rechts, halten kurz inne und
schwingen mit einem kürzeren Ausschlag nach links zurück. Äußere Reihen bleiben
verankert. Jede Reihe verschiebt sich um höchstens einen Pixel. Die Engine
blendet die Frames mit zehn Ticks pro Frame; der ungleichmäßige Zyklus dauert
fünf Sekunden. Eine feste, vom Texturnamen abgeleitete Startphase verteilt die
Bewegung zwischen Blattarten, während identische Texturen weiterhin dieselbe
Phase haben. Es werden keine Farben aufgehellt oder neu eingemischt: jeder
erzeugte Frame enthält dieselben RGBA-Pixel wie das Original. Die Einblendung
zwischen Frames und die Transparenzkanten müssen im Spiel auf Flimmern und
veränderte Deckung geprüft werden.

Alle 28 transparenten/undurchsichtigen Blatttexturen des festgehaltenen Stands
sind enthalten: Eiche, Fichte, Birke, Dschungel, Akazie, dunkle Eiche,
Mangrove, Azalee mit/ohne Blüten, Kirsche, blasse Eiche und drei Pappelfarben.
40 Atlaszuordnungen decken die aktuellen Namen und älteren Laubarrays ab.
Getragene Itemtexturen bleiben unangetastet. Es wird kein vollständiger
Vanilla-Atlas ersetzt. Die gemeinsame Animation gilt in allen Stilen und
beiden Qualitätsstufen, auch für dort platzierte Blattblöcke in anderen Dimensionen.

Das ist eine leichte Texturbewegung. Zweige und Baumkronen ändern ihre Geometrie
nicht, und einzelne Bäume erhalten keine individuelle Windphase. Biomtönung
einschließlich Herbst und bestehende Materialparameter bleiben erhalten.
PNG-/TGA-Referenzen stammen unverändert vom dokumentierten Mojang-Commit;
der Generator benötigt nur Python-Standardbibliotheken.

## Offene Sichtprüfung

Mit `TEST_WORLD.md` und denselben Kameras in Quality/Balanced prüfen:

1. Alle acht Gewässer bei Tageslicht und Nacht filmen: Bewegung, Reflexe und
   Abdunklung vergleichen. Die vereinbarte Näherung bei Bedarf nach Bildbelegen
   abstimmen, ohne die allgemeine Helligkeit zu ändern.
2. Halloween im Stehen, Gehen und Schwenken in erster/dritter Person betrachten.
   Weiche Schwaden, Tiefenverdeckung an Wänden und Ausblendung unter Wasser,
   beim Dimensionswechsel sowie im Inventar kontrollieren. Content-Log auf
   Molang-/Partikelfehler prüfen. Danach zu jedem anderen Stil zurückwechseln.
3. Alle Baumarten nah/fern und mit transparentem/undurchsichtigem Laub prüfen;
   auch Herbsttönung, Held-Items, Schatten und Transparenzkanten beobachten.
4. Spieleranimationen, Speer/andere Gegenstände, Rüstung, Skins und Mehrspieler
   sowie gegebenenfalls weitere Spieler-Grafikpakete prüfen. FPS messen.

## Technische Quellen

- [Bedrock-Wasserparameter](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/watercustomization?view=minecraft-bedrock-stable)
- [Partikeleffekte in Entity-Animationen](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/particlesreference/particleentityintegration?view=minecraft-bedrock-stable)
- [Partikel-Koordinatenraum](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/particlesreference/particlecomponents/minecraftemitter_local_space?view=minecraft-bedrock-stable)
- [Biomabfrage ab Format 1.21.130](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/molangreference/examples/molangconcepts/queryfunctions/query_entity_biome_has_any_identifier?view=minecraft-bedrock-stable)
- [Flipbook-Animationen](https://learn.microsoft.com/en-us/minecraft/creator/documents/createanimatedblocktexture?view=minecraft-bedrock-stable)
- [Mojang-Atlas am Referenzcommit](https://github.com/Mojang/bedrock-samples/blob/46ba6ea985fb5a92d79a9419198f10dda14c199d/resource_pack/textures/terrain_texture.json)
