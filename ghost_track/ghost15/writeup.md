# Ghost Track - Ghost 15

## Sommario

- Track: Ghost Track
- Livello: Ghost 15
- Fonte appunti: `ghost_track/ghost15/notes.md`

## Obiettivo

Il livello ("Ephemeral Port") indica che un operatore ha lasciato un servizio attivo su una porta effimera nel range 49000-49500. Il servizio parla TLS, il resto del range è chiuso. Bisogna trovarlo, connettersi e "salutarlo" per ottenere la password del livello successivo.

## Ricognizione

Il range indicato (49000-49500) è tipico delle porte effimere assegnate dinamicamente dal kernel, quindi non prevedibile a priori: va scansionato per intero. Una scansione mirata con nmap sul range indicato individua un'unica porta aperta, con servizio non riconosciuto ("unknown").

## Tecnica

Non essendo un servizio HTTP/SSH standard, il passo successivo è la sonda manuale del protocollo con uno strumento che parli TLS a basso livello. `openssl s_client` permette di stabilire una connessione TLS diretta e vedere sia il certificato presentato dal server sia il traffico applicativo che segue l'handshake — utile quando non si sa ancora che protocollo applicativo giri sopra TLS. Il certificato è self-signed, coerente con un servizio interno mai esposto pubblicamente. Dopo l'handshake, il server invia direttamente un prompt testuale che chiede la password del livello corrente: si tratta quindi di un servizio custom, testuale, incapsulato in TLS.

## Sfruttamento

1. Scansione della fascia di porte effimere indicata nel brief:

```bash
nmap -p 49000-49500 localhost
```

Output (unica porta aperta, porta reale omessa):

```text
PORT      STATE SERVICE
<PORT>/tcp open  unknown
```

2. Connessione TLS diretta alla porta trovata per ispezionare il servizio:

```bash
openssl s_client -connect localhost:<PORT>
```

L'handshake TLS 1.3 va a buon fine (con warning atteso di certificato self-signed), e subito dopo il completamento della connessione il servizio invia in chiaro sul canale cifrato:

```text
Send the current level password:
```

3. A quel punto è sufficiente digitare, nella stessa sessione `openssl s_client` ancora aperta, la password nota del livello corrente e premere invio: il servizio la valida e risponde con la password del livello successivo.

```text
<REDACTED>
Correct! Next password: <REDACTED>
```

## Risultato

Individuato il servizio nascosto sulla porta effimera, TLS puro, che dopo autenticazione con la password corrente restituisce la password per il livello successivo. Il valore letterale non è riportato qui secondo la dottrina BreachLab.

## Nota di pubblicazione

Questa è la versione pensata per la pubblicazione su GitHub secondo la dottrina BreachLab (Writeups · Creators): il metodo è spiegato per intero, ma password, numero di porta specifico e flag letterali sono state sostituite con placeholder per non fornire scorciatoie a chi non ha ancora risolto il livello.

## Crediti

Livello risolto su BreachLab (https://breachlab.org), Ghost Track. Credito al progetto BreachLab per la piattaforma di training.
