# Ghost Track - Ghost 12

## Sommario

- Track: Ghost Track
- Livello: Ghost 12 → Ghost 13 ("Harvested Key")
- Fonte appunti: `ghost_track/ghost12/notes.md`

## Obiettivo

Il livello 12 non fornisce una password: fornisce una chiave privata SSH sottratta durante un'operazione precedente su un jump host. L'obiettivo dichiarato è autenticarsi come l'utente successivo della catena usando quella chiave, dimostrando la comprensione dell'autenticazione SSH a chiave pubblica.

## Ricognizione

Nella home dell'utente è presente una cartella di "loot" con tre file:

- un memo operativo in formato testo
- una chiave privata ed25519
- la chiave pubblica corrispondente

Il memo chiarisce provenienza e stato della chiave: proviene dall'account SSH di un servizio di automazione su un jump host, non è protetta da passphrase, ed è ancora accettata dall'account target.

Due dettagli chiave: la chiave è immediatamente utilizzabile (nessuna passphrase da craccare), e l'account target ha ancora la chiave pubblica corrispondente nel proprio `authorized_keys`, perché proveniva da un account di servizio che aveva accesso legittimo a più host tramite lo stesso jump host.

## Tecnica

Questo è un caso da manuale di **riutilizzo di credenziali/chiavi trapelate (credential/key reuse)**: una chiave SSH pensata per un account di automazione viene trovata su un sistema compromesso e risulta valida anche per un account diverso su un host diverso. In un contesto reale questo accade quando la stessa chiave viene distribuita a più macchine per comodità operativa (deployment automatizzato), senza rotazione o restrizioni per host. Chi compromette un solo host che detiene la chiave eredita l'accesso a tutti i sistemi che la accettano.

L'autenticazione a chiave pubblica SSH funziona così: il client dimostra di possedere la chiave privata firmando una sfida crittografica; il server verifica la firma con la chiave pubblica presente in `~/.ssh/authorized_keys`. Non è necessaria alcuna password se la chiave privata è valida e non protetta da passphrase (o se la passphrase è nota).

## Sfruttamento

1. Enumerazione della home directory e della cartella di loot, dove sono stati depositati gli artefatti recuperati dal jump host:

```bash
ll
total 40
drwx------ 1 <user> <user> 4096 Jun 22 13:41 ./
drwx------ 1 <user> <user> 4096 Jun 22 19:46 ../
-rw-r--r-- 1 <user> <user>  113 Jun 22 13:41 NOTES.txt
-rw------- 1 <user> <user>  411 Jun 22 13:41 id_ed25519
-rw-r--r-- 1 <user> <user>  100 Jun 22 13:41 id_ed25519.pub
```

2. Lettura del memo per capire provenienza e stato della chiave (nessuna passphrase, ancora fidata dall'account target).

3. Verifica del contenuto della chiave privata (formato OpenSSH standard — il materiale crittografico reale non viene riportato qui):

```text
-----BEGIN OPENSSH PRIVATE KEY-----
<REDACTED>
-----END OPENSSH PRIVATE KEY-----
```

4. Autenticazione diretta verso l'account target usando l'opzione `-i` di `ssh` per specificare la chiave privata da usare al posto della password:

```bash
ssh -i id_ed25519 <target_user>@<host> -p <port>
```

L'host non era mai stato contattato prima dal client, quindi SSH chiede conferma del fingerprint della chiave host (TOFU — trust on first use) prima di proseguire. Accettando, la connessione va a buon fine e la sessione si apre come l'utente target senza alcuna password.

## Risultato

Accesso ottenuto tramite autenticazione a chiave pubblica, senza craccare nulla: la chiave era valida e senza passphrase. Il login sblocca il livello successivo, che introduce un servizio TCP personalizzato con cui dialogare per ottenere la credenziale dell'account seguente.

## Nota di pubblicazione

Questa è la versione pensata per la pubblicazione su GitHub, in conformità con la dottrina BreachLab: insegna il metodo (identificazione e uso di una chiave SSH trapelata per credential reuse) senza riportare la chiave privata reale, gli indirizzi/porte specifici del lab o altri valori che permetterebbero di saltare direttamente alla soluzione.

## Crediti

Livello e piattaforma: BreachLab (breachlab.org) — Ghost Track. Se questo writeup genera revenue, parte del ricavato va devoluta secondo la dottrina "if it earns, give back" di BreachLab.
