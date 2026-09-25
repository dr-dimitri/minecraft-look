# Prüfung auf dem Ziel-PC

Ziel: ungefähr 80 echte gerenderte Bilder pro Sekunde bei WQHD, Bildqualität hat Vorrang. Das ist noch kein bestätigtes Ergebnis. 80 FPS entsprechen durchschnittlich 12,5 ms pro Bild; einzelne lange Frames bleiben dabei wichtig.

## Vorbereitung

Minecraft-Versionsnummer, Radeon-Treiberversion, CPU, Arbeitsspeicher, Monitor-Hz und Einstellungen notieren. 16 GB Grafikspeicher sind nicht gleichbedeutend mit 16 GB Arbeitsspeicher. Hintergrundaufnahmen für den Vergleich gleich einstellen. Zusätzliche Frame-Generation zunächst deaktivieren, damit der gemessene Wert die echte Renderleistung beschreibt.

Eine Weltkopie für reproduzierbare Vergleichsrunden verwenden. Vor der eigentlichen Messung dieselbe Gegend zwei Minuten ablaufen, damit frisches Chunk-Laden die Ergebnisse weniger verfälscht. Die Tests ohne Bildratenbegrenzung durchführen; ein Ziel-Limit erst danach setzen.

## Vergleichsrunden

Jeweils dreimal denselben 60-Sekunden-Weg ablaufen und Durchschnitts-FPS, GPU-Auslastung sowie auffällige Frame-Spitzen notieren. Ein vorhandenes Radeon-Metrikoverlay kann dafür genutzt werden. CPU-/GPU-Werte nur notieren, wenn tatsächlich verfügbar.

1. Küste/Meer: viel Wasser im Bild, dann unter Wasser schauen.
2. Wald mit Blick durch Blätter: mittags und kurz vor Sonnenuntergang.
3. Dorf oder eigene Basis mit Laternen: nachts.
4. Größere eigene Bebauung: gleiche Route und Blickrichtung.

Zuerst Vanilla Vibrant Visuals ohne Lumen testen, dann Quality im Stil „Natürlich“, bei Bedarf Balanced mit demselben Stil. Zwischen Paketwechseln die Welt neu öffnen. Wetter, Tageszeit, Sichtweite und interne Renderauflösung konstant halten. Screenshots von Tageslicht, Sonnenuntergang, Nacht und Wasser helfen zusätzlich bei der Bildabstimmung.

## Stilauswahl und Bildwirkung

Bei gleicher Qualitätsstufe nacheinander Natürlich → Geheimnisvoll → Herbst → Halloween → Natürlich über das Zahnrad des aktiven Pakets wählen; nach jeder Auswahl die Welt neu öffnen. Den gewählten Stil in der Messvorlage erfassen. Prüfen:

- Alle vier Namen sind auswählbar, die Auswahl bleibt nach einem Neustart erhalten.
- Tag, Sonnenuntergang und Nacht unterscheiden sich sichtbar zwischen den Stilen; besonders in Geheimnisvoll und Halloween bleiben Wege und Hindernisse erkennbar.
- Im Wald unterscheiden sich die vom Biom getönten Blätter bei Herbst. Nach der Rückkehr zu Natürlich verschwinden diese Tönungen wieder. Fest gefärbte Blätter müssen sich nicht verändern.
- Wechsel zwischen Wald, Meer und warmen/kalten Biomen verursachen keine auffälligen Farbsprünge oder fehlenden Ressourcen. Den Content-Log auf Fehler kontrollieren.
- Für jeden Stil eine Nachtszene und eine Wasserszene mit identischem Wetter und identischer Kamera vergleichen. Gleiche Wellenwerte sind keine Garantie für identische FPS.

## Wasser-Abnahme für 0.3.0

Mit Quality + Natürlich beginnen. Die höhere Wellenqualität und die neuen Lichtwerte erfordern einen erneuten Vergleich mit 0.2.0 bei identischen Szenen. Ein Standbild zeigt weder Flimmern noch die Qualität der Bewegung.

1. Flaches Ufer bis tiefes Wasser bei Mittag betrachten: Bodenzeichnung, Übergang der Sichttiefe, natürliche Farbe und dezente Lichtmuster prüfen. Unter Wasser dürfen helle Flächen nicht zu einer strukturlosen weißen Fläche werden.
2. Meer vom Ufer aus 30 Sekunden beobachten, dann langsam seitlich gehen. Grobe Wellen und kleine Kräuselungen sollen zusammenhängend wirken; auf wiederholende Muster, Flimmern und flackernde Glanzpunkte achten.
3. Baum oder Haus am anderen Ufer spiegeln lassen und langsam schwenken. Verschwindet es aus dem Bild, können SSR-Reflexionen ausfallen: Enginegrenze dokumentieren, keine vollständige Spiegelung behaupten.
4. See, Fluss, Strand, kaltes Meer, tropisches Meer und Sumpf vergleichen. Tropisches Wasser darf klarer sein als Sumpfwasser; Flüsse dürfen sich schneller bewegen als Seen. Künstliche Becken erben das Biomprofil.
5. Sonnenuntergang, Nacht und Wechsel aus einer dunklen Höhle ins Tageslicht prüfen. Belichtung, Lesbarkeit der Umgebung und Zeichnung in hellen Wasserreflexen beurteilen; auf störende Helligkeitssprünge achten.
6. Dieselben Ansichten in den drei Themenstilen und anschließend Balanced wiederholen. Themen sollen die Stimmung ändern, klare Gewässer jedoch nicht durch zusätzliche Schwebstoffe eintrüben. Balanced soll dieselbe Wasserfarbe und Lichtstimmung behalten.

Erst nach dem Sichttest die drei Messrunden pro Szene ausführen. Die CSV bleibt bis dahin eine leere Vorlage; Wasserqualität, 80 FPS und Treiberverhalten sind lokal nicht bestätigt.

## Nachsteuern

Vor den Messrunden für 0.4.0 zusätzlich den Galaxienhimmel prüfen: Mittag → Abend → Nacht → Morgen, alle Blickrichtungen einschließlich direkt nach oben, Regen und Nebel, alle Stile und Biomwechsel. Tagsüber darf keine dunkle oder sichtbare Weltraum-Kulisse den natürlichen Himmel verdrängen. Bei Nacht auf Nähte, verzogene Sterne und eine zu helle Umgebung achten. Die Texturvorschau ist kein Nachweis für dieses Verhalten; Details in `NIGHT_SKY.md`.

- Liegt Quality in den relevanten Runden um 80 FPS und fühlt sich ruhig an: Einstellungen behalten, gewünschtes Limit setzen.
- Wenn nur Wasserszenen deutlich langsamer sind: Balanced vergleichen.
- Wenn die GPU dauerhaft stark ausgelastet ist: zuerst Sichtweite oder einzelne Engine-Effekte prüfen, danach erst Auflösung reduzieren.
- Wenn Ruckler vor allem beim Erkunden auftreten: vorbeladene Route vergleichen; nicht vorschnell Wasser-/Lichtdetails reduzieren.
- Wenn die Optik nicht passt: unveränderten Screenshot plus Uhrzeit/Wetter/Biom notieren. Keine Leistungsbehauptung allein aus einem Standbild ableiten.

Die folgende CSV ist eine leere Messvorlage. Es wurden noch keine Resultate eingetragen.
