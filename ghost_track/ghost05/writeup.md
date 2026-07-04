```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x05 · "the listener"
 ========================================================================

   target ..: ghost-05  "The Listener"
   class ...: network recon / custom protocol
   tools ...: nmap · nc · curl
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> due porte, un incidente, e un tizio — KAEL — che dopo il fattaccio
> non si fida più dei file e sposta il suo "canale di servizio" sulla
> rete. `ss` e `netstat` murati (permission denied), restano solo `nc`
> e `curl`. il gioco: trovare chi ascolta, farlo parlare, e dargli la
> parola giusta per farsi sputare la password del livello dopo.

## ----[ 0x00 · intel ]----

Il livello annuncia da subito il vincolo: l'operatore precedente ha
spostato tutto su rete, su due porte. Una spiega il protocollo, l'altra
risponde solo se le dici la parola giusta. Gli strumenti di
introspezione del kernel sono stati tolti di mezzo, quindi niente
scorciatoie: si bussa porta per porta.

## ----[ 0x01 · recon ]----

Il README nella home conferma il paletto: `ss` restituisce "Permission
denied", tocca andare a mano. Una scansione nmap di default vede solo
SSH — il servizio non è sulle porte comuni.

```bash
nmap localhost
```

```text
PORT   STATE SERVICE
22/tcp open  ssh
```

Qualche tentativo IPv6 fallisce per sintassi (`nmap ::1`, `nmap localhost::1`);
`nmap -6 ::1` conferma comunque solo SSH. La svolta è la scansione
completa di tutte le 65535 porte TCP:

```bash
nmap -p- localhost
```

```text
PORT      STATE SERVICE
22/tcp    open  ssh
<PORTE ALTE MULTIPLE>/tcp open  ...
```

Un intero cluster di porte alte. Un `-sV` mirato non identifica i
servizi ("unrecognized"), ma è proprio il probe grezzo a tradirli: nei
fingerprint `SF-` c'è già il banner in chiaro. Una porta è il canale
informativo, un'altra il "secure channel" a token.

## ----[ 0x02 · il difetto ]----

Il difetto non è un bug di memoria, è di design: un protocollo custom
che si regge su due porte separate, "annuncio + autenticazione a token
noto".

La porta informativa annuncia un token fisso e ti dice esplicitamente a
quale porta mandarlo. Il secure channel, se gli passi quel token,
sputa la credenziale. Nessun reverse engineering del binario: basta un
`-p-` completo e leggere con attenzione i banner (anche quelli
recuperati di striscio dai fingerprint di `-sV`).

Nota a margine: durante la scansione spunta pure un banner
"CLASSIFIED — GHOST TRACK BONUS". È un easter egg del track, puro
sapore narrativo, non serve per chiudere il livello.

## ----[ 0x03 · exploit ]----

Leggi il README, prendi nota del vincolo e del fatto che i canali sono
due:

```bash
cat README
```

Scansione completa → cluster di porte alte (vedi 0x01). Poi `-sV` sulle
porte trovate, che nel probe recupera i banner:

```bash
nmap -sV -p <porte trovate> localhost
```

Dal fingerprint di uno dei servizi emerge il canale informativo:

```text
  GHOST PROTOCOL — CHANNEL A
  ─────────────────────────────────────

  This channel is informational only.

  Authentication token: <REDACTED>
  Secure channel: port <REDACTED>

  Send the token to receive your credential.
```

Ci si attacca a mano al secure channel e si passa il token annunciato:

```bash
nc localhost <PORT>
```

```text
AUTHENTICATE: <REDACTED>

  Credential: <REDACTED>

^C
```

Il servizio valida il token e restituisce la credenziale del livello
successivo.

## ----[ 0x04 · loot ]----

La credenziale ottenuta dal secure channel è la password del livello
dopo. Il valore letterale resta fuori dal writeup: il succo è che un
`nmap -p-` completo più una lettura attenta dei banner — anche quelli
grezzi di `-sV` — bastano a ricostruire un protocollo applicativo custom
senza toccare un disassembler.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
