```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x0f · "ephemeral port"
 ========================================================================

   target ..: ghost-15  "Ephemeral Port"
   class ...: port scan · tls service discovery
   tools ...: nmap · openssl s_client
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> un servizio nascosto in una porta effimera, 49000-49500. parla TLS, il
> resto del range è chiuso. si scansiona, ci si collega, gli si dà del tu.

## ----[ 0x00 · intel ]----

Un operatore ha lasciato un servizio su una porta effimera nel range
49000-49500. Parla TLS, il resto è chiuso. Va trovato, ci si connette e
lo si "saluta" per ottenere la password del livello dopo.

## ----[ 0x01 · recon ]----

Il range 49000-49500 è tipico delle porte effimere assegnate
dinamicamente dal kernel: non prevedibile, va scansionato tutto. Una
scansione nmap mirata trova un'unica porta aperta, servizio "unknown".

## ----[ 0x02 · il difetto ]----

Non è HTTP/SSH standard, quindi si sonda il protocollo a mano con uno
strumento che parli TLS a basso livello. `openssl s_client` stabilisce la
connessione e mostra sia il certificato sia il traffico applicativo dopo
l'handshake — utile quando non sai ancora che gira sopra TLS. Certificato
self-signed, coerente con un servizio interno mai esposto. Dopo
l'handshake, il server manda un prompt testuale che chiede la password
corrente: servizio custom, testuale, incapsulato in TLS.

## ----[ 0x03 · exploit ]----

1. Scansione della fascia effimera:

```bash
nmap -p 49000-49500 localhost
```

```text
PORT      STATE SERVICE
<PORT>/tcp open  unknown
```

2. Connessione TLS diretta alla porta trovata:

```bash
openssl s_client -connect localhost:<PORT>
```

Handshake TLS 1.3 ok (warning atteso di self-signed), e subito:

```text
Send the current level password:
```

3. Nella stessa sessione ancora aperta si digita la password nota del
   livello corrente e invio: il servizio la valida e risponde con la
   successiva.

```text
<REDACTED>
Correct! Next password: <REDACTED>
```

## ----[ 0x04 · loot ]----

Servizio nascosto sulla porta effimera individuato, TLS puro, che dopo
l'auth restituisce la password del livello dopo (valore fuori dal
writeup). Lezione: le porte effimere non si indovinano, si scansionano
per intero.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
