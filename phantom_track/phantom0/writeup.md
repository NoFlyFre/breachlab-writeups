# Phantom Track - Phantom 0

[← Torna all'indice](../../README.md)

## Sommario

- Track: Phantom Track
- Livello: Phantom 0 ("Recon Gateway")
- Fonte appunti: `phantom_track/phantom0/notes.md`

## Obiettivo

Il briefing è esplicito: si ha accesso shell su un host compromesso e, prima di qualunque escalation, serve piena consapevolezza situazionale. Le domande guida sono: che OS/kernel gira, chi altro è sulla macchina, quali servizi sono attivi, quali difese sono presenti. La flag è nascosta in un punto che solo una ricognizione approfondita permette di trovare.

## Ricognizione

La ricognizione segue un metodo sistematico da checklist di privilege escalation Linux (in stile HackTricks), coprendo in sequenza: identità del sistema, utenti, processi, rete, cron, e permessi.

**Sistema operativo e kernel:** identificati tramite `uname -a` e `/etc/os-release`, rivelando una distribuzione Ubuntu LTS con kernel recente.

**Utenti del sistema:** `/etc/passwd` rivela una popolazione insolita di account: oltre ai soliti account di sistema, ci sono decine di utenti numerati (livelli del wargame), account "flagkeeper" (che custodiscono le flag di altri livelli), e alcuni account di servizio. Da notare alcuni account con shell impostata su un binario custom invece della classica shell interattiva — un dettaglio che segnala un meccanismo di redirect/sandboxing specifico del lab.

**Gruppi:** `/etc/group` rivela che un utente appartiene al gruppo `shadow` — un privilegio insolito che normalmente permette la lettura di `/etc/shadow` (gli hash delle password). Un altro utente risulta membro secondario del gruppo di un altro livello.

**Processi attivi:** l'enumerazione dei processi rivela, oltre ai processi di sistema standard tipici di un container, due dettagli interessanti: un emulatore dell'API Docker in ascolto sia su porta TCP standard sia su socket Unix, e un processo con riferimento esplicito a `ptrace_scope` — indizi su temi dei livelli successivi (container escape, ptrace/debugging tra processi).

**Difese attive:** AppArmor risulta installato e ASLR è impostato al valore di default hardened.

**Rete:** due interfacce di rete, una verso la rete Docker generale e una rete secondaria dedicata — probabilmente per il pivoting tra le macchine del lab. Il forwarding IP risulta abilitato, coerente con un possibile ruolo di gateway/router tra segmenti.

**Cron:** tra le voci standard di sistema compare un file dal nome molto indicativo legato alla gestione/rotazione delle flag del lab.

**Superficie SUID e sudo:** vengono enumerati sia i comandi sudo disponibili sia i binari SUID sul sistema, propedeutici a un'eventuale escalation nei livelli successivi.

**File toccati nella finestra di setup del lab:** la ricerca mirata più produttiva è stata cercare tutti i file leggibili modificati in una finestra temporale specifica, corrispondente al giorno di provisioning del lab. Questo approccio, invece di enumerare a tappeto tutto il filesystem, isola rapidamente gli artefatti specifici del lab (script di verifica, vault, flag) dal rumore di sistema.

## Tecnica

La tecnica centrale di questo livello è la **ricognizione sistematica combinata con una ricerca temporale mirata (`find -newermt`)**: invece di affidarsi solo all'enumerazione manuale standard (utenti, processi, rete, cron, SUID), la scoperta decisiva arriva isolando tutti i file leggibili modificati esattamente nella finestra temporale in cui il lab è stato provisionato. Questo riduce drasticamente lo spazio di ricerca su un filesystem enorme, portando dritti agli artefatti "piantati" dagli autori del lab — inclusa la flag — invece di perdersi nel rumore dei file di sistema standard (pacchetti, cache, documentazione).

## Sfruttamento

1. Identificazione di OS e kernel:

```bash
uname -a
cat /etc/os-release
```

2. Enumerazione di utenti e gruppi per capire la topologia degli account e individuare privilegi di gruppo anomali:

```bash
cat /etc/passwd
cat /etc/group
```

3. Enumerazione dei processi attivi per identificare servizi custom del lab e altri indizi sui livelli successivi:

```bash
ps -aux
ps -ef
top -n 1
```

4. Verifica delle difese attive (AppArmor, ASLR):

```bash
if [ `which aa-status 2>/dev/null` ]; then aa-status; elif [ `ls -d /etc/apparmor* 2>/dev/null` ]; then ls -d /etc/apparmor*; fi
cat /proc/sys/kernel/randomize_va_space
```

5. Enumerazione della rete (interfacce, routing, forwarding):

```bash
(ifconfig || ip a)
ip route
sysctl net.ipv4.ip_forward net.ipv6.conf.all.forwarding net.ipv4.conf.all.rp_filter
```

6. Controllo dei cron job di sistema, dove emerge un file dal nome indicativo legato alla gestione delle flag:

```bash
cat /etc/cron* /etc/at* /etc/anacrontab /var/spool/cron/crontabs/root 2>/dev/null | grep -v "^#"
ls -al /etc/cron.d/
```

7. Enumerazione della superficie di privilegio (sudo, SUID), propedeutica ai livelli successivi:

```bash
sudo -l
find / -perm -4000 2>/dev/null
```

8. La ricerca mirata decisiva: individuare tutti i file leggibili toccati durante la finestra di provisioning del lab, filtrando via il rumore delle directory di libreria/documentazione/cache standard:

```bash
find / \( -path /proc -o -path /sys -o -path /run \) -prune -o \
  -type f -newermt '<data_provisioning>' ! -newermt '<data_provisioning+1>' -readable -print 2>/dev/null \
  | grep -vE '^/(usr/lib|usr/share|var/lib/dpkg|etc/ssl)' | head -60
```

L'output rivela una serie di script di verifica automatica dei livelli successivi (pod escape, persistence, clean exit, shadow, ecc.), un vault, un segreto legato al namespace host, e soprattutto il file contenente la flag del livello.

9. Lettura diretta del file flag individuato tramite `cat`.

## Risultato

La flag del livello si trovava in un file dedicato sotto `/opt/`, individuata non tramite ricerca a tappeto ma isolando i file leggibili modificati nella specifica finestra temporale di provisioning del lab. Il valore letterale della flag non viene riportato in questa versione. La ricognizione ha inoltre raccolto diversi indizi utili per i livelli successivi: l'emulatore del socket Docker in ascolto, il processo con riferimento a `ptrace_scope`, il gruppo `shadow` assegnato a un utente, e gli script di verifica che anticipano i temi (pod escape, persistence, namespace host) dei livelli avanzati della Phantom Track.

## Nota di pubblicazione

Questa è la versione pensata per la pubblicazione su GitHub, in conformità con la dottrina BreachLab: insegna il metodo di ricognizione sistematica e la tecnica della ricerca temporale mirata (`find -newermt`) senza riportare percorsi assoluti specifici del lab, date di provisioning esatte o il valore letterale della flag.

---

## Crediti

Livello e piattaforma: BreachLab (breachlab.org) — Phantom Track. Se questo writeup genera revenue, parte del ricavato va devoluta secondo la dottrina "if it earns, give back" di BreachLab.
