```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x00 · "first contact"
 ========================================================================

   target ..: ghost-00  "First Contact"
   class ...: recon / filesystem enum · OPSEC leak
   tools ...: ls · cat
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> primo contatto. nessun exploit, nessun trucco: solo una home da
> guardare bene. qualcuno prima di te ha lasciato appunti, e — nonostante
> si sia raccomandato di non farlo — anche le password accanto.

## ----[ 0x00 · intel ]----

Livello d'ingresso del Ghost Track. L'unica missione è la ricognizione
della home assegnata: cercare file lasciati sul sistema che portino
avanti la catena — credenziali, note operative, riferimenti ad altri
file. La regola d'oro dell'attaccante: prima di lanciare qualunque tool,
guardati intorno.

## ----[ 0x01 · recon ]----

Nella home c'è `notes.txt`, appunti operativi lasciati da un altro
operatore (KAEL). Descrivono un target di rete fittizio e un metodo di
lavoro (recon passiva, niente scan attivi), e soprattutto un promemoria:
le credenziali stanno separate in una cartella `archive/`, con tanto di
nota "non salvare password in chiaro nelle note".

Peccato che, ispezionando la stessa directory, accanto alle note ci sia
anche un file `credentials`.

## ----[ 0x02 · il difetto ]----

Non c'è vulnerabilità software: il difetto è puramente operativo, un
OPSEC failure. Un file di credenziali lasciato accanto alle note, in
barba all'avvertimento scritto nelle note stesse. La lezione è doppia: i
segreti non vanno mai in chiaro insieme alla documentazione, e da
attaccante la prima mossa è sempre `ls` / `cat` su tutto il raggiungibile.

## ----[ 0x03 · exploit ]----

Lettura delle note nella home:

```bash
cat notes.txt
```

```text
OPERATIONAL NOTES — KAEL
========================
Target: internal network segment 10.4.x.x
Method: passive recon, no active scanning
Status: ongoing

Credentials filed separately in archive/.
Do not store passwords in plaintext notes.
```

Le note stesse confermano l'esistenza di un secondo file con le
credenziali — in violazione della loro stessa policy. Lo si legge:

```bash
cat credentials
```

```text
<REDACTED>
```

## ----[ 0x04 · loot ]----

Il secondo file contiene la password per ghost-01. Valore letterale
fuori dal writeup: il punto è che un `ls` / `cat` su ogni file della home
— anche su quello che sembra "solo" un promemoria — basta a chiudere il
livello.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
