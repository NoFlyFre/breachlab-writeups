```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x04 · "signal in the noise"
 ========================================================================

   target ..: ghost-04  "Signal in the Noise"
   class ...: log analysis · needle in a haystack
   tools ...: cat · grep · pipe
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> 500 file, migliaia di righe di heartbeat tutte identiche. una sola non
> è come le altre. non si legge a mano: si filtra il rumore finché resta
> solo il segnale.

## ----[ 0x00 · intel ]----

KAEL ha riversato centinaia di voci di log in `vault/`, tutte con lo
stesso formato apparente. Il livello avverte che una sola entry, tra
centinaia, "non è come le altre". L'obiettivo: isolarla senza leggere a
mano 500 file, e usarla per la credenziale del livello dopo.

## ----[ 0x01 · recon ]----

La home di `ghost4` ha una sola directory utile, `vault/`, con ~500 file
(`record_0001` … `record_0500`), quasi tutti da 63 byte, con qualche
eccezione a 48 e 42 byte. Un `cat *` restituisce un lungo elenco nel
formato `[timestamp] STATUS: <hash-like>`: heartbeat sintetici con
timestamp e valori esadecimali simil-MD5 casuali. Questo è il "rumore"
del titolo.

## ----[ 0x02 · il difetto ]----

Caso classico di **needle-in-haystack su log testuali**: la tecnica
giusta non è leggere in sequenza, è filtrare per pattern con `grep` (da
cui l'hint del livello verso `grep` e il piping). Le righe anomale sono
di due tipi:

1. Alcune `password=<valore>` sparse nel flusso — sono **distrattori**:
   ce n'è più d'una, con valori diversi, quindi la loro stessa
   molteplicità le squalifica come risposta univoca.
2. Un'unica riga con formato radicalmente diverso, con un prefisso tutto
   suo. Questo è il vero segnale: fuori pattern e presente una sola volta.

Per trovarla basta un filtro mirato: `grep -v "STATUS:"` per togliere il
rumore, un pattern negativo, o un ordinamento per formato.

## ----[ 0x03 · exploit ]----

1. Enumerazione di `vault/`: ~500 record quasi uniformi (63 byte), poche
   eccezioni a 48/42:

```bash
ll
...
drwx------ 2 ghost4 ghost4 20480 Jun 22 14:07 vault/
ll
...
-rw-r--r-- 1 ghost4 ghost4    63 Jun 22 14:06 record_0001
...
-rw-r--r-- 1 ghost4 ghost4    48 Jun 22 14:07 record_0073
...
```

2. Concatenazione del contenuto:

```bash
cat *
[2026-03-28 02:01:01] STATUS: f2f2ffd3bdbbd0a63ec6da711e58bbb7
[2026-03-28 02:02:02] STATUS: 4b4d0d986bdd503080cf617eb05594f7
...
```

3. Tra le migliaia di `STATUS:` compaiono più `password=<valore>`
   isolate — distrattori, valori diversi tra loro, statisticamente
   scartabili.

4. Isolando l'unica riga con formato davvero diverso (né `STATUS:` né
   `password=`) si trova la credenziale reale, marcata con un prefisso
   distinto (es. `[CLASSIFIED] CREDENTIAL: ...`), non riportata qui.

## ----[ 0x04 · loot ]----

Filtrato il rumore ripetitivo e scartati i distrattori multipli, resta
l'unica riga davvero anomala: la credenziale per l'utente successivo
(valore fuori dal writeup). La lezione: davanti a grandi volumi di log,
non leggere — filtra per ciò che *non* combacia col pattern.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
