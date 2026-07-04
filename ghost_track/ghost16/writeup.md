```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x10 · "config drift"
 ========================================================================

   target ..: ghost-16  "Config Drift"
   class ...: diff · config drift · backdoored line
   tools ...: diff · comm
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> due snapshot giornalieri dello stesso file di credenziali. tra lunedì e
> martedì una riga è cambiata: qualcuno ha piantato una backdoor. non a
> occhio — con `diff`.

## ----[ 0x00 · intel ]----

Sull'host ci sono due snapshot giornalieri di un file di credenziali
autorizzate (`audit-mon.txt` e `audit-tue.txt`). Tra un giorno e l'altro
una riga è cambiata: una credenziale di servizio modificata di nascosto.
Il livello impone di non confrontare a occhio, ma con uno strumento di
diff automatico.

## ----[ 0x01 · recon ]----

I due file sono lo stato del sistema di auth in due momenti. L'ipotesi:
un attaccante ha alterato una singola riga per inserire una credenziale
nota, senza toccare il resto — persistenza silenziosa classica: se
nessuno confronta i backup, la modifica passa liscia.

## ----[ 0x02 · il difetto ]----

Individuazione di **configuration drift** via diff testuale. Invece di
frugare centinaia di righe a mano, `diff` confronta byte per byte e
restituisce riga e contenuto della modifica. `diff file1 file2` produce
output in formato ed (`42c42` = riga 42 cambiata), con `<` per il primo
file e `>` per il secondo. Per file ordinati, `comm` isola le righe
uniche a ciascuno.

## ----[ 0x03 · exploit ]----

1. Confronto diretto dei due snapshot:

```bash
diff audit-mon.txt audit-tue.txt
42c42
< svc_0042:ede8866d29e6eec0fb98
> svc_0042:<REDACTED>
```

2. L'output isola subito l'unica riga divergente: alla 42, l'account
   `svc_0042` aveva un valore simile a un hash/token, sostituito nello
   snapshot successivo con una stringa in chiaro — il segnale classico di
   una credenziale piantata in fretta, senza curarsi di mascherarla come
   le altre.

## ----[ 0x04 · loot ]----

Il diff isola la riga alterata: la credenziale piantata per `svc_0042` è
la password del livello dopo (valore fuori dal writeup). Lezione: il
drift tra due snapshot si trova in un comando, non con la pazienza.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
