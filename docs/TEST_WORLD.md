# Wiederholbare Bedrock-Abnahme

Status: Verfahren und leere Vorlagen. Eine Testwelt wurde hier noch nicht in
Minecraft erstellt oder geprüft. Dieser Leitfaden ersetzt keine Spielabnahme.

## Einmalig eine Referenzwelt festhalten

Eine eigene Testwelt in der vorgesehenen Windows-/Bedrock-Version anlegen,
Creative und Cheats für feste Tageszeit, Wetter und Kamerapositionen aktivieren.
Keine Gameplay-Add-ons oder weiteren Grafikpakete laden. Eine normale Welt mit
Küste, Fluss, Wald sowie warmen, kalten und Sumpfbiomen verwenden. Ein Seed allein
reproduziert weder Bebauung noch den Zustand bereits erzeugter Chunks.

Die folgenden Stationen einmal einrichten. Koordinaten, Kameradrehung,
Blickneigung, Biom, Tageszeit, Wetter und einen Referenzscreenshot pro Station
in einer Kopie von `test-world-scenes.csv` eintragen. Für die Bewegungsprüfung
zusätzlich Start, Ende, Dauer und Eingabemethode festhalten; die gleiche Route
vor jeder Messrunde vorladen. Fehlende Biome nicht als geprüft markieren.

| Station | Motiv und gezielte Prüfung |
|---|---|
| water-shore | Flaches Ufer bis tiefes Wasser, unter Wasser; Farbe, Sichttiefe, Caustics |
| water-motion | Offenes Meer und Objekt am Gegenüber; 30 s Standbildkamera, dann seitlich bewegen und schwenken; Flimmern, Wellen, Reflexionen |
| forest | Getöntes Laub und Horizont; Herbst und Rückwechsel zu Natürlich |
| lamps | Fackeln, Laternen, Seelenlichter und vier Materialblöcke; Helligkeit und Oberflächen bei Nacht |
| sky | Freier Horizont; Mittag, Abend, Mitternacht und Morgen, alle Himmelsrichtungen und Zenit; zusätzlich Regen |
| biome-route | Küste/Fluss, warm/kalt/Sumpf sowie Höhle/Pale Garden; Übergänge, erhaltene Vanilla-Eigenschaften und fehlende Ressourcen |

Danach Welt als `.mcworld` exportieren, Dateinamen, SHA-256, genaue Bedrock-Version
und Seed notieren. Die Welt plus ausgefüllte Szenendatei gemeinsam außerhalb des
Quellarchivs als Testmaterial verwahren, beispielsweise als Anhang des
Abnahmebelegs. Eine Änderung an Welt, Route oder Engine erhält eine neue
Weltkennung. Vergleichsaufnahmen innerhalb einer Runde immer mit derselben
Weltkopie durchführen. Eine neu angelegte Welt ohne dokumentierte Stationen ist
noch keine Referenzwelt.

## Jede Releaseprüfung

1. Commit, Namen und SHA-256 der heruntergeladenen CI-Pakete im
   [Abnahmebeleg](releases/TEMPLATE.md) erfassen. Ein lokaler Neubau ist ein
   anderes Prüfarbeitsstück. Windows, Bedrock, GPU-Treiber und alle
   Grafikeinstellungen festhalten; automatische Änderungen der Auflösung vermeiden.
2. Eine frische Kopie der Referenzwelt verwenden. Erst Vanilla Vibrant Visuals
   ohne Lumen als Vergleich aufnehmen, dann Quality und Balanced jeweils allein.
3. Je Variante Natürlich → Geheimnisvoll → Herbst → Halloween → Natürlich
   auswählen und nach jeder Änderung die Welt neu öffnen. Alle Stationen
   einschließlich Zeit-/Wettervarianten durchlaufen. Nach einem Spielneustart
   prüfen, ob die Auswahl erhalten bleibt.
4. Kamera, Tageszeit und Wetter anhand der gespeicherten Station einstellen.
   Screenshots und kurze Videos ohne Nachbearbeitung aufnehmen. Dateien nach
   `Version_Variante_Stil_Station_Zeit_Wetter` benennen; im Beleg verlinken.
   Ein Screenshot belegt weder Bewegung noch Bildrate.
5. Frischen Content-Log vor dem Import abgrenzen und nach Import, Weltstart,
   Stilwechseln und Route sichern. Fehler und Warnungen mit Zeitpunkt und
   betroffener Szene dokumentieren. Nicht pauschal nur „Log sauber“ eintragen.
6. Neuimport getrennt vom Updatepfad prüfen: Auf einer gesicherten Testwelt die
   letzte veröffentlichte Version installieren, danach den Kandidaten mit
   denselben Paket-UUIDs importieren. Sichtbare Version, gewählten Stil,
   Weltladen und Stationen prüfen. Originalwelt und Sicherung nicht überschreiben.
7. Für Leistungsangaben die drei 60-Sekunden-Runden aus
   [BENCHMARK.md](BENCHMARK.md) ausführen. Weltkennung, Szenenkennung und
   Rohmessdatei zusammen mit `benchmark.csv` verwahren. Nicht gemessene Werte
   bleiben leer. Vorversion und Kandidat unter identischen Bedingungen vergleichen.

## Entscheidung

Alle acht Kombinationen aus Variante und Stil sowie der Rückwechsel benötigen
Belege. Importfehler, nicht auflösbare Ressourcen, fehlende Texturen, störende
Himmelsnähte oder unlesbare Szenen verhindern die stabile Freigabe. Auffällige
Reflexionsabbrüche und Leistungseinbrüche mit Vergleich zur unveränderten Engine
festhalten; bekannte Enginegrenzen nicht ohne Vergleich als Paketfehler einstufen.

Offene Stationen und fehlende Messungen werden als offen eingetragen. Ohne reale
Bedrock-Abnahme bleibt ein Kandidat Entwurf oder ausdrücklich gekennzeichnete
Testversion. Historische Berichte nicht als Abnahme der neuen Dateien übernehmen.
