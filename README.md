# PadFinder
Der FFF-Pad-Scanner sucht Stellen mit problematischen Informationen aus FFF Pads heraus, damit diese entsprechend entfernt werden können. Er basiert auf Christopher's PadFinder (https://github.com/Christ0pheri/PadFinder/tree/e6bce97cfbf51925463bceead48dd606368f3339). Ist jetzt zugegebenermaßen nicht der schönste Code der Welt, aber vielleicht trotzdem nützlich.

### Setup
Mit `pip3 install -r requirements.txt` die benötigten Pakete installieren. Idealerweise vorher noch ein virtuel environment mit venv machen, aber wenn nicht auch nicht schlimm was hier installiert wird kann eh immer gebraucht werden.

### Benutzung
Am besten ein oder mehrere Start Pads auswählen. Bei einem einzelnen kann dieses mit dem -s CLI Argument übergeben werden. Bei mehreren Pads die Namen / URLs in eine .txt Datei schreiben und diese dann mit -sf übergeben. Für gebauere Informationen einfach `python3 scanner.py --help` ausführen.

Jedes Pad wird auch nach Links zu anderen Pads durchsucht und diese dann in eine Warteschlange fürs durchsuchen nach problematischen Stellen angefügt.
Konkret wird gesucht nach:
- E-Mailadressen
- Telefonnummern
- FFF Links
- WhatsApp Links
- Hinweise auf Zugehärigkeit  zu marginalisierten Gruppen

Bei einigen Punkten gibt es relativ viel False Positives, da muss einmal manuell über das Ergebnis geguckt werden.

Die Ergebnisse werden am Ende in einer JSON Datei gespeichert.

Bei Fragen, Anmerkungen oder irgendwas mich einfach auf Twitter anschreiben unter @malikpaetzold