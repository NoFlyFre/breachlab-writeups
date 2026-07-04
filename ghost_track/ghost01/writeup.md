```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x01 · "name game"
 ========================================================================

   target ..: ghost-01  "Name Game"
   class ...: recon / filesystem enum · shell quoting
   tools ...: ls · cat
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> nomi di file scelti apposta per farti desistere. un `MANIFEST` che fa
> il narratore e un file col nome che contiene uno spazio, giusto per
> vedere se ti fermi al primo fastidio. non fermarti.

## ----[ 0x00 · intel ]----

La directory di partenza contiene file battezzati per scoraggiare
l'analista: un `MANIFEST` che si spaccia per nota "narrativa" e un
secondo file con uno spazio letterale nel nome. Il livello misura una
sola cosa: la disciplina di enumerare tutto, ostacoli cosmetici inclusi.

## ----[ 0x01 · recon ]----

Un `cat` su `MANIFEST` restituisce un messaggio in cui l'autore dichiara
apertamente di aver scelto i nomi dei file per far mollare i frettolosi.
Indizio meta chiarissimo: qui si valuta la costanza nell'enumerare una
directory, senza lasciarsi depistare da nomi strani o testo di flavor.

## ----[ 0x02 · il difetto ]----

Nessun bug software: la "vulnerabilità" è procedurale, ed è la stessa di
una recon reale — controllare ogni file, compresi quelli con nomi
anomali (spazi, caratteri speciali, nomi civetta), invece di fermarsi al
primo che sembra irrilevante. Un nome scherzoso può custodire il dato
buono.

L'unico ostacolo tecnico è di shell: un nome con lo spazio va gestito
con l'escape (`\ `) o con le virgolette, altrimenti la shell lo tratta
come due argomenti.

## ----[ 0x03 · exploit ]----

1. `cat` sul primo file: testo di flavor in prima persona dell'autore,
   che conferma il test di pazienza più che l'exploit.
2. Si prosegue l'enumerazione e salta fuori il secondo file, con lo
   spazio nel nome.
3. Lo si legge applicando il quoting corretto:

```bash
cat "nome con spazio"
# oppure
cat nome\ con\ spazio
```

## ----[ 0x04 · loot ]----

Andando oltre il file esca si arriva al valore finale, nel secondo file:
`<REDACTED_FLAG>`. Il livello premia solo chi controlla ogni file della
directory senza cedere al primo ostacolo psicologico.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
