# Phantom Track - Phantom 1

[← Torna all'indice](../../README.md)

## Sommario

- Track: Phantom Track
- Livello: Phantom 1 — SUID Hunter
- Fonte appunti: `phantom_track/phantom01/notes.md`

## Obiettivo

Dal BRIEFING del livello:

```text
MISSION: SUID Hunter
====================

Something on this system runs with more privilege than it should.
The flag belongs to another user. You cannot read it directly.

Find what has been misconfigured. Exploit it.
```

La flag appartiene a un altro utente (`flagkeeper1`) e non è leggibile direttamente. Obiettivo: trovare una misconfigurazione locale che permetta di leggere file arbitrari con privilegi non propri.

## Ricognizione

Enumerazione della propria home (`ll`): solo dotfile standard e il file `BRIEFING`, nulla di sfruttabile.

Enumerazione di `/home`: presenti le directory di tutti gli utenti `flagkeeper1..8` e `phantom0..31`, quasi tutte `drwx------` (non attraversabili da altri utenti), con poche eccezioni più permissive.

Durante la ricognizione del filesystem emerge un binario non standard: `/usr/local/bin/phantom-find`. Interrogandolo con `--help` si scopre che è, a tutti gli effetti, una build di GNU `find` (stessa sintassi, stesse opzioni). La domanda diventa: perché esiste una copia locale di `find` con un nome diverso in `/usr/local/bin`, invece di usare quello di sistema?

## Tecnica

La misconfigurazione è un binario "wrapper" attorno a `find` installato con privilegi/proprietario elevati rispetto all'utente che lo invoca. `find` supporta nativamente l'azione `-exec COMMAND {} \;`, che esegue un comando arbitrario per ogni file trovato, sostituendo `{}` con il path del file.

Se il processo che esegue `-exec` gira con l'identità del proprietario del binario, qualunque comando passato a `-exec` — incluso un semplice `cat` — viene eseguito con quei privilegi. Questo permette di leggere file che l'utente corrente non potrebbe aprire direttamente, puntando il binario sulla directory bersaglio e usando `-exec cat {} \;` su ogni file trovato.

Regola generale: qualunque binario SUID/wrapper che espone funzionalità di esecuzione di comandi arbitrari (qui `-exec`, ma vale per `--exec`, plugin, callback, ecc.) è di fatto un privilege escalation primitive, perché il comando iniettato eredita i privilegi del processo genitore.

## Sfruttamento

1. Identificazione del binario custom e verifica che si comporti come `find`:

```bash
/usr/local/bin/phantom-find --help
```

L'output conferma trattarsi di una build di GNU findutils, con tutte le azioni standard incluse `-exec`.

2. Uso di `phantom-find` con `-exec cat {} \;` puntato sulla directory dell'utente bersaglio, sfruttando il fatto che il binario gira con privilegi non propri per attraversare una directory altrimenti non accessibile e leggere i file al suo interno:

```bash
/usr/local/bin/phantom-find ../flagkeeper1/ -exec cat {} \;
```

Nell'esempio catturato nelle note, l'output mostra `cat` eseguito su ogni file della directory target come dimostrazione del funzionamento — la stessa tecnica applicata sulla directory corretta espone il file contenente la flag.

3. Lettura del contenuto sensibile risultante dall'esecuzione con privilegi elevati.

## Risultato

Sfruttando `phantom-find -exec cat {} \;` sulla directory dell'utente bersaglio è stato possibile leggere file altrimenti inaccessibili, ottenendo la flag del livello:

```
<REDACTED_FLAG>
```

## Nota di pubblicazione

Questa è la versione pensata per pubblicazione su GitHub, secondo la dottrina BreachLab: il metodo (individuazione del wrapper, uso di `-exec` per leggere file arbitrari con privilegi ereditati) è spiegato per intero — comandi, percorsi e nomi di binari restano in chiaro — ma il valore letterale della flag è stato rimosso. Chi legge deve rifare il ragionamento e l'exploitation per ottenerla.

---

## Crediti

Livello risolto su BreachLab — https://breachlab.org (Phantom Track). Writeup pubblicato nel rispetto delle regole della piattaforma: si insegna la tecnica, non si condivide la risposta.
