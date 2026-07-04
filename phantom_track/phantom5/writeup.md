# Phantom Track - Phantom 5

## Sommario

- Track: Phantom
- Livello: Phantom 5
- Fonte appunti: `phantom_track/phantom5/notes.md`

## Obiettivo

Il brief ("File Authority") spiega che l'utente del livello appartiene a un gruppo Unix "interessante" — un gruppo che determina cosa si può leggere sul sistema, e che non dovrebbe mai essere assegnato a utenti normali. L'obiettivo è capire di che gruppo si tratta, cosa permette di leggere, leggere ciò che normalmente non si potrebbe leggere, e craccare offline l'unico hash effettivamente craccabile trovato — che appartiene a un account diverso dall'utente di partenza, il quale è sia il pivot target sia il proprietario della flag. Il brief specifica esplicitamente che root è bloccato su questa macchina: l'hash di root non è craccabile, mentre quello dell'account target lo è.

## Ricognizione

L'enumerazione dei file appartenenti al gruppo `shadow` rivela, oltre ai binari di sistema attesi (utility con bit setgid come `chage`, `expiry`, `unix_chkpwd`), i file `/etc/shadow` e `/etc/gshadow` (e i relativi backup) leggibili dal gruppo. Questo indica che l'utente del livello appartiene al gruppo `shadow`, un gruppo che su un sistema Linux standard concede la lettura del database delle password hashate — un privilegio che normalmente nessun utente non amministrativo dovrebbe avere.

## Tecnica

La tecnica sfruttata è l'abuso dell'appartenenza al gruppo `shadow` per leggere `/etc/shadow` (operazione normalmente riservata a root), seguita da cracking offline con dizionario dell'unico hash effettivamente crackabile nel file — gli altri account hanno hash bloccati o, nel caso di root, un prefisso che ne indica l'account disabilitato/non craccabile in questo contesto. Una volta ottenuta la password in chiaro dell'account target, la tecnica prosegue con un cambio di utente (`su`) per accedere ai file di proprietà di quell'account, incluso la flag protetta.

## Sfruttamento

1. Enumerazione dei file appartenenti al gruppo `shadow` con `find`, che rivela l'accesso in lettura al database delle password oltre ai normali binari di sistema con bit setgid.

2. Lettura diretta di `/etc/shadow`, resa possibile dall'appartenenza al gruppo `shadow` (un tentativo di lettura senza quel gruppo fallirebbe con "Permission denied", come dimostra un primo tentativo fallito con path relativo). L'estratto rilevante mostra l'hash di root con un prefisso che ne indica l'account bloccato (non autenticabile via password), e una lunga lista di altri account con hash di tipo `yescrypt` validi.

3. Identificazione dell'hash target — l'unico effettivamente craccabile con un dizionario comune, appartenente a un account di supporto diverso da quello del solutore — e cracking offline con dizionario (tool tipo `hashcat`/`john`, wordlist tipo rockyou, come suggerito dai riferimenti del brief). La password in chiaro risulta una parola comune presente in wordlist standard.

4. Cambio utente verso l'account target con la password appena craccata (`su <utente>`).

5. Navigazione verso la home dell'account target ed enumerazione dei file di sua proprietà nel filesystem con `find / -user <utente>`.

6. Lettura della flag, ora accessibile con l'identità dell'account target.

## Risultato

Sfruttando l'appartenenza indebita al gruppo `shadow` è stato possibile leggere `/etc/shadow`, individuare l'unico hash password realmente craccabile, craccarlo offline con dizionario, ed effettuare un cambio utente per leggere la flag di proprietà di quell'account. I valori letterali (hash, password in chiaro, flag) non vengono riportati qui: `<REDACTED_HASH>`, `<REDACTED_PASSWORD>`, `<REDACTED_FLAG>`. Il livello ha insegnato l'analisi dei privilegi di gruppo Unix con impatto sulla sicurezza (in particolare `shadow`) e il cracking offline responsabile di hash di password, senza alcun brute force diretto contro servizi live.

## Nota di pubblicazione

Questo writeup è la versione pubblica (GitHub) delle note personali sul livello Phantom 5 di BreachLab. In conformità alla dottrina BreachLab (Writeups · Creators), il documento insegna il metodo — analisi dei privilegi di gruppo Unix pericolosi, lettura autorizzata (dal punto di vista del sistema operativo, anche se non prevista) di `/etc/shadow`, e cracking offline con dizionario — ma non riporta hash, password in chiaro o la flag finale, che il solutore deve ottenere in autonomia ripetendo l'analisi sul proprio ambiente, nel rispetto della regola "no brute force" contro l'infrastruttura viva (il cracking qui è sempre offline, contro un hash già esfiltrato legittimamente).

## Crediti

Livello svolto su BreachLab (breachlab.org), Phantom Track. Credit a BreachLab per la piattaforma e il design del livello.
