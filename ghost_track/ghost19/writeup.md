```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x13 · "your first script"
 ========================================================================

   target ..: ghost-19  "Your First Script"
   class ...: scripting · TCP service · loop assembly
   tools ...: nc · for · seq
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> il segreto arriva a pezzi, uno per indice, da un servizio TCP.
> raccoglierli a mano è da masochisti: si scrive il loop.

## ----[ 0x00 · intel ]----

Recuperare la password del livello dopo. Un servizio su porta TCP locale
la restituisce un pezzo alla volta, indicizzato per posizione. Il brief
avverte di non raccogliere i pezzi a mano, ma di scrivere un ciclo che li
prenda e li rimetta insieme in ordine.

## ----[ 0x01 · recon ]----

Nella home un file piccolo, leggibile solo dal proprietario, che fa
intuire un segreto corto. Il vero canale è però un servizio TCP locale:
gli si chiede quanti "pezzi" compongono il segreto, poi li si richiede
uno per uno per indice.

## ----[ 0x02 · il difetto ]----

Il servizio è una API testuale su netcat: un comando restituisce il
numero totale di pezzi, un secondo comando (con l'indice) restituisce il
pezzo in quella posizione. Farlo a mano è lento e sbagliabile —
l'approccio giusto è un ciclo shell (`for`/`seq`) che interroga per ogni
indice dal minimo al totale, concatenando l'output per ricostruire il
segreto.

## ----[ 0x03 · exploit ]----

1. Numero totale di pezzi tramite il comando dedicato:

```bash
echo "<COMANDO_COUNT>" | nc localhost 30003
```

2. Ciclo automatico su tutti gli indici, riassemblando:

```bash
for i in $(seq 0 N); do
  echo "<COMANDO_PEZZO> $i" | nc -w 1 localhost 30003
done
```

Ogni `nc` apre una connessione, invia l'indice e riceve il pezzo; `-w 1`
limita l'attesa per non bloccare il ciclo su stream che non chiudono.

3. Concatenando in ordine si ottiene la password ricostruita (valore
   omesso).

## ----[ 0x04 · loot ]----

Il servizio restituisce tutti i pezzi per indice; la loro concatenazione
è la password del livello dopo (valore omesso). "Your First Script": il
punto è proprio automatizzare invece di sudare a mano.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
