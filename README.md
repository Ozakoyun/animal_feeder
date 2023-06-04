# Animal Feeder
[General explanaition]

## How to install
### Installation Raspberry Pi – Starten der Applikation über SSH:
Bei dieser Anleitung wird davon ausgegangen, dass der Nutzer die fertige Einheit bekommt, heißt keine Verkabelungen selbst durchführen muss und auch nicht das fertige Projekt instal-lieren muss. Die Schritte 1-3 müssen nur bei der ersten Installation oder wenn das verwende-te WLAN gewechselt wird, durchgeführt werden. Der 4. Schritt ist bei jedem Neustart not-wendig. 

1. Raspberry Pi an den Strom hängen 
Dazu sollte der offizielle USB-C (Raspberry 4596 Pi - offizielles Netzteil für Raspberry Pi 4 Model B, USB-C, 5.1V, 3A) verwendet werden um ausreichend Spannung zu garantieren.

2. Raspberry Pi mit dem lokalem WLAN verbinden
Die Konfiguration ist über den Raspberry Pi OS Desktop am unkompliziertesten. Dafür klickt man mit der linken Maustaste auf das Symbol der WLAN-Auswahlliste und wählt das ent-sprechende WLAN, das man verwenden möchte, aus. Zuletzt wird noch das Passwort zu dem WLAN eingeben, welches auch gespeichert wird. Der Raspberry Pi verbindet sich beim nächsten Mal von selbst mit dem WLAN.

3. IP-Adresse vom Raspberry Pi ermitteln
In diesem Schritt wird die Ermittlung der IP-Adresse des Raspberry Pi erklärt. In diesem Fall wird von einem lokalen Zugriff, heißt Bildschirm und Tastatur sind vorhanden, ausgegangen.
Zuerst wird in der Kommandozeile des Raspberry Pi einer der folgenden Befehle eingegeben.
	```ifconfig```
	```ip a```
	```hostname -I```

	Diese liefern eine Ausgabe, in der unter anderem die IPv4-Adressen für die Ethernet-Anschlüsse „eth0“ aufgelistet werden. Eine IP-Adresse hat meist folgende Form: "192.168.?.?". Mit dieser IP-Adresse wird eine Verbindung mittels SSH von einem anderen System aus ermöglicht.

4. Folgende Kommandos über einen SSH-Client ausführen
Als letztes werden noch die nachfolgenden Kommandos über einen SSH-Client (z.B. PuTTY) ausgeführt.
Für das erste Kommando wird die IP-Adresse (z.B. 192.168.137.127) aus Schritt 3 benötigt.
	```ssh admin@RASPERRY_PI_IP_ADRESSE```
	
	Als nächstes wird nach einem Passwort gefragt. Für den Benutzer „admin“ lautet das Pass-wort auch „admin“. Nach der Eingabe des Passworts wird mit den nachfolgenden Komman-dos in den Ordner, wo sich das Projekt befindet, gewechselt. Der Ordner wird immer nach dem „cd“ angegeben.
	```cd PycharmProjects```
	```cd animal_feeder```

	Anschließend wird die virtuelle Umgebung von Python mit dem nachfolgenden Kommando aktiviert.
	```source venv/bin/activate```

	Zuletzt wird mittels nachfolgenden Kommando der „Animal Feeder“ gestartet.
	```flask run```

Jetzt sollte der Raspberry Pi ganz normal funktionieren und es können alle Funktionen ge-nutzt werden.


### Applikation auf Raspberry Pi deployen
In dieser Anleitung wird erklärt, wie die Applikation auf einen „neuen“ Raspberry Pi geladen werden kann und weiters auch direkt am Raspberry Pi gestartet wird. Diese Anleitung wurde für die Nutzung mit dem Raspberry Pi OS als Betriebssystem geschrieben. 

1. Als ersten Schritt müssen die nachfolgenden Kommandos in der Kommandozeile ausge-führt werden.
	```sudo apt update```
	```sudo apt upgrade```

2. Als nächstes muss kontrolliert werden ob die richtigen Versionen von Python und Pip ver-wendet werden. Diese sind 3.9.2 für Python und 21.3.1 für Pip. Die Lauffähigkeit der Applikation ist nur für diese Versionen gegeben. Dazu werden die folgenden Kommandos ausgeführt.
	```python --version```
	```pip –version```

3. In diesem Schritt wird zuerst der Ordner erstellt, in dem sich das Projekt befinden soll. Da-zu wird zuerst mittels „mkdir <Verzeichnis>“ das Verzeichnis erstellt. Weiters navigiert man mit „cd <ORDNER_PFAD>“ zu dem entsprechenden Ordner. Das Projekt selbst kann mithilfe von Kommando „git clone“ in der Kommandozeile von Github heruntergeladen werden (https://github.com/Ozakoyun/animal_feeder.git) und in den entsprechenden Ordner platziert werden.

4. Als nächstes muss man mittels dem vorhin erwähnten „cd“-Kommando in den Ordner navigieren, in dem sich das Projekt befindet. Danach wird die virtuelle Umgebung von Python, mit dem nachfolgenden Kommando, installiert.
	```py -m venv venv``` 

5. Nachdem die virtuelle Umgebung von Python installiert wurde, kann diese nun mit dem nachfolgenden Kommando gestartet werden.
	```source venv/bin/activate```

6. In diesem Schritt werden nun die benötigten Bibliotheken, mit dem unteren Kommando, für das Projekt installiert.
	```pip install -r requirements.txt```

7. Zuletzt wird mithilfe des nachfolgenden Kommandos die Applikation auf dem Raspberry Pi gestartet.
	```flask run```

Fertig. Die Applikation befindet sich nun am Raspberry Pi.

## How to use
Nach der Installation können mit der Website Nahrungen und die Zeitpläne zur Fütterung verwaltet werden. Die Website besteht aus vier Registern: Home, Food, Timetable, Statistic.

### Home
Im Home-Register können manuelle Fütterungen gestartet werden. Hierfür wählt man zuerst das entsprechende Futter aus und klickt auf einen Button, um die Fütterung zu starten. Da es in diesem Projekt nur einen Futterspender zur Ausgabe gibt, kann hier keine andere ausgewählt werden.

### Food
Im Food-Register sind alle verfügbaren Futter aufgelistet. Dazu werden Daten wie die ID (automatisch), die Bezeichnung, die noch verfügbare Menge, die Portionsgröße und wann es erstellt bzw. hinzugefügt wurde gespeichert. In diesem Register können die verschiedenen Futter bearbeitet, gelöscht oder neue hinzugefügt werden.
	
### Timetable
In diesem Register werden die Zeitpläne zur automatischen Fütterung erstellt. Bei der Erstellung eines neuen Zeitplanes werden die ID (automatisch), das verwendete Futter, der Wochentag und die Zeit der Fütterung gespeichert. Fütterungen werden immer wöchentlich durchgeführt. In dem Timetable-Register können auch wieder die Zeitpläne bearbeitet, gelöscht oder neue hinzugefügt werden.

### Statistic
In diesem Register werden alle ausgeführten Fütterungen aufgelistet und auch wie viel nach der Fütterung noch von dem Futter vorhanden ist. Wenn man bei einer Fütterung auf „Details“ klickt, wird einem jede Fütterung zu dem entsprechenden Futter aufgelistet und auch in einem Liniendiagramm dargestellt.

### Löschverhalten
Das Löschverhalten passiert kaskadierend, heißt wenn ein Futter aus „Food“ gelöscht wird, werden auch alle Inhalte in dem dieses Futter vorkommt, wie die Zeitpläne und Statistiken, gelöscht. Passiert jedoch nicht, wenn ein Zeitplan gelöscht wird. Bevor jedoch eine Löschung endgültig durchgeführt wird, wird der Benutzer nochmal gefragt, ob er die Löschung wirklich vornehmen möchte.


## Notes
[any important notes]

(c) Akkoyun Ozan, Lazic Michelle, Schwarz Markus
