```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x0a · "odd token out"
 ========================================================================

   target ..: ghost-10  "Odd Token Out"
   class ...: log analysis · frequency / dedup
   tools ...: sort · uniq -u
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> due collector scrivono ogni token due volte. un outage ne ha scritto
> uno una volta sola. quello è la chiave — e non lo trovi a occhio tra
> centinaia di righe. lo trova `uniq -u`.

## ----[ 0x00 · intel ]----

Il livello ti dà `session-tokens.log`, generato da due collector che
registrano ogni token di sessione due volte. A causa di un'interruzione,
un token è stato scritto una sola volta: compare **una volta** mentre
tutti gli altri sono in coppia. Va isolato senza leggere riga per riga, e
usato come credenziale.

## ----[ 0x01 · recon ]----

`session-tokens.log` ha diverse centinaia di righe, ciascuna con un token
alfanumerico di 14 caratteri. Troppe per un controllo manuale
affidabile: serve uno strumento che deduplichi e isoli le occorrenze
singole.

## ----[ 0x02 · il difetto ]----

`sort` + `uniq` per l'analisi di frequenza su testo:

- `sort` ordina le righe e porta vicine le occorrenze duplicate — serve
  perché `uniq` lavora solo su righe adiacenti.
- `uniq -u` stampa solo le righe che compaiono **una volta**, scartando
  duplicati e ripetizioni. Isola l'elemento anomalo in un colpo, senza
  contare a mano.

`sort file | uniq -u` è lo strumento esatto per "trova l'elemento
dispari" in un set dove tutto il resto è duplicato esattamente due volte.
Pattern generale, buono per qualunque dataset con uno schema di
duplicazione atteso.

## ----[ 0x03 · exploit ]----

1. Ispezione del log:

```bash
cat session-tokens.log
```

Centinaia di token, ciascuno atteso in duplice copia salvo uno.

2. Controllo preliminare con `sort | uniq` (senza `-u`) per farsi un'idea
   del set unico rispetto al totale — passaggio di controllo, non
   risolutivo.

3. Estrazione dell'elemento che compare una volta sola:

```bash
sort session-tokens.log | uniq -u
<REDACTED>
```

Unico output: il token anomalo, con un pattern diverso dagli altri
(generato a mano durante l'outage, non dal collector).

## ----[ 0x04 · loot ]----

`sort | uniq -u` isola l'unica riga non duplicata, che è la credenziale
per il livello dopo (valore fuori dal writeup). Due comandi in pipe
battono qualunque lettura manuale.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
