# Ghost Track - Ghost 20

[← Torna all'indice](../../README.md)

## Sommario

- Track: Ghost Track
- Livello: Ghost 20 ("Cron Discovery")
- Fonte appunti: `ghost_track/ghost20/notes.md`

## Obiettivo

Il livello indica che "qualcosa" viene eseguito periodicamente come root e chiede di scoprire cosa, dove scrive e cosa legge, suggerendo di cercare nei "corners" di `/etc` dedicati ai job pianificati (cron). L'obiettivo è identificare il job cron root rilevante, capire il suo comportamento e usarlo per ottenere la credenziale per il livello successivo.

## Ricognizione

L'elenco di `/etc/cron.d/` mostra, oltre ai job di sistema standard (`e2scrub_all`), due file non standard con timestamp recente. Il contenuto combinato di `/etc/cron.d/*` rivela due entry cron che girano **ogni minuto** come root, puntando a due script personalizzati in `/opt/`. Il primo di questi (`job.sh`) è il target di interesse: viene letto per capire cosa fa.

## Tecnica

La tecnica sfruttata è una **race condition su un file temporaneo scritto da un cron job root** (pattern TOCTOU — time-of-check to time-of-use). Lo schema generale di questo tipo di script è:

1. Un job root copia un contenuto protetto (leggibile solo da root) in un file temporaneo con permessi più permissivi (es. in `/var/tmp`, world-readable).
2. Attende un breve intervallo di tempo prima di cancellarlo.
3. Cancella il file temporaneo.

Il punto debole è la finestra temporale tra la scrittura del contenuto protetto nel file temporaneo e la sua cancellazione: durante quella finestra, qualunque utente locale con permessi di lettura sulla directory temporanea può leggere un contenuto che altrimenti sarebbe inaccessibile. Poiché il job cron gira ogni minuto, la finestra si ripresenta periodicamente, rendendo lo sfruttamento affidabile anche senza timing millimetrico: basta monitorare il file target in un loop di lettura stretto.

## Sfruttamento

1. Enumerazione dei job pianificati per identificare cosa gira come root:

```bash
ls -la /etc/cron.d/
```

Si notano entry non standard con timestamp recente rispetto ai job di sistema.

2. Lettura del contenuto delle crontab per capire cosa viene eseguito e con quale frequenza:

```bash
cat /etc/cron.d/*
```

Emergono job custom pianificati con cadenza `* * * * *` (ogni minuto) eseguiti come root — condizione ideale per una race condition, perché l'esecuzione si ripete costantemente.

3. Lettura dello script per capire il flusso dati (dove scrive, cosa legge, quanto dura la finestra):

```bash
cat /opt/ghost-cron/job.sh
```
```bash
#!/bin/bash
cat <REDACTED> > /var/tmp/ghost-cron-output 2>/dev/null
sleep 2
rm -f /var/tmp/ghost-cron-output
while true; do cat /var/tmp/ghost-cron-output 2>/dev/null && break; sleep 1; done
```

Emerge chiaramente una finestra temporale in cui un file world-readable in `/var/tmp` contiene un secret altrimenti non accessibile, prima di essere cancellato.

4. Sfruttando la periodicità del job (ogni minuto), è sufficiente leggere in loop il file temporaneo per catturarne il contenuto prima della cancellazione.

## Risultato

Sfruttando la finestra temporale creata dal cron job root tra scrittura e cancellazione del file temporaneo, è stato possibile leggere il secret prima della sua rimozione, ottenendo la credenziale per il livello successivo. Il valore letterale non è incluso in questo writeup.

## Nota di pubblicazione

Questa è la versione pubblicabile su GitHub secondo la dottrina BreachLab: spiega per intero il metodo (identificazione di job cron custom, analisi dello script e sfruttamento della race condition TOCTOU su file temporanei), ma non riporta il secret/password risolutivo, in modo da preservare la sfida per gli altri operatori.

---

## Crediti

Livello risolto su BreachLab (https://breachlab.org), Ghost Track — piattaforma di training autorizzato per pentest/CTF. Rispetta le Standing Orders: nessuno spoiler di password o flag letterali.
