# Ghost Track - Ghost 8

[← Torna all'indice](../../README.md)

## Sommario

- Track: Ghost Track
- Livello: Ghost 8 ("Something's Running")
- Fonte appunti: `ghost_track/ghost08/notes.md`

## Obiettivo

Recuperare la password per l'utente del livello successivo. La consegna del livello indica che un operatore ha "pulito" i file e i log, e ha persino rimosso ogni argomento dai suoi processi — ma `/proc` ricorda quello che la shell dimentica: l'obiettivo è usare il filesystem virtuale `/proc` per recuperare informazioni che non sono più visibili con i metodi standard (history, file di log, argomenti dei processi in `ps`).

## Ricognizione

La home utente non contiene nulla di utile oltre ai file di configurazione shell standard. L'indizio chiave è nel banner del livello: gli argomenti dei processi sono stati ripuliti, quindi `ps aux` da solo non rivelerà segreti passati come parametri da riga di comando. Esplorando `/proc` a mano (file di sistema come `cmdline`, `keys`, `timer_list`, `interrupts`, la gerarchia `sys/`) non emerge nulla di direttamente utile — sono per lo più file di sistema vuoti o non correlati al livello.

Enumerando i processi dell'utente si individuano più istanze dello stesso demone applicativo del livello, lanciate da root con privilegi elevati e poi declassate all'utente target.

## Tecnica

La tecnica sfrutta il fatto che `/proc/<pid>/environ` espone le variabili d'ambiente con cui un processo è stato avviato, indipendentemente dal fatto che i suoi argomenti da riga di comando siano stati ripuliti o oscurati. Le variabili in `environ` sono separate da byte NUL (`\0`) anziché da newline, quindi vanno convertite con `tr '\0' '\n'` per essere leggibili. Se un segreto è stato passato al processo come variabile d'ambiente (pratica comune, e comunque non sicura, per evitare che compaia in `ps aux`), resta visibile tramite questo file finché il processo è vivo — anche se i log e la history della shell sono stati cancellati.

## Sfruttamento

1. Enumerazione dei processi correlati all'utente per identificare i PID del demone di livello:

```bash
ps aux | grep <utente>
```

Vengono individuate più istanze dello stesso processo, lanciate da root e poi eseguite come l'utente target.

2. Lettura dell'ambiente di ciascun processo tramite `/proc/<pid>/environ`, convertendo i separatori NUL in newline per leggibilità:

```bash
cat /proc/<PID>/environ | tr '\0' '\n'
```

3. Una delle istanze del processo espone una variabile d'ambiente non standard tra quelle di sistema, contenente il segreto del livello (valore omesso in questa versione pubblica). Questa variabile non fa parte dell'ambiente shell tipico (HOSTNAME, PWD, HOME, SHLVL, PATH, ecc.) ed è stata iniettata specificamente nel processo lanciato da root.

## Risultato

Password/chiave del livello successivo recuperata leggendo l'ambiente di uno dei processi del demone tramite `/proc/<pid>/environ` (valore omesso in questa versione pubblica).

## Nota di pubblicazione

Questa è la versione pubblicabile su GitHub secondo la dottrina BreachLab: spiega per intero il metodo (enumerazione dei processi e lettura di `/proc/<pid>/environ` per recuperare variabili d'ambiente non visibili tramite `ps`) ma omette il nome esatto della variabile e il suo valore, per non fornire una scorciatoia a chi non ha ancora risolto il livello.

---

## Crediti

Livello risolto su BreachLab (https://breachlab.org), Ghost Track. Writeup pubblicato nel rispetto della dottrina "no spoilers" della piattaforma.
