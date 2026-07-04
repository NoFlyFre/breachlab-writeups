```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   phantom track · phile 0x06 · "scheduled sins"
 ========================================================================

   target ..: phantom-06  "Scheduled Sins"
   class ...: privesc / writable cron script
   tools ...: ls /etc/cron.d · edit script · patience
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> ogni minuto gira uno script schedulato, non come root, e — sorpresa — è
> scrivibile da te. lo modifichi, il cron lo riesegue coi privilegi del
> suo proprietario, e la flag diventa leggibile.

## ----[ 0x00 · intel ]----

Il brief: ogni minuto gira qualcosa di schedulato, non da root. Obiettivo:
capire cosa, chi lo esegue, e se si può modificarlo per la flag, di
proprietà dell'utente che possiede il job. Attenzione a un dettaglio:
`/tmp` è poli-istanziato per sessione SSH, quindi un cron in un contesto
diverso scrive nel `/tmp` reale dell'host, non visibile dalla tua shell —
conta dove scrivi l'output.

## ----[ 0x01 · recon ]----

L'enumerazione dei cron di sistema rivela vari file. Oltre alla
manutenzione legittima, ci sono job commentati come "sweep" anti-leak, che
gli operatori usano per ripulire i file lasciati dai solutori. Tra questi,
la riga chiave: un job che ogni minuto esegue uno script di manutenzione
come un utente diverso da root — coerente col brief.

## ----[ 0x02 · il difetto ]----

Abuso di un cron di manutenzione eseguito da un altro utente, il cui
script è scrivibile dall'utente corrente per permessi troppo larghi (bit
setuid attivo, gruppo del solutore con write). Modificando lo script — che
il cron riesegue ogni minuto coi privilegi del proprietario originale — si
eseguono comandi arbitrari con quella identità: qui, comandi che rendono
leggibile la flag, invece del semplice cleanup originale.

## ----[ 0x03 · exploit ]----

1. Brief e ricognizione dei job in `/etc/cron.d/`: spicca un job eseguito
   ogni minuto da un utente specifico (non root), che richiama uno script
   di manutenzione.

2. Ispezione dello script: in origine cancella solo file temporanei più
   vecchi di un giorno.

3. Verifica dei permessi: scrivibile dal gruppo del solutore e con setuid
   attivo — troppo permissivo.

4. Modifica esplorativa per confermare che il cron riesegue le modifiche.

5. Modifica finale mirata: aggiunta di un comando che rende leggibile la
   flag, sfruttando la riesecuzione periodica coi privilegi del
   proprietario.

6. Attesa del tick del cron (il brief invita alla pazienza) e verifica
   ripetuta dei permessi del target, che passano da inaccessibili a
   leggibili.

7. Lettura della flag.

## ----[ 0x04 · loot ]----

Script di manutenzione modificato → rieseguito dal cron coi privilegi di
un altro utente → flag leggibile (valore fuori dal writeup:
`<REDACTED_FLAG>`). Lezione: un cron che gira come qualcun altro e ha uno
script scrivibile da te è privesc su un timer.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · phantom track
```
