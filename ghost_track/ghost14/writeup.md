```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x0e · "tls only"
 ========================================================================

   target ..: ghost-14  "TLS Only"
   class ...: tls · manual client handshake
   tools ...: openssl s_client
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> stesso gioco dei broker precedenti, ma il socket non parla in chiaro:
> vuole un ClientHello TLS. `nc` non basta più — serve un client che
> sappia stringere la mano.

## ----[ 0x00 · intel ]----

Recuperare la password del livello dopo. L'endpoint di controllo TCP, a
differenza dei precedenti, risponde solo se il client apre correttamente
una sessione TLS. Un `nc` verso quella porta non cava un ragno dal buco:
il socket aspetta un ClientHello, non testo grezzo.

## ----[ 0x01 · recon ]----

Servizio in locale su una porta TCP dedicata. Un tentativo in chiaro non
produce risposta valida. Il brief suggerisce di cercare "un CLI che parla
TLS": la scelta naturale è `openssl s_client`, pensato per aprire
connessioni TLS manuali e interagire con lo stream applicativo una volta
stabilito il canale.

## ----[ 0x02 · il difetto ]----

`openssl s_client -connect host:porta` apre il TCP, fa l'handshake TLS
(TLSv1.3 qui) e poi espone stdin/stdout come un tunnel testuale sopra il
canale cifrato — come farebbe `nc` in chiaro. Il certificato è
self-signed, quindi OpenSSL segnala un errore di verifica, ma la
connessione si stabilisce comunque: è solo un avviso di fiducia, non un
blocco.

Dentro la sessione cifrata, il servizio si comporta come i broker
precedenti: aspetta la password del livello corrente e, se giusta,
restituisce la successiva. La differenza è che tutto viaggia dentro TLS,
quindi serve un client che completi l'handshake prima di poter parlare
con l'applicazione.

## ----[ 0x03 · exploit ]----

1. Strumenti disponibili:

```bash
openssl help
```

Conferma `s_client` come sotto-comando per connessioni TLS lato client.

2. Connessione di prova per osservare handshake e comportamento:

```bash
openssl s_client --connect localhost:41311
```

L'handshake TLS 1.3 si completa (certificato self-signed), arrivano dei
Post-Handshake Session Ticket e infine la richiesta di password. Senza
input in tempo, il socket chiude con EOF SSL inatteso.

3. Invio della password corrente nello stream, `echo` in pipe:

```bash
echo "<REDACTED>" | openssl s_client --connect localhost:41311
```

Dopo un nuovo handshake, il servizio legge la password da stdin e la
valida.

4. Risposta con la password del livello dopo:

```text
Send the current level password:

Correct! Next password: <REDACTED_FLAG>
```

## ----[ 0x04 · loot ]----

Sessione TLS stabilita con `openssl s_client`, password corrente inviata
nello stream cifrato, password successiva ottenuta (valore omesso).
Lezione: quando il servizio è TLS-only, `openssl s_client` è il tuo
netcat.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
