# Ghost Track - Ghost 4

## Sommario

- **Track:** Ghost Track
- **Livello:** Ghost 4 → 5 ("Signal in the Noise")
- **Fonte appunti:** `ghost_track/ghost4/notes.md`

## Obiettivo

KAEL ha riversato centinaia di voci di log in una directory (`vault/`), tutte con lo stesso formato apparente. Il livello avverte che una sola voce, tra centinaia, "non è come le altre" — ha un formato diverso dal resto del rumore. L'obiettivo è isolare quella voce anomala tra il rumore, senza leggere manualmente centinaia di file, e usarla per ottenere la credenziale del livello successivo.

## Ricognizione

Nella home di `ghost4` c'è una sola directory rilevante, `vault/`, che contiene circa 500 file (`record_0001` … `record_0500`), quasi tutti da 63 byte, con alcune eccezioni isolate a 48 e 42 byte. Concatenando tutto il contenuto con `cat *` si ottiene un lungo elenco di righe nel formato `[timestamp] STATUS: <hash-like>`, cioè un log di heartbeat sintetico ripetuto migliaia di volte con timestamp e valori esadecimali simil-MD5 casuali — il "rumore" del titolo.

## Tecnica

Si tratta di un caso di **needle-in-haystack su log testuali**, dove la tecnica corretta non è la lettura sequenziale ma il filtraggio per pattern con `grep` (o simili) — da cui l'hint del livello verso la documentazione di `grep` e del piping. Analizzando l'output, la stragrande maggioranza delle righe segue rigidamente il formato `[YYYY-MM-DD HH:MM:SS] STATUS: <32 caratteri esadecimali>`. Ci sono due categorie di righe anomale:

1. Alcune righe `password=<valore>` sparse nel flusso — plausibili ma **distrattori**: sono più di una (più valori diversi osservati), quindi nessuna di esse può essere "la" risposta univoca — la loro stessa molteplicità le squalifica.
2. Un'unica riga con formato radicalmente diverso, prefissata diversamente dal resto del rumore — questo è il vero segnale, poiché è l'unica entry realmente fuori pattern e presente una sola volta.

Il modo efficiente per trovarla è un filtro mirato, ad esempio `grep -v "STATUS:"` per escludere il rumore e isolare le righe residue, oppure un pattern negativo mirato, oppure ordinare le righe per lunghezza/formato.

## Sfruttamento

1. Enumerazione della home e della directory `vault/`, che rivela circa 500 record di dimensione quasi uniforme (63 byte), con poche eccezioni a 48/42 byte:

```bash
ll
total 68
...
drwx------ 2 ghost4 ghost4 20480 Jun 22 14:07 vault/
ll
total 2028
...
-rw-r--r-- 1 ghost4 ghost4    63 Jun 22 14:06 record_0001
...
-rw-r--r-- 1 ghost4 ghost4    48 Jun 22 14:07 record_0073
...
```

2. Concatenazione di tutto il contenuto della vault:

```bash
cat *
[2026-03-28 02:01:01] STATUS: f2f2ffd3bdbbd0a63ec6da711e58bbb7
[2026-03-28 02:02:02] STATUS: 4b4d0d986bdd503080cf617eb05594f7
...
```

3. Tra le migliaia di righe `STATUS:` compaiono più occorrenze isolate di righe `password=<valore>` (distrattori, valori diversi tra loro e quindi statisticamente scartabili).

4. Isolando l'unica riga con formato realmente diverso (né `STATUS:` né `password=`), si trova la credenziale reale, marcata con un prefisso distinto (es. `[CLASSIFIED] CREDENTIAL: ...`), non riportata qui.

## Risultato

Filtrando il rumore ripetitivo e scartando i distrattori multipli si isola l'unica riga realmente anomala, che contiene la credenziale per l'utente successivo della catena. Il valore non è riportato qui per rispetto della dottrina "no spoilers" di BreachLab.

## Nota di pubblicazione

Questo writeup è la versione pubblicabile su GitHub secondo la dottrina BreachLab (`RULES · OPS DOCTRINE`): insegna il metodo (filtraggio mirato di grandi volumi di log per isolare l'anomalia reale tra rumore e distrattori) senza rivelare la password/flag letterale del livello.

## Crediti

Livello e sfida a cura di **BreachLab** (https://breachlab.org) — Ghost Track.
