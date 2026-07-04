# Ghost Track - Ghost 16

## Sommario

- **Track:** Ghost Track
- **Livello:** Ghost 16 → 17 ("Config Drift")
- **Fonte appunti:** `ghost_track/ghost16/notes.md`

## Obiettivo

Sull'host sono presenti due snapshot giornalieri di un file di credenziali autorizzate (`audit-mon.txt` e `audit-tue.txt`, presumibilmente dump di lunedì e martedì). Tra un giorno e l'altro una riga è cambiata: un backdoor è stato piantato modificando silenziosamente una credenziale di servizio. Il livello impone esplicitamente di non confrontare "a occhio" i due file, ma di usare uno strumento di confronto automatico.

## Ricognizione

I due file rappresentano lo stato del sistema di autenticazione in due momenti diversi. L'ipotesi è che un attaccante abbia alterato una singola riga tra i due snapshot per inserire una credenziale di servizio nota, senza toccare il resto — una tecnica classica di persistenza silenziosa: se nessuno confronta i backup, la modifica passa inosservata.

## Tecnica

Si tratta di un caso di **individuazione di configuration drift** tramite diff testuale. Anziché ispezionare manualmente centinaia di righe cercando l'anomalia, si usa `diff` per confrontare byte per byte i due snapshot e ottenere direttamente il numero di riga e il contenuto esatto della modifica. `diff file1 file2` produce un output nel formato ed (es. `42c42` = riga 42 cambiata), con `<` che indica la riga nel primo file e `>` la riga corrispondente nel secondo. In alternativa, per file ordinati, `comm` permette di isolare righe uniche a ciascun file.

## Sfruttamento

1. Confronto diretto dei due snapshot di credenziali con `diff`:

```bash
diff audit-mon.txt audit-tue.txt 
42c42
< svc_0042:ede8866d29e6eec0fb98
> svc_0042:<REDACTED>
```

2. L'output isola immediatamente l'unica riga divergente: alla riga 42, l'account di servizio `svc_0042` aveva originariamente un valore che assomiglia a un hash/token, sostituito nello snapshot successivo con una stringa in chiaro — il classico segnale di una credenziale piantata "in fretta" da chi non si è preoccupato di mascherarla come le altre.

## Risultato

Il diff isola con precisione la riga alterata, rivelando la credenziale piantata per l'account di servizio `svc_0042`, che coincide con la password del livello successivo della catena. Il valore non è riportato qui per rispetto della dottrina "no spoilers" di BreachLab.

## Nota di pubblicazione

Questo writeup è la versione pubblicabile su GitHub secondo la dottrina BreachLab (`RULES · OPS DOCTRINE`): insegna il metodo (individuazione di configuration drift tramite diff testuale) senza rivelare la password/flag letterale del livello, in modo che chi legge debba comunque eseguire l'esercizio.

## Crediti

Livello e sfida a cura di **BreachLab** (https://breachlab.org) — Ghost Track.
