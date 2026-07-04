```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   phantom track · phile 0x0c · "ghost install"
 ========================================================================

   target ..: phantom-12  "Ghost Install"
   class ...: persistence · user-level (no root)
   tools ...: ssh-keygen · crontab · systemd --user · bashrc
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> niente root: si pianta persistenza a livello utente su quattro superfici
> diverse, ciascuna capace di sopravvivere a reboot e logout. quattro modi
> di restare, tutti sotto il radar del rilevamento root.

## ----[ 0x00 · intel ]----

Il brief chiede di installare, senza sudo/root, quattro meccanismi di
persistenza utente indipendenti nella home, ognuno capace di sopravvivere
a reboot e logout. Ogni artefatto deve contenere una stringa marker, così
lo script di verifica distingue i file piantati da quelli di default.
Superfici suggerite: SSH `authorized_keys`, crontab utente, unit systemd
user, shell rc, e uno shim binario via PATH.

## ----[ 0x01 · recon ]----

Scenario post-exploitation: shell utente (senza root) e persistenza a
lungo termine restando sotto il radar del rilevamento root. Le superfici
sono meccanismi reali usati dagli avversari: chiave SSH aggiuntiva, cron,
unit systemd user, hijack dei file di init della shell. Uno script di
verifica del livello controlla il marker su ciascuna superficie e assegna
un punteggio parziale.

## ----[ 0x02 · il difetto ]----

Quattro meccanismi user-level, tutti senza privilegi elevati:

1. **SSH backdoor** — chiave pubblica ad-hoc in `~/.ssh/authorized_keys`,
   col marker nel commento della chiave (`ssh-keygen -C`).
2. **cron utente** — task via `crontab -e` che stampa il marker ed esegue
   una reverse shell a intervalli.
3. **unit systemd user** — `.service` in `~/.config/systemd/user/`, marker
   nel `Description`, `ExecStart` con shell su TCP via file descriptor Bash
   (`/dev/tcp/...`) e riavvio automatico.
4. **shell rc hijack** — riga in `.bashrc`, preceduta da un commento col
   marker, con lo stesso trucco reverse shell a ogni shell interattiva.

Ogni meccanismo si valida in modo incrementale rieseguendo lo script di
verifica, che dà punteggio parziale e indica cosa manca.

## ----[ 0x03 · exploit ]----

1. Brief: quattro superfici indipendenti, marker obbligatorio, verifica
   via script.

2. Coppia ed25519 dedicata col marker come commento, pubblica in
   `authorized_keys` (il commento a fine riga soddisfa il marker senza
   toccare il formato).

3. Cron utente che stampa il marker + reverse shell, via `crontab -e`.

4. Prima verifica con due meccanismi su quattro: punteggio parziale, il
   verificatore indica cosa manca.

5. Unit systemd user in `~/.config/systemd/user/`, marker nel
   `Description`, `ExecStart` con reverse shell via file descriptor TCP e
   riavvio automatico. Punteggio al 75%.

6. Riga nel shell rc con marker + reverse shell, a ogni shell interattiva.

7. Verifica finale: tutti e quattro installati, punteggio massimo, lo
   script rilascia la flag.

## ----[ 0x04 · loot ]----

Quattro meccanismi user-level (SSH, cron, systemd user, shell rc)
installati e verificati → la flag, password per il livello dopo:
`<REDACTED_FLAG>`. Lezione: la persistenza non ha bisogno di root — ha
bisogno solo di superfici che nessuno controlla.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · phantom track
```
