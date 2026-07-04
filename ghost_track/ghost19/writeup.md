# Ghost Track - Ghost 19

[← Torna all'indice](../../README.md)

## Sommario

- Track: Ghost Track
- Livello: Ghost 19 ("Your First Script")
- Fonte appunti: `ghost_track/ghost19/notes.md`

## Obiettivo

Recuperare la password per l'utente del livello successivo. Un servizio in ascolto su una porta TCP locale restituisce la password del livello successivo un pezzo alla volta, indicizzato per posizione. La consegna avverte esplicitamente di non recuperare i pezzi a mano, ma di scrivere un ciclo che li raccolga e li riassembli in ordine.

## Ricognizione

Nella home utente è presente un file di piccole dimensioni, leggibile solo dal proprietario, che lascia intuire che il segreto finale sia corto. Il vero canale di consegna è però un servizio TCP locale: inviandogli una richiesta apposita è possibile chiedere quanti "pezzi" compongono il segreto, e poi richiederli singolarmente per indice.

## Tecnica

Il servizio implementa una API testuale molto semplice su netcat: un comando speciale restituisce il numero totale di pezzi in cui è stata frammentata la password successiva; un secondo comando, parametrizzato con l'indice, restituisce il carattere o blocco corrispondente a quella posizione. Recuperare i pezzi uno per uno a mano sarebbe lento e soggetto a errori — l'approccio corretto è automatizzare la richiesta con un ciclo shell (`for`/`seq`) che interroga il servizio per ogni indice dal minimo al conteggio ottenuto, concatenando l'output per ricostruire il segreto completo.

## Sfruttamento

1. Richiesta del numero totale di pezzi tramite il comando dedicato del protocollo del servizio:

```bash
echo "<COMANDO_COUNT>" | nc localhost 30003
```

Il servizio risponde con il numero di pezzi totali da recuperare.

2. Ciclo automatico per interrogare il servizio per ogni indice e riassemblare l'output:

```bash
for i in $(seq 0 N); do
  echo "<COMANDO_PEZZO> $i" | nc -w 1 localhost 30003
done
```

Ogni chiamata a `nc` apre una nuova connessione, invia l'indice richiesto e riceve il pezzo corrispondente; il flag `-w 1` limita l'attesa per evitare che il ciclo si blocchi su connessioni che non chiudono lo stream.

3. Concatenando in ordine l'output di tutte le richieste si ottiene la password ricostruita pezzo per pezzo (valore omesso in questa versione pubblica).

## Risultato

Tecnica di raccolta e riassemblaggio automatizzato applicata con successo: il servizio ha restituito tutti i pezzi richiesti per indice, la cui concatenazione produce la password del livello successivo (valore omesso in questa versione pubblica).

## Nota di pubblicazione

Questa è la versione pubblicabile su GitHub secondo la dottrina BreachLab: spiega per intero il metodo (interrogazione per indice via netcat automatizzata con un ciclo shell) ma omette il nome esatto dei comandi del protocollo applicativo e la password ricostruita, per non fornire una scorciatoia a chi non ha ancora risolto il livello.

---

## Crediti

Livello risolto su BreachLab (https://breachlab.org), Ghost Track. Writeup pubblicato nel rispetto della dottrina "no spoilers" della piattaforma.
