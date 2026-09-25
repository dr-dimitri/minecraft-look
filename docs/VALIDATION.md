# Prüfstand 25.09.2026 · v0.4.0

## Ausgeführt

- 516 JSON-Dateien in `pack/` ohne doppelte Schlüssel oder ungültige Zahlen geparst: 108 Basisdateien und je 102 Dateien für vier Stile.
- Manifestformat 2, `pbr`, zwei unterschiedliche UUIDs, konsistente Paketversion und interne Mindestversion `[1,26,50]` kontrolliert.
- Basis und alle vier gewählten Stile jeweils mit 83 Biomdefinitionen geprüft: 78 vollständige Grafikabstimmungen und fünf Biome mit ausschließlich neuer Cubemap-Zuordnung. Eigene Grafikverweise lösen vollständig auf. Außer den Grafikverweisen und den Herbst-Laubfarben in 15 Biomen stimmen die Komponenten mit den festgehaltenen Originalreferenzen überein.
- Vier benannte Manifest-Optionen ohne Hardware-Sperre; „Natürlich“ als Standard gemäß der dokumentierten Reihenfolge. Vollständige Ressourcen je Stil, einschließlich der ursprünglichen Biomfarben beim Zurückwechseln, geprüft.
- Zahlenbereiche für Wellen, Wasserzusammensetzung, Licht und Farbkorrektur geprüft. Tageskurven sind geordnet und schließen ohne Sprung zwischen 1 und 0.
- Nicht überblendbare Parameter bleiben über Biomgrenzen gleich: Sonnenbahnversatz, aktivierte Wellen und Caustics-Einstellungen.
- Vier PNG-Farbtexturen mit gültigem PNG-Kopf und unterstützter Kanalzahl; alle Texturverweise liegen im selben Paket. Referenzdateien gegen gespeicherte SHA-256-Werte geprüft.
- Sechs registrierte RGB-Himmelsflächen mit jeweils 1024 × 1024 Pixeln; Kopien gegen die Prüfsummen der erzeugten Originalgrafik geprüft. Originalpanoramen und ausgewählte umgerechnete Flächen visuell betrachtet. Keine Nahtfreiheits- oder Rendererfreigabe.
- 17 Verhaltenstests: die bisherigen 13 Paket-/Stil-/Realismusprüfungen sowie interpolierte Tag-/Nachtkurven aller Stile, unveränderte übrige Komponenten in fünf speziellen Overworld-Biomen, Ablehnung ungültiger Cubemap-Verweise und Ablehnung eines Pakets mit fehlender Himmelsfläche.
- Beide MCPACK-Varianten werden nach dem Packen erneut geöffnet und auf CRC, Wurzelmanifest und die gewählte Wellenzahl/Abtastbreite in allen 40 Wasserdateien geprüft. Der Pakettest prüft außerdem, dass Balanced sämtliche übrigen Wasserparameter unverändert übernimmt.

## Selbstreview

Quellcode, erzeugte Ressourcen, Anleitung und Paketaufbau wurden separat nach der Umsetzung durchgesehen. Es ist ein Selbstreview, keine unabhängige Freigabe. Befunde und Entscheidungen:

- Die Cubemap-Zuordnung verlangt Biomformat mindestens `1.21.130`. Alte Dateien werden beim Erzeugen entsprechend angehoben und vom Prüfer kontrolliert.
- Himmelstexturen wirken in der gesamten Overworld. Deshalb erhalten auch die fünf zuvor nicht bearbeiteten Overworld-Biome eine explizite Nachtkurve; deren bisheriges Licht, Wasser und Nebel bleiben erhalten. Nether und Ende bleiben ausgeschlossen.
- Tageslicht darf die Galaxien nicht zusätzlich beleuchten: beide entsprechenden Beitragswerte sind null, die eigene Helligkeitskurve ist tagsüber ebenfalls null. Das Zusammenspiel mit atmosphärischer Streuung und Belichtung ist ein offener Windows-Sichttest.
- Die erste Bildvorlage zeigte nach der Projektion störende polare Streifen. Ein image_gen-Edit reduziert scharfe Strukturen an den Polen. Die Bilddateien wurden erneut exportiert und betrachtet; die projizierten Sterne bleiben teilweise gestreckt. Orientierung und sichtbare Nähte müssen weiterhin im Spiel geprüft werden.
- Der Kurventest verwendet eine Toleranz für Gleitkomma-Interpolation: rechnerische Rundungsreste von etwa 10^-18 sind kein negatives Licht in den gespeicherten JSON-Werten.

- Sonnenlicht war mit 115 Lux zur Mittagszeit für die dokumentierte Einheit erheblich zu schwach. Die neue Basis nutzt 110.000 Lux und einheitliches ACES; ein Regressionstest prüft die Größenordnung auch in den Themenstilen. Die tatsächliche automatische Belichtung bleibt ein offener Sichttest.
- Teilzeichenfolgen ordneten lauwarme Meere dem tropischen Wasser und Mangroven dem kalten Klima zu. Explizite Ausnahmen/Zuordnungen beheben diese Fälle; geprüft werden die tatsächlich exportierten Biomdateien aller Stile.
- Künstlich erhöhte Stoffkonzentrationen in den Themen wurden entfernt, damit die klaren Gewässerprofile erhalten bleiben. Stile verändern Licht und Farbkorrektur.
- Die beiden Qualitätsstufen ändern nur zwei Wellenparameter. Alle 40 Wasserdateien einschließlich der vier Unterpakete werden erfasst; Caustics bleiben durchgängig gleich.
- Positive Nachtlichtwerte und gültige Wasserparameter sind kein Nachweis für Lesbarkeit, ruhige Bewegung oder fotorealistische Bildqualität. Tests und Dokumentation benennen diese Grenze ausdrücklich.

## Nicht ausgeführt

- Kein Import-/Sichttest in Minecraft für Windows; kein Test des tatsächlichen Zahnrad-Dialogs, des Ressourcen-Neuladens oder der Laubfarben im Renderer.
- Kein In-Game-Test von Galaxienhelligkeit, Tageshimmel, Wetterverdeckung, Projektionsnähten oder Würfelflächen-Orientierung. Die generierte Grafik ist ausdrücklich keine Aufnahme aus Minecraft.
- Keine visuelle Bestätigung von Wasserfarbe, Reflexionen, Bewegungsruhe, Belichtungswechseln oder Fotorealismus. Keine Testbilder aus einem anderen Renderer als Minecraft ausgegeben.
- Keine Messung auf RX 9060 XT, keine bestätigten 80 FPS und kein gemessener Vorteil der Balanced-Variante.
- Kein GitHub-Actions-Lauf; nur lokale Prüfung der Skripte und des Workflowaufbaus.
- Keine vollständige offizielle JSON-Schema- oder Enginevalidierung. Der lokale Prüfer kontrolliert die verwendeten dokumentierten Felder und Paketbeziehungen; der Minecraft-Content-Log muss bei der ersten Nutzung zusätzlich kontrolliert werden.

Vor einer als hardwareoptimiert bezeichneten Veröffentlichung sind Import, Bildwirkung und Vergleichsmessungen gemäß BENCHMARK.md auf dem Ziel-PC erforderlich.
