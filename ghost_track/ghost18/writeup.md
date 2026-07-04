```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x12 · "wrong user"
 ========================================================================

   target ..: ghost-18  "Wrong User"
   class ...: privesc / SUID owned by another user
   tools ...: find
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> c'è un binario che gira coi privilegi di un altro operatore. lo trovi
> incrociando due liste, lo esegui, e lascia che sia lui a leggere il
> segreto al posto tuo.

## ----[ 0x00 · intel ]----

Recuperare la password di `ghost19`. Il brief: sul sistema c'è un binario
che gira con i privilegi di un altro utente. Va trovato, va letto il suo
bit setuid, e va sfruttato per fargli leggere il segreto per noi.

## ----[ 0x01 · recon ]----

Enumerazione classica dei binari SUID/SGID, per capire quali eseguibili
girano con l'identità del proprietario invece che di chi li lancia:

```bash
find / -perm -4000 -type f 2>/dev/null
find / -perm -2000 -type f 2>/dev/null
```

Tra i SUID ci sono i binari di sistema attesi (`su`, `mount`, `umount`,
`newgrp`, `ssh-keysign`, `dbus-daemon-launch-helper`) ma anche due binari
non standard, assenti su un Linux "di base".

## ----[ 0x02 · il difetto ]----

Abuso di un binario SUID di proprietà di un altro utente (`ghost19`).
Incrociando i SUID con i file posseduti da `ghost19` salta fuori un
binario che è al tempo stesso l'unico file suo **ed** è SUID. Vettore
naturale: eseguendolo, il processo assume l'EUID di `ghost19`, quindi
ogni lettura di file dentro il binario opera coi suoi permessi, non coi
nostri.

## ----[ 0x03 · exploit ]----

1. Enumerazione dei SUID:

```bash
find / -perm -4000 -type f 2>/dev/null
```

Oltre ai binari di sistema, due custom sotto `/usr/local/bin/`.

2. File posseduti dall'utente target, per restringere il campo:

```bash
find / -user ghost19 -type f 2>/dev/null
```

3. Intersezione (SUID **e** di `ghost19`) per isolare il binario buono:

```bash
find / -user ghost19 -perm -4000 -type f 2>/dev/null
```

4. Esecuzione: girando con l'EUID di `ghost19`, legge materiale a noi
   inaccessibile e restituisce la credenziale del prossimo account:

```bash
<REDACTED_FLAG>
```

## ----[ 0x04 · loot ]----

Il binario SUID di `ghost19` consegna la password per l'account
successivo (valore fuori dal writeup), buona per il login SSH al Level
19. Lezione: quando enumeri i SUID, chiediti sempre *di chi* sono — la
proprietà è il vettore.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
