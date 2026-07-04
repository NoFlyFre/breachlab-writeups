# Ghost Track - Ghost 13

[← Torna all'indice](../../README.md)

## Sommario

- Track: Ghost
- Livello: Ghost 13 ("Credential Broker")
- Fonte appunti: `ghost_track/ghost13/notes.md`

## Obiettivo

Il brief del livello ("Credential Broker") indica che su una porta TCP alta è in ascolto un demone di tipo "credential broker": accetta il token corrente e, se valido, restituisce il token successivo. L'obiettivo dichiarato è recuperare la password dell'account del livello successivo. Il brief specifica esplicitamente di non usare una libreria client dedicata, ma di connettersi e leggere il protocollo che il servizio stesso espone.

## Ricognizione

Nella home directory è presente un file `flag` in sola lettura per l'utente, che contiene una stringa iniziale. Il nome del file e il contesto lasciano intendere — e il servizio lo conferma esplicitamente — che questo valore non è la password finale, ma solo il "token corrente" da presentare al broker per ottenere il prossimo.

## Tecnica

La tecnica è l'interazione diretta con un protocollo testuale custom su un socket TCP, usando un client generico (`nc`/netcat) invece di un tool o libreria dedicata. Il servizio, una volta connesso, dichiara da solo la sintassi attesa nel proprio banner (`usage: RETRIEVE <current-token>`): la parte tecnica del livello consiste nel capire che il comando va inviato come riga di testo sul socket già aperto, non come argomento da linea di comando di `nc`, e che la connessione va mantenuta aperta abbastanza a lungo da ricevere la risposta prima di chiudersi.

## Sfruttamento

1. Lettura del token corrente dal file dedicato nella home directory tramite `cat`.

2. Prima connessione interattiva al demone sulla porta indicata dal brief, per scoprire il protocollo atteso: il banner del servizio rivela subito il comando `RETRIEVE <current-token>` come unica sintassi valida.

3. Alcuni tentativi mostrano gli errori comuni da evitare: passare il comando come argomento a `nc` invece che come dato sul socket produce un errore di parsing degli argomenti della shell/netcat; inviare il comando letterale senza sostituire il placeholder con il token reale produce invece una risposta `DENIED` esplicita dal server, che nel messaggio di errore ripete la sintassi corretta.

4. Sfruttamento corretto: invio del comando `RETRIEVE` seguito dal token reale come singola riga sul socket, usando `echo` in pipe con `nc` e un'opzione di ritardo alla chiusura (`nc -q <secondi>`) per dare il tempo al server di rispondere prima che la connessione venga chiusa. Il broker accetta il token corrente e restituisce il token successivo, che rappresenta la password dell'account del livello successivo.

## Risultato

L'invio corretto del comando `RETRIEVE` con il token valido al credential-broker restituisce un nuovo token, da usare come password per l'accesso SSH al livello successivo. Il valore letterale non viene riportato qui: `<REDACTED_FLAG>`. Il livello ha insegnato l'interazione manuale con protocolli TCP testuali tramite netcat, senza l'uso di librerie client dedicate.

## Nota di pubblicazione

Questo writeup è la versione pubblica (GitHub) delle note personali sul livello Ghost 13 di BreachLab. In conformità alla dottrina BreachLab (Writeups · Creators), il documento insegna il metodo — interazione manuale con un protocollo TCP testuale via netcat — ma non riporta i valori letterali dei token o della password finale, che il solutore deve ottenere in autonomia interagendo con il servizio.

---

## Crediti

Livello svolto su BreachLab (breachlab.org), Ghost Track. Credit a BreachLab per la piattaforma e il design del livello.
