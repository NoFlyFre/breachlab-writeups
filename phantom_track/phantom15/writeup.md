# Phantom Track - Phantom 15

[← Torna all'indice](../../README.md)

## Sommario

- Track: Phantom Track
- Livello: Phantom 15 — Clean Slate
- Fonte appunti: `phantom_track/phantom15/notes.md`

## Obiettivo

Dal BRIEFING del livello:

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

Livello di anti-forensics: dopo la lettura di un valore in `/root/clean_flag`, l'obiettivo è ripulire ogni traccia operativa (log SSH, login, tentativi falliti, shell history, audit filesystem) fino a passare lo script `/opt/verify-clean.sh` con zero tracce residue.

## Ricognizione

Verifica identità e appartenenza a gruppi:

```bash
whoami
phantom15
id
uid=1022(phantom15) gid=1022(phantom15) groups=1022(phantom15),1024(ops_flag14),1025(ops_logs)
```

L'utente appartiene ai gruppi `ops_flag14` e `ops_logs`, oltre al proprio gruppo primario. Enumerazione dei file accessibili tramite questi gruppi:

```bash
find / \( -group phantom15 -o -group ops_flag14 -o -group ops_logs \) 2>/dev/null
```

Tra i risultati rilevanti: la propria home (`/home/phantom15` con `.bash_history`, `.bashrc`, `.profile`, `BRIEFING`) e diversi file di log tipici delle tracce forensi: `/var/log/lastlog`, `/var/log/wtmp`, `/var/log/audit/audit.log`, `/var/log/syslog`.

## Tecnica

Il livello richiede di ragionare sulle categorie di evidenza che un investigatore forense controllerebbe dopo una compromissione:

- **auth.log** — log di autenticazione (successi/fallimenti SSH)
- **wtmp / btmp / lastlog** — record binari di login/logout e ultimi accessi
- **audit.log** — audit trail del filesystem
- **bash_history** — cronologia dei comandi della shell

La tecnica non è un singolo exploit ma un processo iterativo guidato dal verificatore (`/opt/verify-clean.sh`), che segnala quali categorie sono ancora "sporche". Il punto tecnico più importante emerso: **svuotare un file con `echo "" > file` non è equivalente a rimuoverlo**. Il verifier continuava a segnalare `TRACE: commands in .bash_history` anche dopo lo svuotamento con redirection, perché il file (anche vuoto) risultava comunque presente/modificato in modo anomalo. La soluzione corretta è stata la rimozione diretta del file (`rm`), e in aggiunta l'uso di `unset HISTFILE` per impedire che la shell corrente riscrivesse una nuova history al termine della sessione.

## Sfruttamento

1. Lettura del valore iniziale richiesto dal brief prima di procedere alla pulizia:

```bash
cat /root/clean_flag
<REDACTED_FLAG>
```

2. Primi tentativi di pulizia via redirection vuota sui file di log e history:

```bash
echo "" > /home/phantom15/.bash_history
echo "" > /var/log/audit/audit.log
echo "" > /var/log/auth.log
```

3. Verifica con lo script fornito dal lab:

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

Restano due tracce: `lastlog` e `.bash_history`.

4. Pulizia di `lastlog` (non individuato nel primo giro di `find`, va cercato esplicitamente):

```bash
echo "" > /var/log/lastlog
echo "" > /home/phantom15/.bash_history
/opt/verify-clean.sh
```

Risultato: `lastlog: CLEAN`, ma `.bash_history` resta segnalata nonostante lo svuotamento ripetuto via `echo "" >`.

5. Diagnosi del problema: il verifier continua a vedere il file come traccia anche vuoto. Enumerazione di tutti i `.bash_history` presenti sul sistema per confronto:

```bash
find / -name ".bash_history" -exec ls -al {} \; 2>/dev/null
-rw------- 1 phantom28 phantom28 48 Jun 28 13:40 /home/phantom28/.bash_history
-rw------- 1 phantom24 phantom24 48 Jun 28 13:40 /home/phantom24/.bash_history
-rw------- 1 phantom20 phantom20 48 Jun 28 13:40 /home/phantom20/.bash_history
-rw------- 1 phantom16 phantom16 48 Jun 28 13:40 /home/phantom16/.bash_history
-rw------- 1 phantom15 phantom15 155 Jun 28 13:55 /home/phantom15/.bash_history
```

6. Impostazione di `unset HISTFILE` per evitare che la shell riscriva la history a fine sessione, poi rimozione diretta del file invece di svuotarlo:

```bash
unset HISTFILE
rm /home/phantom15/.bash_history
/opt/verify-clean.sh
```

7. Verifica finale: tutte le categorie risultano pulite.

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

## Risultato

Cleanup completo verificato dallo script del lab, con zero tracce residue. Il livello restituisce una flag di completamento che funge anche da password per accedere al livello successivo (Phantom 16). Il valore mostrato inizialmente da `/root/clean_flag` è solo un marker intermedio della fase di lettura, non la flag di completamento del livello — entrambi i valori sono stati rimossi da questa versione.

## Nota di pubblicazione

Questa è la versione pensata per pubblicazione su GitHub, secondo la dottrina BreachLab: il metodo di pulizia forense (identificazione delle categorie di traccia, differenza tra svuotare e rimuovere un file, uso di `unset HISTFILE`) è spiegato per intero — comandi e percorsi restano in chiaro — ma entrambi i valori letterali (il marker letto da `/root/clean_flag` e la flag finale del verifier) sono stati rimossi.

---

## Crediti

Livello risolto su BreachLab — https://breachlab.org (Phantom Track). Writeup pubblicato nel rispetto delle regole della piattaforma: si insegna la tecnica, non si condivide la risposta.
