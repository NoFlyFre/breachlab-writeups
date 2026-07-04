```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x07 · "lost in translation"
 ========================================================================

   target ..: ghost-07  "Lost in Translation"
   class ...: encoding · layered decode
   tools ...: cat · xxd · base64 -d
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> "niente è solo una cosa". il file di trasmissione è cifpolla: strati
> di codifica uno sopra l'altro. si sbucciano nell'ordine inverso a come
> sono stati messi.

## ----[ 0x00 · intel ]----

Il livello ti dà un file di "trasmissione" con un hint esplicito: nulla
di ciò che è stato inviato è "solo una cosa". Traduzione: serve più di un
passaggio di decodifica prima che salti fuori la credenziale del
prossimo account.

## ----[ 0x01 · recon ]----

Nella home un solo file utile, poche centinaia di byte. Un `cat` mostra
qualcosa che somiglia a un dump esadecimale: offset a 8 cifre hex, coppie
di byte, colonna ASCII a destra. È la firma classica dell'output di
`xxd`.

## ----[ 0x02 · il difetto ]----

Decodifica a strati: il contenuto vero è stato prima messo in base64, poi
il risultato salvato/mostrato come dump esadecimale. Per tornare
all'originale si invertono i passaggi:

1. Leggere il dump hex per ricostruire i byte ASCII (già leggibili nella
   colonna destra di `xxd`, da leggere come stringa base64).
2. Decodificare quella stringa da base64.

Colpo di fortuna: la colonna ASCII di `xxd` è già la stringa base64 bella
pronta, non serve reinvertire i byte a mano. Resta un solo `base64 -d`.

## ----[ 0x03 · exploit ]----

1. Lettura del file, output in formato dump esadecimale:

```bash
cat transmission.dat
```

```text
00000000: <REDACTED_HEX_DUMP>
00000010: <REDACTED_HEX_DUMP>
```

2. Riconoscimento del pattern: la colonna destra è già l'ASCII dei byte a
   sinistra e forma una stringa base64 (il punto finale reso da xxd è il
   newline non stampabile).

3. Decodifica base64 della stringa ricostruita:

```bash
echo "<stringa_base64_ricostruita>" | base64 -d
```

## ----[ 0x04 · loot ]----

Dietro il doppio strato (base64 mostrato come dump hex) c'era la
credenziale in chiaro dell'account successivo (valore fuori dal
writeup). Lezione: riconoscere il formato dai suoi tratti — offset +
coppie di byte + colonna ASCII = `xxd` — e sbucciare a ritroso.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
