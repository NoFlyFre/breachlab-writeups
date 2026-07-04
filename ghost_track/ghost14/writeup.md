# Ghost Track - Ghost 14

## Sommario

- Track: Ghost Track
- Livello: Ghost 14 ("TLS Only")
- Fonte appunti: `ghost_track/ghost14/notes.md`

## Obiettivo

Recuperare la password per l'utente del livello successivo. Il livello espone un endpoint di controllo TCP che, a differenza dei livelli precedenti della stessa catena, non parla testo in chiaro: risponde solo se il client apre correttamente una sessione TLS. Un semplice `nc` verso quella porta non ottiene nulla di utile perché il socket si aspetta un ClientHello TLS, non testo grezzo.

## Ricognizione

Il servizio è raggiungibile in locale su una porta TCP dedicata. Un tentativo diretto in chiaro non produce risposta valida. La consegna del livello suggerisce esplicitamente di cercare "un CLI che parla TLS": la scelta naturale è `openssl s_client`, lo strumento a riga di comando della suite OpenSSL pensato per aprire connessioni TLS manuali verso un servizio e interagire con lo stream applicativo una volta stabilito il canale cifrato.

## Tecnica

`openssl s_client -connect host:porta` apre una connessione TCP, esegue l'handshake TLS (TLSv1.3 in questo caso) e poi espone stdin/stdout come un tunnel testuale sopra quel canale cifrato — esattamente come farebbe `nc` su un servizio in chiaro. Il certificato del servizio è self-signed, quindi OpenSSL segnala un errore di verifica, ma la connessione TLS si stabilisce comunque: l'errore è solo un avviso sulla fiducia del certificato, non un blocco della sessione.

Una volta dentro la sessione cifrata, il servizio applicativo si comporta come i "broker" dei livelli precedenti: aspetta in input la password del livello corrente e, se corretta, restituisce la password del livello successivo. La particolarità di questo livello è che l'intero scambio avviene incapsulato in TLS anziché in chiaro, quindi serve un client capace di completare l'handshake prima di poter parlare con l'applicazione.

## Sfruttamento

1. Verifica degli strumenti disponibili in locale:

```bash
openssl help
```

Conferma che `s_client` è disponibile come sotto-comando per aprire connessioni TLS lato client.

2. Prima connessione di prova per osservare l'handshake e il comportamento del servizio:

```bash
openssl s_client --connect localhost:41311
```

L'handshake TLS 1.3 si completa nonostante il certificato self-signed, il servizio invia dei Post-Handshake Session Ticket e infine chiede una password. Senza input in tempo utile, il socket si chiude con un errore SSL di EOF inatteso.

3. Invio della password del livello corrente incanalata nello stream TLS, tramite `echo` in pipe verso `openssl s_client`:

```bash
echo "<REDACTED>" | openssl s_client --connect localhost:41311
```

Dopo un nuovo handshake, il servizio legge la password inviata via stdin e la valida.

4. Il servizio risponde con la conferma e la password per il livello successivo:

```text
Send the current level password:

Correct! Next password: <REDACTED_FLAG>
```

## Risultato

Sessione TLS stabilita con successo verso il servizio di controllo tramite `openssl s_client`; password del livello corrente inviata correttamente nello stream cifrato e password del livello successivo ottenuta (valore omesso in questa versione pubblica).

## Nota di pubblicazione

Questa è la versione pubblicabile su GitHub secondo la dottrina BreachLab: spiega per intero il metodo (uso di `openssl s_client` per interagire con un servizio TLS-only) ma omette la password del livello corrente e la password/flag ottenuta come risultato, per non fornire una scorciatoia a chi non ha ancora risolto il livello.

## Crediti

Livello risolto su BreachLab (https://breachlab.org), Ghost Track. Writeup pubblicato nel rispetto della dottrina "no spoilers" della piattaforma.
