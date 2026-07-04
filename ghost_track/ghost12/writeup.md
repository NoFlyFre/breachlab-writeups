```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   ghost track · phile 0x0c · "harvested key"
 ========================================================================

   target ..: ghost-12  "Harvested Key"
   class ...: ssh · leaked key reuse
   tools ...: ssh -i
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> niente password stavolta: una chiave privata SSH sgraffignata da un
> jump host. nessuna passphrase, e l'account target la accetta ancora.
> key reuse da manuale.

## ----[ 0x00 · intel ]----

Il livello non dà una password, dà una chiave privata SSH sottratta in
un'operazione precedente su un jump host. Obiettivo: autenticarsi come
l'utente successivo con quella chiave, dimostrando di capire l'auth SSH a
chiave pubblica.

## ----[ 0x01 · recon ]----

Nella home una cartella di loot con tre file: un memo operativo, una
chiave privata ed25519 e la pubblica corrispondente. Il memo dice tutto:
la chiave viene dall'account SSH di un servizio di automazione su un jump
host, non ha passphrase, ed è ancora accettata dall'account target.

Due dettagli d'oro: usabile subito (niente passphrase da craccare), e il
target ha ancora la pubblica corrispondente in `authorized_keys`, perché
veniva da un account di servizio con accesso legittimo a più host dallo
stesso jump host.

## ----[ 0x02 · il difetto ]----

Caso da manuale di **key reuse**: una chiave pensata per un account di
automazione, trovata su un sistema compromesso, vale anche per un account
diverso su un host diverso. Nel mondo reale succede quando la stessa
chiave viene distribuita a più macchine per comodità (deploy
automatizzato), senza rotazione né restrizioni per host. Chi compromette
un solo host che la detiene eredita l'accesso a tutti quelli che la
accettano.

L'auth a chiave pubblica: il client firma una sfida con la privata, il
server verifica con la pubblica in `~/.ssh/authorized_keys`. Nessuna
password se la privata è valida e senza passphrase.

## ----[ 0x03 · exploit ]----

1. Enumerazione della home e della cartella di loot:

```bash
ll
total 40
...
-rw-r--r-- 1 <user> <user>  113 Jun 22 13:41 NOTES.txt
-rw------- 1 <user> <user>  411 Jun 22 13:41 id_ed25519
-rw-r--r-- 1 <user> <user>  100 Jun 22 13:41 id_ed25519.pub
```

2. Lettura del memo: provenienza, niente passphrase, ancora fidata dal
   target.

3. La chiave privata è in formato OpenSSH standard (materiale reale fuori
   dal writeup):

```text
-----BEGIN OPENSSH PRIVATE KEY-----
<REDACTED>
-----END OPENSSH PRIVATE KEY-----
```

4. Autenticazione al target con `-i`, la chiave al posto della password:

```bash
ssh -i id_ed25519 <target_user>@<host> -p <port>
```

Host mai contattato prima → SSH chiede conferma del fingerprint (TOFU).
Accettando, la sessione si apre come l'utente target senza password.

## ----[ 0x04 · loot ]----

Accesso via chiave pubblica, senza craccare niente: la chiave era valida
e senza passphrase. Il login sblocca il livello dopo, che introduce un
servizio TCP custom con cui dialogare. Lezione: una chiave che gira su
troppe macchine è un anello che apre l'intera catena.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · ghost track
```
