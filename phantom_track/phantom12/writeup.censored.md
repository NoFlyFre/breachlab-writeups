# Phantom Track - Phantom 12

## Sommario

- Track: Phantom
- Livello: Phantom 12
- Fonte appunti: `phantom_track/phantom12/notes.md`
- Variante: censored (pubblica)

## Obiettivo

Il brief ("Ghost Install") chiede di installare, senza privilegi sudo/root, quattro meccanismi di persistenza indipendenti a livello utente nella propria home directory, ciascuno in grado di sopravvivere sia a un reboot che a un logout. Ogni artefatto piantato deve contenere una stringa marker specifica da qualche parte nel proprio corpo, per permettere allo script di verifica di distinguere i file piantati dall'operatore da quelli di default della distribuzione. Le superfici suggerite dal brief sono: SSH `authorized_keys`, crontab utente, unit systemd in modalità utente, file di shell rc, e uno shim binario via PATH.

## Ricognizione

Il livello simula lo scenario post-exploitation in cui un operatore ha già accesso a una shell utente (senza root) e deve garantirsi persistenza a lungo termine restando sotto il radar del rilevamento a livello root. Le superfici indicate corrispondono a meccanismi reali usati dagli avversari: chiave SSH aggiuntiva autorizzata, job schedulato via cron, unit systemd in modalità utente, e hijack dei file di inizializzazione della shell. Uno script di verifica fornito dal livello controlla la presenza del marker in ciascuna delle superfici e assegna un punteggio parziale.

## Tecnica

La tecnica è l'installazione di quattro meccanismi di persistenza user-level distinti, tutti realizzabili senza privilegi elevati:

1. **SSH backdoor utente**: aggiunta di una chiave pubblica generata ad-hoc in `~/.ssh/authorized_keys`, usando il commento della chiave (opzione `-C` di `ssh-keygen`) come veicolo per il marker richiesto.
2. **Cron job utente**: un task pianificato (`crontab -e`) che, a intervalli regolari, stampa il marker ed esegue una reverse shell verso un host/porta configurabili.
3. **Unit systemd utente**: un file `.service` sotto `~/.config/systemd/user/` con il marker nel campo `Description` e un `ExecStart` che apre una shell su una connessione TCP tramite file descriptor Bash (`/dev/tcp/...`), con riavvio automatico.
4. **Shell rc hijack**: una riga aggiunta a `.bashrc`, preceduta da un commento con il marker, che esegue lo stesso trucco della reverse shell via file descriptor ogni volta che si apre una shell interattiva.

Ogni meccanismo viene validato incrementalmente rieseguendo lo script di verifica fornito dal livello, che riporta un punteggio parziale e indica esplicitamente quale meccanismo manca ancora.

## Sfruttamento

1. Lettura del brief per capire i requisiti esatti: quattro superfici indipendenti, marker testuale obbligatorio in ciascun artefatto, verifica tramite script fornito dal livello.

2. Generazione di una coppia di chiavi ed25519 dedicata, con il marker richiesto inserito come commento della chiave, e installazione della chiave pubblica in `authorized_keys`. Il commento della chiave, che finisce alla fine della riga della chiave pubblica in formato OpenSSH, soddisfa il requisito del marker senza bisogno di modificare altrimenti il formato del file.

3. Installazione di un cron job utente che stampa il marker ed esegue una reverse shell a intervalli regolari, tramite `crontab -e`.

4. Prima verifica dopo aver installato solo due dei quattro meccanismi, che mostra un punteggio parziale e indica esplicitamente quali meccanismi mancano ancora — il verificatore fornisce feedback granulare per ogni superficie.

5. Creazione di una unit systemd utente sotto `~/.config/systemd/user/`, con il marker nel campo `Description` e un `ExecStart` che apre una reverse shell tramite file descriptor TCP di bash, con parametri di riavvio automatico. Il punteggio sale al 75%.

6. Aggiunta al file di shell rc di una riga con marker e reverse shell, eseguita a ogni apertura di shell interattiva.

7. Verifica finale: tutti e quattro i meccanismi risultano installati, punteggio massimo, e lo script rilascia la flag del livello.

## Risultato

Con tutti e quattro i meccanismi di persistenza user-level installati e verificati, il livello rilascia la flag del livello, da usare come password per l'account del livello successivo. Il valore letterale non viene riportato qui: `<REDACTED_FLAG>`. Il livello ha insegnato tecniche reali di persistenza post-exploitation a livello utente (SSH, cron, systemd user, shell rc) senza necessità di privilegi di root.

## Nota di pubblicazione

Questo writeup è la versione pubblica (GitHub) delle note personali sul livello Phantom 12 di BreachLab. In conformità alla dottrina BreachLab (Writeups · Creators), il documento insegna il metodo — quattro tecniche distinte di persistenza user-level e come validarle incrementalmente — ma non riporta la flag/password finale né dettagli superflui identificativi dell'ambiente personale del solutore, che deve ripetere l'esercizio in autonomia sul proprio ambiente.

## Crediti

Livello svolto su BreachLab (breachlab.org), Phantom Track. Credit a BreachLab per la piattaforma e il design del livello.
