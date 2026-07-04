# Ghost Track - Ghost 18

## Sommario

- **Track:** Ghost
- **Livello:** 18 → 19 ("Wrong User")
- **Fonte appunti:** `ghost_track/ghost18/notes.md`
- **Variante:** censored

## Obiettivo

Recuperare la password dell'utente `ghost19` per poter accedere al livello successivo. Il brief indica che sul sistema esiste un binario che gira con i privilegi di un altro operatore: va trovato, va letto il suo bit setuid, e va sfruttato per far leggere a lui il segreto al posto nostro.

## Ricognizione

Il punto di partenza è un'enumerazione classica dei binari con bit SUID e SGID impostato, per capire quali eseguibili sul sistema possono girare con l'identità del proprietario del file invece che con quella dell'utente che li lancia:

```bash
find / -perm -4000 -type f 2>/dev/null
find / -perm -2000 -type f 2>/dev/null
```

Tra i risultati SUID compaiono binari di sistema attesi (`su`, `mount`, `umount`, `newgrp`, `ssh-keysign`, `dbus-daemon-launch-helper`) ma anche due binari non standard, non presenti su un sistema Linux "di base".

## Tecnica

La tecnica è l'abuso di un binario SUID di proprietà di un altro utente (`ghost19`). Incrociando la lista dei SUID con la lista dei file posseduti da `ghost19`, emerge un binario che è al tempo stesso l'unico file posseduto da quell'utente **ed** è marcato SUID. Questo lo rende il vettore naturale: eseguendolo, il processo assume l'EUID di `ghost19`, quindi qualunque logica di lettura file incorporata nel binario opera con i suoi permessi, non con quelli dell'operatore corrente.

## Sfruttamento

1. Enumerazione dei binari SUID/SGID sul filesystem:

```bash
find / -perm -4000 -type f 2>/dev/null
```

Tra i risultati compaiono, oltre ai binari di sistema attesi, due binari custom sotto `/usr/local/bin/`.

2. Enumerazione dei file posseduti specificamente dall'utente target, per restringere il campo a ciò che gli appartiene:

```bash
find / -user ghost19 -type f 2>/dev/null
```

3. Intersezione delle due liste (SUID **e** di proprietà di `ghost19`) per identificare univocamente il binario vulnerabile:

```bash
find / -user ghost19 -perm -4000 -type f 2>/dev/null
```

4. Esecuzione del binario individuato. Girando con l'EUID di `ghost19`, il programma è in grado di leggere materiale altrimenti inaccessibile all'operatore corrente e restituisce la credenziale del prossimo account:

```bash
<REDACTED_FLAG>
```

## Risultato

Sfruttando il binario SUID di proprietà di `ghost19` è stata ottenuta la password per l'account successivo (`<REDACTED>`), utile per il login SSH e il proseguimento al Level 19.

## Nota di pubblicazione

Questa è la versione destinata alla pubblicazione su GitHub, in linea con la dottrina BreachLab (Writeups · Creators): il metodo — enumerazione dei bit SUID, correlazione per proprietario, abuso del binario per leak di credenziali — è spiegato per intero; il valore letterale della password ottenuta è stato rimosso per non fornire uno spoiler diretto ad altri operatori.

## Crediti

Livello e ambiente forniti da [BreachLab](https://breachlab.org) — Ghost Track.
