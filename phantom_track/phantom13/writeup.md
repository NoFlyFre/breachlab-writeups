# Phantom Track - Phantom 13

[← Torna all'indice](../../README.md)

## Sommario

- Track: Phantom Track
- Livello: Phantom 13 ("Deep Roots")
- Fonte appunti: `phantom_track/phantom13/notes.md`

## Obiettivo

Il livello ("Deep Roots") gira in un container ephemeral personale, distrutto alla disconnessione. La missione (`cat ~/BRIEFING`) chiede di installare tre meccanismi di persistenza indipendenti, ciascuno su un diverso sottosistema Linux, capaci di sopravvivere a un reboot ed evadere un audit di sicurezza di base. Il brief specifica esplicitamente che non serve root: gli attaccanti moderni sfruttano ciò che possono già toccare con i permessi correnti. Il completamento si verifica con `/opt/verify-deep-roots.sh`.

## Ricognizione

Il punto di partenza è l'enumerazione dei file di sistema scrivibili dall'utente corrente, usando `find <path> -user <utente>` su directory chiave (`/etc`, `/dev`, `/home`). Il risultato su `/etc` è sorprendente per un utente non privilegiato: l'utente risulta proprietario di diversi file critici solitamente riservati a root, tra cui uno script in `/etc/profile.d/`, la configurazione PAM `common-auth`, un file in `/etc/cron.d/`, `/etc/bash.bashrc` e altri. Questo è chiaramente un ambiente di laboratorio configurato apposta per permettere l'esercizio: ogni file elencato corrisponde a un diverso sottosistema Linux sfruttabile per la persistenza.

## Tecnica

Il compito richiede tre meccanismi indipendenti su tre sottosistemi diversi. Dalle note emergono chiaramente due implementazioni concrete più un terzo elemento predisposto ma non confermato in dettaglio:

1. **Profile.d (avvio shell di login)**: uno script in `/etc/profile.d/` viene eseguito automaticamente per ogni shell di login. Scrivervi dentro un reverse/bind shell garantisce l'esecuzione ad ogni login interattivo, senza bisogno di demoni o servizi visibili — un meccanismo "silenzioso" perché si attiva solo passivamente quando qualcuno apre una shell.

2. **PAM (`pam_exec.so` in common-auth)**: `/etc/pam.d/common-auth` è la catena di moduli di autenticazione condivisa da tutti i servizi PAM del sistema (SSH, login, sudo...). Aggiungendo una riga `auth optional pam_exec.so <comando>` si ottiene l'esecuzione del comando ad ogni tentativo di autenticazione — un meccanismo particolarmente subdolo perché si integra nel flusso di autenticazione stesso, spesso ignorato da audit superficiali che guardano solo a cron, systemd o file eseguibili sospetti in home directory.

3. **Cron.d (job pianificati di sistema)**: un file in `/etc/cron.d/`, scrivibile dall'utente, permette di installare un job schedulato a livello di sistema (non nel crontab personale, meno ovvio da controllare) che riesegue periodicamente il payload.

In tutti e tre i casi il payload usato nelle note è lo stesso tipo di one-liner di reverse/bind shell basato su `/dev/tcp` (una feature builtin di bash che apre socket TCP senza bisogno di `nc`).

Il punto pedagogico centrale è che, in un ambiente mal configurato, un utente non privilegiato può ottenere persistenza system-wide semplicemente perché è proprietario (o ha permessi di scrittura) su file di configurazione che normalmente richiederebbero root — senza sfruttare alcuna vulnerabilità software, solo un errore di permessi/ownership.

## Sfruttamento

1. Lettura della missione:

```bash
cat BRIEFING
```

2. Enumerazione dei file di sistema di proprietà dell'utente corrente, il passo chiave suggerito dal brief stesso ("modern adversaries rarely need root to persist — they find what they can already touch"):

```bash
find /etc -user <utente> 2>/dev/null
```

```text
/etc/profile.d/<script>.sh
/etc/pam.d/common-auth
/etc/cron.d/<job>
/etc/bash.bashrc
/etc/systemd/system/<servizio>.service
/etc/ld.so.preload
```

Questo singolo comando rivela l'intera superficie di persistenza disponibile: sei file di sistema, sei sottosistemi Linux potenzialmente sfruttabili, tutti scrivibili senza root.

3. **Sottosistema 1 — profile.d**: modifica dello script in `/etc/profile.d/` per includere il payload, eseguito automaticamente a ogni login di shell.

4. **Sottosistema 2 — cron.d**: il file in `/etc/cron.d/` viene popolato con un job che esegue lo stesso payload periodicamente, a livello di sistema anziché nel crontab utente.

5. **Sottosistema 3 — PAM**: individuazione del modulo `pam_exec.so` disponibile sul sistema:

```bash
find / -name "pam_exec.so" 2>/dev/null
```

```text
/usr/lib/x86_64-linux-gnu/security/pam_exec.so
```

e aggiunta di una riga in `/etc/pam.d/common-auth` che lo invoca ad ogni autenticazione, eseguendo il payload.

6. Esecuzione dello script di verifica fornito dal laboratorio, che conferma la presenza di tre meccanismi di persistenza indipendenti:

```bash
/opt/verify-deep-roots.sh
```

```text
[*] Persistence verification: 3 / 3 independent subsystems detected

[*] FLAG: <REDACTED>
[*] Use this as the password for phantom14.
```

## Risultato

Installati con successo tre meccanismi di persistenza indipendenti (profile.d, cron.d, PAM), sfruttando permessi di scrittura anomali su file di sistema critici assegnati all'utente non privilegiato. Il valore della flag non è riportato qui secondo la dottrina BreachLab; il punto didattico è che la persistenza non richiede sempre exploit o privilege escalation — spesso basta un audit di ownership sui file di sistema per trovare superfici già disponibili.

## Nota di pubblicazione

Questa è la versione pensata per la pubblicazione su GitHub secondo la dottrina BreachLab (Writeups · Creators): il metodo è spiegato per intero (i tre sottosistemi sfruttati e la logica di ciascun meccanismo di persistenza), ma il payload letterale copiato dalle note e la flag finale sono stati generalizzati/omessi per non fornire una copia diretta della soluzione.

---

## Crediti

Livello risolto su BreachLab (https://breachlab.org), Phantom Track. Credito al progetto BreachLab per la piattaforma di training.
