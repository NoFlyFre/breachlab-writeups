# Ghost Track - Ghost 17

[← Torna all'indice](../../README.md)

## Sommario

- Track: Ghost Track
- Livello: Ghost 17 ("No Shell For You")
- Fonte appunti: `ghost_track/ghost17/notes.md`

## Obiettivo

L'account `ghost17` è un relay automatizzato senza shell interattiva: la sessione SSH si chiude subito dopo il login. L'obiettivo è recuperare la credenziale per il livello successivo sfruttando il fatto che il server SSH accetta ed esegue comandi one-off passati direttamente sulla riga di comando, anche se non concede un prompt interattivo.

## Ricognizione

Il primo tentativo di connessione (`ssh ghost17@... -p 2222`) restituisce il banner del livello e chiude subito la connessione: non c'è modo di ottenere un prompt bash persistente su questo account. Questo è tipico di configurazioni SSH con `ForceCommand` o shell ristrette che processano solo il comando passato inline e poi terminano la sessione.

Passando un comando esplicito come argomento SSH (`ssh host "ls"`), invece, il server lo esegue e restituisce l'output prima di chiudere — confermando che l'esecuzione "one-shot" funziona, solo la shell interattiva è disabilitata.

## Tecnica

La tecnica è l'uso del meccanismo standard di SSH per l'esecuzione remota di comandi singoli: `ssh utente@host "comando"`. Quando si passa un comando come argomento a `ssh`, il client apre una sessione, esegue esattamente quel comando sul server (bypassando qualsiasi shell interattiva di login) e restituisce stdout/stderr al client prima di chiudere la connessione. Questo è indipendente dal fatto che l'account abbia una shell interattiva assegnata o meno: se il demone SSH consente l'esecuzione di comandi, l'operazione riesce comunque.

Da qui, l'enumerazione della home directory dell'utente remoto (`ls`) e la lettura dei file trovati (`cat <file>`) permettono di raccogliere le informazioni necessarie senza mai ottenere una shell interattiva.

## Sfruttamento

1. Verifica che la sessione interattiva sia effettivamente disabilitata:

```bash
ssh ghost17@204.168.229.209 -p 2222
(ghost17@204.168.229.209) Password: 

Connection to 204.168.229.209 closed.
```

La connessione si chiude immediatamente dopo l'autenticazione, senza offrire un prompt.

2. Esecuzione di un comando singolo passato inline a `ssh`, per enumerare la home directory remota:

```bash
ssh ghost17@204.168.229.209 -p 2222 "ls"
(ghost17@204.168.229.209) Password: 
handoff
```

Viene individuato un unico elemento nella home.

3. Un tentativo di trattarlo come directory fallisce, confermando che si tratta di un file regolare:

```bash
ssh ghost17@204.168.229.209 -p 2222 "cd handoff"
(ghost17@204.168.229.209) Password: 
/bin/bash: line 1: cd: handoff: Not a directory
```

4. Lettura del contenuto del file con lo stesso approccio one-off:

```bash
ssh ghost17@204.168.229.209 -p 2222 "cat handoff"
(ghost17@204.168.229.209) Password: 
<REDACTED>
```

Il contenuto del file è la credenziale richiesta per procedere.

## Risultato

L'esecuzione di comandi SSH non interattivi (`ssh host "comando"`) contro un account privo di shell restituisce comunque l'output desiderato: la lettura del file trovato nella home espone la credenziale per il livello successivo. Il valore letterale non è incluso in questo writeup.

## Nota di pubblicazione

Questa è la versione pubblicabile su GitHub secondo la dottrina BreachLab: spiega per intero il metodo (esecuzione di comandi SSH one-off contro account senza shell interattiva), ma non riporta la password/credenziale risolutiva, in modo da preservare la sfida per gli altri operatori.

---

## Crediti

Livello risolto su BreachLab (https://breachlab.org), Ghost Track — piattaforma di training autorizzato per pentest/CTF. Rispetta le Standing Orders: nessuno spoiler di password o flag letterali.
