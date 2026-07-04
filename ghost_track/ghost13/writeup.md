```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x0d · "credential broker"
 ========================================================================

   target ..: ghost-13  "Credential Broker"
   class ...: custom TCP protocol · manual socket
   tools ...: cat · nc
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> su una porta alta c'è un broker: gli dai il token corrente, se è buono
> ti dà il prossimo. niente librerie client — apri il socket e leggi il
> protocollo che ti dichiara da solo.

## ----[ 0x00 · intel ]----

Il brief: su una porta TCP alta ascolta un demone "credential broker" che
accetta il token corrente e, se valido, restituisce il successivo.
Obiettivo: la password del livello dopo. Vincolo esplicito: niente
libreria client dedicata, ci si connette e si legge il protocollo che il
servizio espone.

## ----[ 0x01 · recon ]----

Nella home un file `flag` in sola lettura con una stringa iniziale. Nome
e contesto — e il servizio lo conferma — dicono che non è la password
finale, ma il "token corrente" da presentare al broker per avere il
prossimo.

## ----[ 0x02 · il difetto ]----

Interazione diretta con un protocollo testuale custom su socket TCP,
usando un client generico (`nc`) invece di un tool dedicato. Una volta
connesso, il servizio dichiara da solo la sintassi nel banner
(`usage: RETRIEVE <current-token>`). La parte tecnica: capire che il
comando va inviato come riga di testo sul socket già aperto — non come
argomento di `nc` — e tenere la connessione aperta abbastanza da ricevere
la risposta.

## ----[ 0x03 · exploit ]----

1. Lettura del token corrente dal file nella home con `cat`.

2. Prima connessione interattiva al demone sulla porta del brief, per
   scoprire il protocollo: il banner rivela `RETRIEVE <current-token>`
   come unica sintassi valida.

3. Gli errori tipici da evitare: passare il comando come argomento a `nc`
   dà un errore di parsing; inviare il comando letterale senza sostituire
   il placeholder col token reale fa rispondere `DENIED`, e il server
   nell'errore ripete la sintassi corretta.

4. Sfruttamento: si invia `RETRIEVE` seguito dal token reale come singola
   riga sul socket, con `echo` in pipe verso `nc` e un ritardo alla
   chiusura (`nc -q <secondi>`) per dare al server il tempo di
   rispondere. Il broker accetta il token e restituisce il successivo.

## ----[ 0x04 · loot ]----

`RETRIEVE` col token valido restituisce un nuovo token, password SSH del
livello dopo: `<REDACTED_FLAG>`. Interazione manuale con protocolli TCP
testuali via netcat, senza librerie.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
