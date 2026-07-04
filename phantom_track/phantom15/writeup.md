```
 ========================================================================
   B R E A C H L A B   ::   F I E L D   N O T E S
 ------------------------------------------------------------------------
   phantom track · phile 0x0f · "clean slate"
 ========================================================================

   target ..: phantom-15  "Clean Slate"
   class ...: anti-forensics · log/trace cleanup
   tools ...: rm · unset HISTFILE · verify script
   author ..: noflyfre
   status ..: owned
```

[← indice](../../README.md)

> hai compromesso il box, ora cancella ogni traccia. e attenzione:
> svuotare un file con `echo "" >` non è cancellarlo. l'investigatore lo
> vede lo stesso.

## ----[ 0x00 · intel ]----

Dal brief:

```text
MISSION: Clean Slate
===================

You compromised this box. Now erase every trace.

An investigator will read the standard operator-trail
categories: SSH records, login records, failed-login records,
your shell history, filesystem audit records. Find what you
can touch. Erase your presence.

Flag first: /root/clean_flag — then clean up.

Run /opt/verify-clean.sh when you think you are clean.
```

Anti-forensics: dopo aver letto `/root/clean_flag`, ripulire ogni traccia
(log SSH, login, failed login, shell history, audit) fino a passare
`/opt/verify-clean.sh` con zero tracce.

## ----[ 0x01 · recon ]----

Identità e gruppi:

```bash
whoami
phantom15
id
uid=1022(phantom15) gid=1022(phantom15) groups=1022(phantom15),1024(ops_flag14),1025(ops_logs)
```

L'utente sta in `ops_flag14` e `ops_logs`. File accessibili via questi
gruppi:

```bash
find / \( -group phantom15 -o -group ops_flag14 -o -group ops_logs \) 2>/dev/null
```

Tra i risultati: la home (con `.bash_history`, `.bashrc`, `.profile`,
`BRIEFING`) e i log forensi tipici: `/var/log/lastlog`, `wtmp`,
`audit/audit.log`, `syslog`.

## ----[ 0x02 · il difetto ]----

Categorie che un forense controllerebbe: **auth.log** (auth SSH),
**wtmp/btmp/lastlog** (login binari), **audit.log** (audit fs),
**bash_history** (comandi). Non è un exploit ma un processo iterativo
guidato da `/opt/verify-clean.sh`, che segnala cosa è ancora "sporco".

Il punto tecnico chiave: **svuotare con `echo "" > file` non equivale a
rimuoverlo**. Il verifier continuava a segnalare `.bash_history` anche
dopo lo svuotamento, perché il file (pur vuoto) risultava
presente/modificato in modo anomalo. Soluzione: `rm` diretto, più `unset
HISTFILE` per impedire alla shell corrente di riscrivere la history a fine
sessione.

## ----[ 0x03 · exploit ]----

1. Lettura del valore iniziale prima della pulizia:

```bash
cat /root/clean_flag
<REDACTED_FLAG>
```

2. Primi tentativi con redirection vuota:

```bash
echo "" > /home/phantom15/.bash_history
echo "" > /var/log/audit/audit.log
echo "" > /var/log/auth.log
```

3. Verifica:

```bash
/opt/verify-clean.sh
[*] Forensic investigation in progress...

[+] auth.log: CLEAN
[+] wtmp: CLEAN
[+] btmp: CLEAN
[!] TRACE: commands in .bash_history
[+] audit.log: CLEAN
[!] TRACE: login recorded in lastlog

[!] 2 trace(s) found. An investigator would catch you.
```

Restano `lastlog` e `.bash_history`.

4. `lastlog` (va cercato esplicitamente) e nuovo tentativo su history:

```bash
echo "" > /var/log/lastlog
echo "" > /home/phantom15/.bash_history
/opt/verify-clean.sh
```

`lastlog: CLEAN`, ma `.bash_history` resta segnalata nonostante lo
svuotamento.

5. Diagnosi: il verifier vede il file come traccia anche vuoto.

```bash
find / -name ".bash_history" -exec ls -al {} \; 2>/dev/null
-rw------- 1 phantom28 phantom28 48 Jun 28 13:40 /home/phantom28/.bash_history
...
-rw------- 1 phantom15 phantom15 155 Jun 28 13:55 /home/phantom15/.bash_history
```

6. `unset HISTFILE` per non far riscrivere la history, poi `rm` invece di
   svuotare:

```bash
unset HISTFILE
rm /home/phantom15/.bash_history
/opt/verify-clean.sh
```

7. Verifica finale, tutto pulito:

```bash
/opt/verify-clean.sh
[*] Forensic investigation in progress...

[+] auth.log: CLEAN
[+] wtmp: CLEAN
[+] btmp: CLEAN
[+] bash_history: CLEAN
[+] audit.log: CLEAN
[+] lastlog: CLEAN

[*] Zero traces found. Perfect cleanup.

[*] FLAG: <REDACTED_FLAG>
[*] Use this as the password for phantom16.
```

## ----[ 0x04 · loot ]----

Cleanup completo, zero tracce; il livello restituisce la flag (anche
password per phantom16). Il valore di `/root/clean_flag` è solo un marker
intermedio, non la flag finale — entrambi omessi. Lezione: svuotare ≠
rimuovere, e la shell riscrive la history se non le togli `HISTFILE`.

```
--[ eof ]---------------------------------------------------------------

  breachlab.org · phantom track
```
