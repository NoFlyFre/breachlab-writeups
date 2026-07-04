# Ghost Track - Ghost 2

[← Torna all'indice](../../README.md)

## Sommario

- Track: Ghost Track
- Livello: Ghost 2
- Fonte appunti: `ghost_track/ghost2/notes.md`

## Obiettivo

Le note di questo livello non riportano un banner di missione esplicito, ma la struttura della home (una cartella di "investigazione" con sottodirectory dedicata a piste/leads, file compartimentati) suggerisce un livello incentrato sull'enumerazione del filesystem e sulla ricerca di dati nascosti dietro documenti "esca" che dichiarano di non contenere segreti.

## Ricognizione

La home dell'utente contiene, oltre ai file di sistema standard, una cartella di investigazione con permessi ristretti (`drwxr-x---`). Al suo interno si trovano due documenti testuali e una sottocartella nascosta dedicata alle "leads" (piste), anch'essa con permessi ristretti.

I due documenti testuali si presentano come rapporti operativi ufficiali, e uno dei due dichiara esplicitamente di non contenere credenziali — un'affermazione che, in un contesto CTF, è un invito a guardare oltre, non una garanzia.

La vera pista è nella sottocartella nascosta, che contiene alcuni file dai nomi criptici con prefisso punto.

## Tecnica

La tecnica qui è enumerazione sistematica di file nascosti (dotfile) combinata con lettura critica del contesto: i documenti "ufficiali" sono deliberatamente depistanti — dichiarano l'assenza di credenziali proprio per scoraggiare ulteriori ricerche. La vera fonte del dato utile è nascosta in una sottodirectory con nome che richiama il gergo dell'intelligence, popolata da file con prefisso punto (invisibili a un semplice `ls` senza `-a`).

Il comando `cat .*` espande il glob su tutti i file che iniziano con `.` nella directory corrente, inclusi `.` e `..` stessi (da cui gli errori "Is a directory"), ma stampa comunque in sequenza il contenuto di tutti i file nascosti trovati.

## Sfruttamento

1. Enumerazione della home e identificazione della cartella con permessi ristretti che segnala dati sensibili:

```bash
ll
total 64
drwx------ 1 <user> <user> 4096 Jun 24 01:21 ./
...
drwxr-x--- 1 <user> <user> 4096 Jun 22 13:41 investigation/
```

2. Ingresso nella cartella di investigazione e lettura dei due documenti di copertura, che si rivelano privi di contenuto utile ma indicano l'esistenza di dati compartimentati altrove:

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

3. Ingresso nella sottocartella nascosta (visibile solo enumerando i file nascosti) ed espansione di tutti i dotfile presenti con un singolo comando:

```bash
cat .*
```

4. Analisi dell'output: alcuni file sono valori esca con formato simile, mentre uno dei file contiene il dato realmente rilevante, marcato con un'indicazione visiva nel proprio output.

## Risultato

Individuato il valore nascosto nell'ultimo file della sottocartella "leads" (il materiale letterale non viene riportato qui). I file precedenti sono depistaggi con formato simile ma non utilizzabili. La lezione operativa è non fidarsi delle dichiarazioni nei documenti di alto livello ("nessuna credenziale qui") e enumerare sempre i file nascosti in ogni directory raggiungibile.

## Nota di pubblicazione

Questa è la versione pensata per la pubblicazione su GitHub, in conformità con la dottrina BreachLab: insegna il metodo (enumerazione di dotfile, diffidenza verso documenti "esca") senza riportare il valore risolutivo trovato nel file finale.

---

## Crediti

Livello e piattaforma: BreachLab (breachlab.org) — Ghost Track. Se questo writeup genera revenue, parte del ricavato va devoluta secondo la dottrina "if it earns, give back" di BreachLab.
