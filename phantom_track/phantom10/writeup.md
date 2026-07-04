# Phantom Track - Phantom 10

## Sommario

- Track: Phantom Track
- Livello: Phantom 10 ("The Harvest")
- Fonte appunti: `phantom_track/phantom10/notes.md`

## Obiettivo

Il briefing parte da un presupposto interessante: si è già root sulla macchina, ma "root su una macchina è niente" — il vero valore è ciò che quella macchina sa su altri sistemi. L'obiettivo è trovare ogni credenziale presente sull'host (password, token, chiavi, segreti) in history file, config, variabili d'ambiente, chiavi SSH, config applicative e memoria di processo. Una di queste è la flag del livello.

## Ricognizione

Partendo dalla home condivisa, si osserva che, oltre alle home dei vari account standard (tutte con permessi ristretti, illeggibili), esistono account di servizio con home leggibili e permessi più larghi. I nomi e i permessi più aperti li rendono bersagli naturali: gli account di servizio tendono ad accumulare credenziali per l'integrazione con altri sistemi (database, storage cloud, altri host).

## Tecnica

Questo livello è un esercizio di **credential harvesting su un host già compromesso**: dopo aver ottenuto root (o comunque accesso), il vero obiettivo diventa trovare tutte le tracce di credenziali lasciate in giro da configurazioni, cronologie di shell e file applicativi, per usarle come trampolino verso altri sistemi (pivoting). Le fonti classiche sono:

- **File di history della shell** (`.bash_history`): spesso contengono comandi con password in chiaro passate come argomenti, perché l'operatore ha digitato la password direttamente sulla riga di comando invece di usare prompt interattivi o variabili d'ambiente.
- **Directory di configurazione cloud** (`.aws/credentials`): chiavi di accesso programmatico ai servizi cloud.
- **File `known_hosts` di SSH**: rivelano quali altri host sono stati contattati (utile per la mappa della rete, anche se non contengono credenziali dirette).
- **File di configurazione applicativa** (`.env` di una webapp): spesso contengono variabili con segreti in chiaro.

Un dettaglio operativo importante: alcune credenziali incontrate durante l'enumerazione sono **esche/valori placeholder**, non segreti reali (ad esempio access key che corrispondono ai valori di esempio standard usati nella documentazione ufficiale di provider cloud) — un promemoria che non tutto ciò che sembra una credenziale nella history è sfruttabile, e va sempre validato.

## Sfruttamento

1. Enumerazione della home condivisa per identificare account di servizio con permessi più permissivi rispetto agli account standard:

```bash
ll /home
```

2. Ingresso nella home di un account di servizio e lettura della sua `.bash_history`, leggibile dal gruppo dell'utente corrente:

```bash
cd <account_servizio>/
cat .bash_history
```

La history rivela comandi con credenziali in chiaro passate come argomenti, riferimenti SSH ad altri host interni, e token/API key che vanno verificati per autenticità.

3. Controllo di eventuali cartelle di configurazione cloud per credenziali:

```bash
cd .aws/
cat credentials
```

Se i valori trovati corrispondono ai placeholder standard della documentazione ufficiale del provider cloud, sono un'esca, non una credenziale reale sfruttabile.

4. Enumerazione di tutti i `known_hosts` presenti sul sistema, per mappare quali altri host sono stati contattati via SSH (utile per capire la topologia della rete anche senza ottenere credenziali dirette):

```bash
find / -name "known_hosts" -exec cat {} \; 2>/dev/null
```

5. Quando l'enumerazione delle fonti classiche non produce subito il risultato, una ricerca testuale mirata sull'intero filesystem con un pattern noto (ad esempio un prefisso ricorrente nelle flag del lab) può individuare rapidamente file di configurazione applicativa altrimenti trascurati:

```bash
find / -exec grep -r "<pattern_noto>" {} \; 2>/dev/null
```

## Risultato

La flag del livello era in realtà un valore di configurazione (variabile di ambiente di tipo credenziale database) definito in un file `.env` di una webapp interna, non tra le credenziali più "ovvie" trovate nella history o nelle config cloud (che si sono rivelate in gran parte esche). Il valore letterale non viene riportato in questa versione.

## Nota di pubblicazione

Questa è la versione pensata per la pubblicazione su GitHub, in conformità con la dottrina BreachLab: insegna il metodo (enumerazione sistematica delle fonti classiche di credential harvesting, distinzione tra credenziali reali ed esche, ricerca testuale mirata come tecnica di fallback) senza riportare percorsi, nomi di host o valori letterali specifici del lab.

## Crediti

Livello e piattaforma: BreachLab (breachlab.org) — Phantom Track. Se questo writeup genera revenue, parte del ricavato va devoluta secondo la dottrina "if it earns, give back" di BreachLab.
