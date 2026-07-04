```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x09 · "core dump"
 ========================================================================

   target ..: ghost-09  "Core Dump"
   class ...: memory forensics · core dump
   tools ...: strings
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> un agente è crashato e ha lasciato il cervello sparso su disco. i
> segreti che aveva in memoria sono finiti nel core, in chiaro. non si
> legge coi byte grezzi: si estraggono le stringhe.

## ----[ 0x00 · intel ]----

Il brief racconta di un processo agente crashato con un core dump su
disco: i segreti in memoria al momento del crash sono finiti nel dump
verbatim. L'obiettivo è estrarre il token giusto — e il brief avverte
esplicitamente di non fare `cat` sul binario, ma di usare uno strumento
per testo stampabile dentro un file binario.

## ----[ 0x01 · recon ]----

Nella home c'è un core dump di qualche KB, leggibile dal gruppo, più un
file secondario illeggibile e irrilevante. Un `cat` diretto sul core
restituisce solo binario: serve altro per tirarne fuori il testo.

## ----[ 0x02 · il difetto ]----

Estrazione di stringhe stampabili da un binario (qui un core dump) con
`strings`, poi ispezione visiva dell'output a caccia di variabili
d'ambiente o strutture riconoscibili. I core dump contengono spesso, in
mezzo a heap/stack non interpretabili, blocchi testuali chiari come le
env var del processo al momento del crash — che possono includere token
o credenziali, se il processo le teneva in variabili d'ambiente invece di
gestirle in modo più sicuro.

## ----[ 0x03 · exploit ]----

1. Enumerazione della home: salta fuori il core dump dell'agente.
2. Tentativo (fallito, come previsto) di leggerlo con `cat`: solo un blob
   binario.
3. Estrazione delle stringhe stampabili:

```bash
strings <core_dump>
```

Produce un lungo elenco: la maggior parte è rumore binario, ma tra i
frammenti emerge un blocco riconoscibile di variabili d'ambiente
dell'agente, una delle quali contiene il token di autenticazione,
marcato visivamente nell'output.

## ----[ 0x04 · loot ]----

Dalle stringhe del core, tra le env var, spunta il token dell'agente da
usare come password SSH per il livello dopo: `<REDACTED_FLAG>`. Analisi
post-mortem di un core dump per recuperare segreti rimasti in chiaro in
memoria.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
