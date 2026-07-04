# Ghost Track - Ghost 5

[← Torna all'indice](../../README.md)

## Sommario

- Track: Ghost Track
- Livello: Ghost 5
- Fonte appunti: `ghost_track/ghost5/notes.md`

## Obiettivo

Il livello ("The Listener") indica che l'operatore precedente (KAEL) non si fidava più dei file dopo un incidente, e ha spostato il proprio "canale di servizio" su rete: due porte, una che spiega il protocollo, l'altra che risponde solo se le si dice la parola giusta. `ss` e `netstat` sono stati resi inutilizzabili (permission denied), ma `nc` e `curl` restano disponibili. L'obiettivo è trovare il listener, leggere cosa dice, e rispondere correttamente per ottenere la password del livello successivo.

## Ricognizione

Il README lasciato nella home conferma il vincolo: niente strumenti di introspezione del kernel (`ss` dà "Permission denied"), bisogna bussare porta per porta. Una prima scansione nmap sulla sola porta di default (nessuna opzione) mostra solo SSH aperta: il servizio non è sulle porte comuni. Servono più tentativi:

- `nmap localhost::1` e `nmap ::1` falliscono per sintassi IPv6 errata; `nmap -6 ::1` conferma comunque solo SSH anche su IPv6.
- Una scansione completa `nmap -p- localhost` (tutte le 65535 porte TCP) rivela invece un intero cluster di porte alte aperte oltre a SSH.

Una successiva `nmap -sV` mirata su queste porte prova a identificare i servizi, senza riuscirci del tutto (servizi "unrecognized"), ma restituisce comunque i banner grezzi via probe, che sono la vera fonte di informazione: si scopre che una delle porte espone un banner in chiaro che spiega il protocollo applicativo, mentre un'altra è il "secure channel" che risponde solo a token valido.

## Tecnica

La tecnica centrale è l'enumerazione completa delle porte (`-p-`) quando una scansione di default non trova nulla di interessante — i servizi custom di livello CTF spesso girano su porte alte non standard, fuori dai default di nmap. Una volta identificato il cluster di porte, la seconda tecnica è la sonda manuale via `nc` per leggere i banner applicativi: il probe di nmap stesso, restituendo i fingerprint SF- non riconosciuti, rivela già in chiaro il contenuto dei banner senza bisogno di connettersi manualmente. Uno dei servizi è puramente informativo e annuncia un token di autenticazione fisso da inviare al "secure channel"; quest'ultimo, se il token è corretto, restituisce la credenziale del livello. Si tratta quindi di un semplice protocollo di "annuncio + autenticazione a token noto" distribuito su due porte separate, pensato per essere scoperto solo tramite scansione approfondita e lettura attenta dei banner.

Nota collaterale: durante la scansione compare anche un servizio con un banner "CLASSIFIED — GHOST TRACK BONUS" che è un easter egg del track (messaggio narrativo, non necessario per completare il livello).

## Sfruttamento

1. Lettura del README che spiega il vincolo (niente `ss`/`netstat`) e il tipo di canale (due porte):

```bash
cat README
```

2. Scansione di default: solo SSH visibile, il listener non è su porte comuni:

```bash
nmap localhost
```

```text
PORT   STATE SERVICE
22/tcp open  ssh
```

3. Scansione completa di tutte le porte TCP, che rivela il cluster di porte alte:

```bash
nmap -p- localhost
```

```text
PORT      STATE SERVICE
22/tcp    open  ssh
<PORTE ALTE MULTIPLE>/tcp open  ...
```

4. Service/version scan mirato sulle porte trovate, che nel probe recupera anche i banner in chiaro:

```bash
nmap -sV -p <porte trovate> localhost
```

Dal fingerprint di uno dei servizi emerge il banner del canale informativo:

```text
  GHOST PROTOCOL — CHANNEL A
  ─────────────────────────────────────

  This channel is informational only.

  Authentication token: <REDACTED>
  Secure channel: port <REDACTED>

  Send the token to receive your credential.
```

5. Connessione diretta con `nc` al "secure channel" e invio del token annunciato:

```bash
nc localhost <PORT>
```

```text
AUTHENTICATE: <REDACTED>

  Credential: <REDACTED>

^C
```

Il servizio conferma il token e restituisce direttamente la credenziale del livello successivo.

## Risultato

La credenziale ottenuta interrogando il "secure channel" con il token annunciato dal canale informativo è la password per il livello successivo. Il valore letterale non è riportato qui secondo la dottrina BreachLab; il punto didattico è che un `nmap -p-` completo seguito da lettura attenta dei banner (anche dai fingerprint grezzi restituiti da `-sV`) è sufficiente a ricostruire un protocollo applicativo custom senza bisogno di reverse engineering del binario.

## Nota di pubblicazione

Questa è la versione pensata per la pubblicazione su GitHub secondo la dottrina BreachLab (Writeups · Creators): il metodo è spiegato per intero, ma numeri di porta specifici, token e credenziale finale sono stati sostituiti con placeholder per non fornire scorciatoie a chi non ha ancora risolto il livello.

---

## Crediti

Livello risolto su BreachLab (https://breachlab.org), Ghost Track. Credito al progetto BreachLab per la piattaforma di training.
