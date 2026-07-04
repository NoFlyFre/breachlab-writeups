```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   phantom track · phile 0x0a · "the harvest"
 ========================================================================

   target ..: phantom-10  "The Harvest"
   class ...: credential harvesting · pivoting
   tools ...: history · .aws · known_hosts · grep
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> sei già root, e allora? root su una macchina è niente: il valore è ciò
> che quella macchina sa sulle altre. si raccolgono tutte le credenziali
> sparse — e si impara a distinguere quelle vere dalle esche.

## ----[ 0x00 · intel ]----

Il brief parte da un assunto: sei già root, ma "root su una macchina è
niente". Il valore è ciò che l'host sa su altri sistemi. Obiettivo: trovare
ogni credenziale (password, token, chiavi, segreti) in history, config, env
var, chiavi SSH, config applicative e memoria. Una di queste è la flag.

## ----[ 0x01 · recon ]----

Nella home condivisa, oltre agli account standard (home ristrette,
illeggibili), ci sono account di servizio con home leggibili e permessi
più larghi. Bersagli naturali: gli account di servizio accumulano
credenziali per l'integrazione con altri sistemi (db, storage cloud, altri
host).

## ----[ 0x02 · il difetto ]----

**Credential harvesting su host già compromesso**: il vero obiettivo è
trovare le tracce di credenziali lasciate da config, history e file
applicativi, per fare pivoting. Fonti classiche:

- **`.bash_history`** — comandi con password in chiaro passate come
  argomenti.
- **`.aws/credentials`** — chiavi di accesso cloud.
- **`known_hosts`** — quali host sono stati contattati (mappa di rete, non
  credenziali dirette).
- **`.env`** — variabili con segreti in chiaro.

Dettaglio operativo: alcune credenziali sono **esche/placeholder** (es.
access key uguali agli esempi standard della doc dei provider cloud). Non
tutto ciò che sembra una credenziale è sfruttabile: va validato.

## ----[ 0x03 · exploit ]----

1. Home condivisa, account di servizio più permissivi:

```bash
ll /home
```

2. `.bash_history` di un account di servizio (leggibile dal gruppo):

```bash
cd <account_servizio>/
cat .bash_history
```

Comandi con credenziali in chiaro, riferimenti SSH ad altri host,
token/API key da verificare.

3. Config cloud:

```bash
cd .aws/
cat credentials
```

Se i valori sono i placeholder standard della doc del provider → esca.

4. Tutti i `known_hosts` per mappare gli host contattati:

```bash
find / -name "known_hosts" -exec cat {} \; 2>/dev/null
```

5. Quando le fonti classiche non bastano, ricerca testuale mirata con un
   pattern noto (es. un prefisso ricorrente delle flag):

```bash
find / -exec grep -r "<pattern_noto>" {} \; 2>/dev/null
```

## ----[ 0x04 · loot ]----

La flag era una variabile di config (credenziale db) in un `.env` di una
webapp interna, non tra le credenziali "ovvie" della history o del cloud
(in gran parte esche). Valore fuori dal writeup. Lezione: il tesoro non è
sempre dove luccica — e metà del lavoro è scartare le esche.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · phantom track
```
