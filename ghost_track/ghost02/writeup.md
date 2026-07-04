```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x02 · "in the shadows"
 ========================================================================

   target ..: ghost-02  "In The Shadows"
   class ...: recon / hidden files · misdirection
   tools ...: ls -a · cat
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> "this document contains no credentials". quando un file te lo scrive
> nero su bianco, è lì che devi guardare. il dato vero non è nei report
> ufficiali: è nei dotfile della sottocartella nascosta.

## ----[ 0x00 · intel ]----

Niente banner di missione, ma la struttura parla: una cartella di
"investigazione" con permessi ristretti, documenti compartimentati e una
sottodirectory dedicata alle "leads". Livello di enumerazione del
filesystem, con dati nascosti dietro documenti esca.

## ----[ 0x01 · recon ]----

La home contiene una cartella `investigation/` con permessi `drwxr-x---`.
Dentro, due documenti testuali che si presentano come rapporti ufficiali
— uno dichiara esplicitamente di non contenere credenziali — e una
sottocartella nascosta con le "leads", anch'essa ristretta e piena di
file dal nome criptico col prefisso punto.

## ----[ 0x02 · il difetto ]----

Enumerazione sistematica dei dotfile più lettura critica del contesto. I
documenti "ufficiali" sono depistaggio deliberato: dichiarano l'assenza
di credenziali proprio per farti smettere di cercare. Il dato buono è
nella sottodirectory nascosta, in file col prefisso punto (invisibili a
un `ls` senza `-a`).

Il trucco pratico: `cat .*` espande su tutti i file che iniziano con `.`
nella directory corrente. Include anche `.` e `..` (da cui gli errori
"Is a directory"), ma stampa comunque in sequenza tutti i file nascosti.

## ----[ 0x03 · exploit ]----

1. Enumerazione della home, individuazione della cartella ristretta:

```bash
ll
total 64
drwx------ 1 <user> <user> 4096 Jun 24 01:21 ./
...
drwxr-x--- 1 <user> <user> 4096 Jun 22 13:41 investigation/
```

2. Lettura dei documenti di copertura, che si rivelano vuoti di sostanza
   ma ammettono l'esistenza di dati compartimentati altrove:

```bash
cat summary.txt
```

```text
OPERATIONAL SUMMARY
===================
Operation: GHOST WATCH
Status: Active

All active source files have been compartmentalized
and moved to a separate location.

This document contains no credentials.
```

3. Ingresso nella sottocartella nascosta ed espansione di tutti i dotfile
   con un colpo solo:

```bash
cat .*
```

4. Nell'output, alcuni file sono valori esca con formato simile; uno
   contiene il dato vero, marcato da un'indicazione visiva nel proprio
   output.

## ----[ 0x04 · loot ]----

Il valore risolutivo è nell'ultimo file della sottocartella "leads"
(fuori dal writeup). Gli altri sono depistaggi col formato simile. Morale
operativa: non fidarsi mai delle dichiarazioni dei documenti di alto
livello ("nessuna credenziale qui") ed enumerare sempre i file nascosti
in ogni directory raggiungibile.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
