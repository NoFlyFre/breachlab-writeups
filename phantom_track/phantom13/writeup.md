```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   phantom track · phile 0x0d · "deep roots"
 ========================================================================

   target ..: phantom-13  "Deep Roots"
   class ...: persistence · system-wide via file ownership
   tools ...: find -user · profile.d · pam_exec · cron.d
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> non serve root per mettere radici: basta essere proprietario dei file
> giusti. un `find /etc -user te` rivela che possiedi profile.d, PAM e
> cron.d — tre sottosistemi, tre persistenze, zero exploit.

## ----[ 0x00 · intel ]----

Container ephemeral personale, distrutto alla disconnessione. Il brief
chiede tre meccanismi di persistenza indipendenti, ognuno su un diverso
sottosistema Linux, capaci di sopravvivere a un reboot ed evadere un audit
di base. Niente root: gli avversari moderni usano ciò che già toccano.
Verifica con `/opt/verify-deep-roots.sh`.

## ----[ 0x01 · recon ]----

Il punto di partenza è enumerare i file di sistema scrivibili dall'utente
con `find <path> -user <utente>` su `/etc`, `/dev`, `/home`. Il risultato
su `/etc` è sorprendente per un utente non privilegiato: possiede diversi
file critici di solito riservati a root (uno script in `/etc/profile.d/`,
`common-auth` di PAM, un file in `/etc/cron.d/`, `/etc/bash.bashrc` e
altri). Ambiente di lab configurato apposta: ogni file = un sottosistema
sfruttabile.

## ----[ 0x02 · il difetto ]----

Tre meccanismi indipendenti, tutti senza root:

1. **profile.d (login shell)** — uno script in `/etc/profile.d/` gira a
   ogni shell di login: metterci una reverse/bind shell dà esecuzione a
   ogni login, silenziosa perché passiva.
2. **PAM (`pam_exec.so` in common-auth)** — `/etc/pam.d/common-auth` è la
   catena di auth condivisa da SSH, login, sudo… Una riga
   `auth optional pam_exec.so <comando>` esegue il comando a ogni auth,
   particolarmente subdola perché sta dentro il flusso di autenticazione,
   spesso ignorato dagli audit che guardano cron/systemd/home.
3. **cron.d (job di sistema)** — un file in `/etc/cron.d/` scrivibile
   installa un job system-wide (non nel crontab personale, meno ovvio) che
   riesegue il payload.

In tutti e tre, il payload è lo stesso one-liner reverse/bind shell su
`/dev/tcp` (builtin di bash, niente `nc`). Il punto: in un ambiente mal
configurato, un utente non privilegiato ottiene persistenza system-wide
solo perché possiede file di config che vorrebbero root — nessuna vuln,
solo un errore di ownership.

## ----[ 0x03 · exploit ]----

1. Brief:

```bash
cat BRIEFING
```

2. Il passo chiave, i file di sistema che possiedi:

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

Un comando, l'intera superficie di persistenza: sei file, sei
sottosistemi, tutti scrivibili senza root.

3. **profile.d** — payload nello script, eseguito a ogni login.

4. **cron.d** — il file popolato con un job che riesegue il payload,
   a livello di sistema.

5. **PAM** — individuazione del modulo:

```bash
find / -name "pam_exec.so" 2>/dev/null
```

```text
/usr/lib/x86_64-linux-gnu/security/pam_exec.so
```

e riga in `/etc/pam.d/common-auth` che lo invoca a ogni auth.

6. Verifica:

```bash
/opt/verify-deep-roots.sh
```

```text
[*] Persistence verification: 3 / 3 independent subsystems detected

[*] FLAG: <REDACTED>
[*] Use this as the password for phantom14.
```

## ----[ 0x04 · loot ]----

Tre persistenze indipendenti (profile.d, cron.d, PAM) sfruttando ownership
anomala su file di sistema (valore fuori dal writeup). Lezione: la
persistenza spesso non chiede un exploit — chiede un audit di ownership che
nessuno ha fatto.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · phantom track
```
