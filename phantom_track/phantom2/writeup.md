# Phantom Track - Phantom 2

[← Torna all'indice](../../README.md)

## Sommario

- Track: Phantom Track
- Livello: Phantom 2 ("Sudo Games")
- Fonte appunti: `phantom_track/phantom2/notes.md`

## Obiettivo

Il BRIEFING del livello indica che l'utente `phantom2` ha diritti sudo limitati, non su tutto e non su root. L'obiettivo è enumerare esattamente cosa può eseguire e **come quale utente**, poi usare quel privilegio per leggere un file protetto posseduto da un altro utente di sistema, individuabile tramite l'enumerazione dei permessi su una directory dedicata alle flag.

## Ricognizione

La home di `phantom2` contiene solo un file `BRIEFING` con la missione. Il comando `sudo -l` rivela il privilegio concesso: un binario eseguibile senza password, ma **non come root** — con un `RunAs` verso un altro utente di sistema.

L'enumerazione della directory delle flag mostra una serie di file, ciascuno posseduto da un diverso "flagkeeper" per ogni livello, tutti con permessi restrittivi (leggibili solo dal rispettivo proprietario). L'utente corrente non può leggere direttamente il file target (`Permission denied`), ma può eseguire il binario concesso proprio come l'utente proprietario del file.

## Tecnica

La tecnica è lo **sfruttamento di una regola sudoers con `RunAs` non-root**. Molti pensano a `sudo` solo come "esegui come root", ma la sintassi sudoers permette di specificare un `RunAs` arbitrario (`(utente) comando`). Se il binario concesso è un editor di testo, senza restrizioni sull'argomento nella entry sudoers, l'utente può aprire **qualunque file leggibile dall'utente target** — inclusi quelli che l'utente originale non potrebbe mai leggere direttamente.

Il punto chiave è che l'entry sudoers concede l'esecuzione del binario senza argomenti fissi, quindi il comando può essere invocato specificando come argomento il file che si vuole leggere:

```
sudo -u <utente_target> /usr/bin/vim <file>
```

Questo apre il file con i permessi effettivi dell'utente target (il proprietario del file), bypassando la protezione che impediva la lettura diretta. Diversi tentativi alternativi (assumere che il target fosse root, tentare `su` verso un utente inesistente) falliscono perché non corrispondono esattamente al privilegio concesso da sudoers — la lezione tecnica è leggere con precisione l'output di `sudo -l`, incluso il campo `RunAs` tra parentesi, prima di agire.

## Sfruttamento

1. Enumerazione del privilegio sudo concesso:

```bash
sudo -l
```

Il target di esecuzione del binario concesso non è root, ma un utente specifico indicato tra parentesi nell'output.

2. Individuazione del file target sfruttando l'indizio nel briefing del livello (il proprietario del file è l'utente verso cui si può fare pivot):

```bash
cd /var/lib/phantom-flags
cat level2_flag
cat: level2_flag: Permission denied
```

Conferma diretta che l'utente corrente non ha i permessi di lettura sul file.

3. Tentativi falliti che aiutano a capire i limiti esatti della regola sudoers:

```bash
sudo vim level2_flag
Sorry, user phantom2 is not allowed to execute '/usr/bin/vim level2_flag' as root on phantom.

sudo su phantom
Sorry, user phantom2 is not allowed to execute '/usr/bin/su phantom' as root on phantom.

sudo -u phantom /usr/bin/vim level2_flag
sudo: unknown user phantom
```

Questi tentativi confermano che, senza specificare correttamente l'utente target consentito dalla regola sudoers, sudo rifiuta l'esecuzione perché il default implicito è root, non concesso dalla regola.

4. Esecuzione corretta specificando l'utente target consentito dalla regola sudoers:

```bash
sudo -u <REDACTED> /usr/bin/vim level2_flag
```

Il file si apre con i permessi dell'utente proprietario, rendendone visibile il contenuto.

## Risultato

L'apertura del file protetto con i privilegi dell'utente indicato nella regola sudoers (`RunAs`) permette di bypassare la protezione a livello di permessi Unix, esponendo il contenuto della flag del livello. Il valore letterale non è incluso in questo writeup.

## Nota di pubblicazione

Questa è la versione pubblicabile su GitHub secondo la dottrina BreachLab: spiega per intero il metodo (lettura attenta di `sudo -l`, comprensione del campo `RunAs` non-root, uso di un editor concesso per leggere file altrui), ma non riporta la flag risolutiva, in modo da preservare la sfida per gli altri operatori.

---

## Crediti

Livello risolto su BreachLab (https://breachlab.org), Phantom Track — piattaforma di training autorizzato per pentest/CTF. Rispetta le Standing Orders: nessuno spoiler di password o flag letterali.
