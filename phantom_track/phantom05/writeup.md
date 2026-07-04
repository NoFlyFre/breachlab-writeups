```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   phantom track · phile 0x05 · "file authority"
 ========================================================================

   target ..: phantom-05  "File Authority"
   class ...: group abuse (shadow) · offline hash cracking
   tools ...: find · cat /etc/shadow · hashcat/john · su
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> l'utente sta nel gruppo `shadow`, che di norma nessun mortale dovrebbe
> avere. legge `/etc/shadow`, cracca offline l'unico hash debole (root è
> bloccato), e fa `su` sull'account che possiede la flag.

## ----[ 0x00 · intel ]----

Il brief: l'utente appartiene a un gruppo Unix "interessante" che
determina cosa si può leggere e che non andrebbe mai dato a utenti
normali. Obiettivo: capire quale, leggere ciò che non si dovrebbe, e
craccare offline l'unico hash effettivamente craccabile — quello di un
account diverso, che è sia il pivot sia il proprietario della flag. Root è
bloccato: il suo hash non è craccabile, quello del target sì.

## ----[ 0x01 · recon ]----

Enumerando i file del gruppo `shadow` compaiono, oltre ai binari setgid
attesi (`chage`, `expiry`, `unix_chkpwd`), `/etc/shadow` e `/etc/gshadow`
(e backup) leggibili dal gruppo. Quindi l'utente sta nel gruppo `shadow`,
che su Linux concede la lettura del database delle password hashate — un
privilegio che nessun utente non amministrativo dovrebbe avere.

## ----[ 0x02 · il difetto ]----

Abuso dell'appartenenza al gruppo `shadow` per leggere `/etc/shadow`
(normalmente solo root), poi cracking offline con dizionario dell'unico
hash craccabile del file — gli altri sono bloccati, e root ha un prefisso
da account disabilitato. Ottenuta la password in chiaro del target, si fa
`su` per accedere ai suoi file, flag inclusa.

## ----[ 0x03 · exploit ]----

1. `find` sui file del gruppo `shadow` → accesso in lettura al DB
   password oltre ai binari setgid.

2. Lettura diretta di `/etc/shadow`, possibile grazie al gruppo (un
   tentativo senza fallirebbe con "Permission denied"). L'hash di root ha
   un prefisso da account bloccato; gli altri sono `yescrypt` validi.

3. Identificazione dell'hash target — l'unico craccabile con una wordlist
   comune, di un account di supporto diverso dal solutore — e cracking
   offline (`hashcat`/`john`, wordlist tipo rockyou come da brief). La
   password risulta una parola comune.

4. Cambio utente col crack:

```bash
su <utente>
```

5. Home del target ed enumerazione dei suoi file:

```bash
find / -user <utente> 2>/dev/null
```

6. Lettura della flag, ora accessibile con la sua identità.

## ----[ 0x04 · loot ]----

Gruppo `shadow` indebito → lettura di `/etc/shadow` → crack offline
dell'unico hash debole → `su` → flag (valori fuori dal writeup:
`<REDACTED_HASH>`, `<REDACTED_PASSWORD>`, `<REDACTED_FLAG>`). Nessun brute
force su servizi vivi: il crack è sempre offline su un hash già
esfiltrato. Lezione: `shadow` in mano a un utente normale è game over.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · phantom track
```
