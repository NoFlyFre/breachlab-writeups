```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x06 · "ghost in the machine"
 ========================================================================

   target ..: ghost-06  "Ghost in the Machine"
   class ...: secret leak · env vars · base64
   tools ...: cat · base64 -d
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> KAEL ha smesso di scrivere segreti su disco, convinto che la shell
> "dimentichi". la shell non dimentica: `.bashrc` è persistente, e quattro
> `export` in base64 se ne stanno lì a chiacchierare.

## ----[ 0x00 · intel ]----

L'idea del livello: le variabili d'ambiente e la config persistita in
file come `.bashrc` sono un posto comune — e trascurato — dove finiscono
credenziali in chiaro o codificate. Serve trovare e decodificare quella
giusta per il livello dopo.

## ----[ 0x01 · recon ]----

La home di `ghost6` sembra pulita: solo i dotfile standard
(`.bash_logout`, `.bashrc`, `.profile`) e una cache vuota. Il punto
debole è `.bashrc`: tra variabili "di sistema" plausibili (build id, log
level, region…) nasconde quattro `export` con valore in Base64.

## ----[ 0x02 · il difetto ]----

Secret leak via variabili d'ambiente persistite in un file di config
della shell, più offuscamento debole in Base64 (che non è cifratura: è
codifica reversibile, senza chiave). Il metodo:

1. Riconoscere il pattern Base64 (alfanumerico + `+`, `/`, padding `=`).
2. Decodificare ogni candidato con `base64 -d`.
3. Distinguere la credenziale vera dai distrattori — valori etichettati
   esplicitamente come "non reali" sono depistaggio.

## ----[ 0x03 · exploit ]----

1. Enumerazione della home: nessun file anomalo, solo dotfile.

```bash
ll
total 48
drwx------ 1 ghost6 ghost6 4096 Jun 24 18:57 ./
...
-rw-r--r-- 1 ghost6 ghost6 4419 Jun 22 13:41 .bashrc
```

2. La cache utente è vuota, nessuna evidenza:

```bash
ll .cache/
total 12
...
-rw-r--r-- 1 ghost6 ghost6    0 Jun 22 19:11 motd.legal-displayed
```

3. Lettura di `.bashrc`: dopo le variabili innocue, quattro `export` in
   Base64:

```bash
cat .bashrc
...
export TRACE_SALT=<REDACTED_B64>
export API_DIGEST=<REDACTED_B64>
export RUNTIME_TOKEN=<REDACTED_B64>
export CACHE_SEED=<REDACTED_B64>
```

4. Decodifica di ciascun valore con `base64 -d`. Tre su quattro sono
   distrattori (il contenuto stesso dichiara di non essere una
   credenziale reale). Quello associato a `API_DIGEST` è la credenziale
   buona.

## ----[ 0x04 · loot ]----

Decodificate le quattro variabili e scartati i distrattori, resta la
credenziale per l'utente successivo (valore fuori dal writeup). Lezione:
Base64 non protegge niente, e `.bashrc` è tra i primi posti da leggere.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
