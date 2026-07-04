```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   phantom track · phile 0x01 · "suid hunter"
 ========================================================================

   target ..: phantom-01  "SUID Hunter"
   class ...: privesc / SUID wrapper · find -exec
   tools ...: find (phantom-find)
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> qualcosa gira con più privilegi del dovuto. la flag è di un altro utente
> e non la leggi. c'è una copia locale di `find` con un nome buffo in
> `/usr/local/bin` — e `find` sa fare `-exec`.

## ----[ 0x00 · intel ]----

Dal brief:

```text
MISSION: SUID Hunter
====================

Something on this system runs with more privilege than it should.
The flag belongs to another user. You cannot read it directly.

Find what has been misconfigured. Exploit it.
```

La flag è di `flagkeeper1`, non leggibile direttamente. Obiettivo: trovare
una misconfig locale che permetta di leggere file arbitrari con privilegi
non propri.

## ----[ 0x01 · recon ]----

Home (`ll`): solo dotfile e `BRIEFING`, niente. `/home`: le directory di
tutti i `flagkeeper1..8` e `phantom0..31`, quasi tutte `drwx------`.
Frugando il filesystem spunta un binario non standard:
`/usr/local/bin/phantom-find`. Un `--help` rivela che è una build di GNU
`find` (stessa sintassi, stesse opzioni). Domanda: perché una copia locale
di `find` con nome diverso in `/usr/local/bin`?

## ----[ 0x02 · il difetto ]----

La misconfig è un wrapper di `find` installato con privilegi/proprietario
elevati rispetto a chi lo lancia. `find` supporta `-exec COMMAND {} \;`,
che esegue un comando arbitrario per ogni file, sostituendo `{}` col path.

Se il processo `-exec` gira con l'identità del proprietario del binario,
qualunque comando — anche un semplice `cat` — gira con quei privilegi:
puntando il binario sulla directory bersaglio e usando `-exec cat {} \;`
si leggono file altrimenti inaccessibili.

Regola generale: qualunque binario SUID/wrapper che espone esecuzione di
comandi arbitrari (`-exec`, plugin, callback…) è di fatto un privesc
primitive — il comando iniettato eredita i privilegi del padre.

## ----[ 0x03 · exploit ]----

1. Verifica che il custom si comporti come `find`:

```bash
/usr/local/bin/phantom-find --help
```

Conferma: build di GNU findutils, `-exec` incluso.

2. `-exec cat {} \;` puntato sulla directory dell'utente bersaglio,
   sfruttando i privilegi non propri per attraversarla e leggerne i file:

```bash
/usr/local/bin/phantom-find ../flagkeeper1/ -exec cat {} \;
```

3. Lettura del contenuto sensibile prodotto dall'esecuzione privilegiata.

## ----[ 0x04 · loot ]----

`phantom-find -exec cat {} \;` sulla directory bersaglio legge file
inaccessibili e consegna la flag:

```
<REDACTED_FLAG>
```

Lezione: un wrapper che sa eseguire comandi è già una scala verso i
privilegi del suo proprietario.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · phantom track
```
