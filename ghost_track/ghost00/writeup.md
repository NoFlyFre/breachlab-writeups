# Ghost Track - Ghost 0

[← Torna all'indice](../../README.md)

## Sommario

- Track: Ghost Track
- Livello: Ghost 0 ("First Contact")
- Fonte appunti: `ghost_track/ghost00/notes.md`

## Obiettivo

Livello di ingresso del Ghost Track. L'obiettivo è la ricognizione base della home directory assegnata all'operatore, alla ricerca di file lasciati sul sistema che possano contenere informazioni utili a proseguire (credenziali, note operative, riferimenti ad altri file).

## Ricognizione

Nella home dell'utente è presente un file `notes.txt` che simula appunti operativi lasciati da un altro operatore (KAEL). Il file descrive un target di rete fittizio e un metodo di lavoro (recon passiva, nessuno scan attivo), e soprattutto contiene un promemoria: le credenziali sono archiviate separatamente in una cartella `archive/`, con la nota esplicita "non salvare password in chiaro nelle note".

Nonostante l'avvertimento presente nel testo, ispezionando la directory è stato trovato anche un secondo file, `credentials`, nella stessa posizione.

## Tecnica

Non è richiesta alcuna tecnica di exploitation: il livello insegna l'abitudine fondamentale del pentesting, ovvero l'enumerazione sistematica del filesystem accessibile prima di qualunque altra azione. La "vulnerabilità" qui è puramente operativa (OPSEC failure) — un file di credenziali lasciato accanto alle note nonostante l'avvertimento contrario presente nelle note stesse. È un promemoria che i secret non vanno mai salvati in chiaro insieme alla documentazione, e che come attaccante la prima cosa da fare è sempre guardarsi intorno con `ls`/`cat` prima di lanciare tool più complessi.

## Sfruttamento

1. Lettura del file di note nella home directory:

```bash
cat notes.txt
```

Output:

```text
OPERATIONAL NOTES — KAEL
========================
Target: internal network segment 10.4.x.x
Method: passive recon, no active scanning
Status: ongoing

Credentials filed separately in archive/.
Do not store passwords in plaintext notes.
```

Il file conferma che esiste un secondo file con le credenziali, in violazione della propria stessa policy interna.

2. Lettura del file di credenziali trovato accanto alle note:

```bash
cat credentials
```

Output:

```text
<REDACTED>
```

## Risultato

La lettura del secondo file nella home directory restituisce la password per il livello successivo (ghost1). Il valore letterale non è riportato qui secondo la dottrina BreachLab; il punto didattico è che l'enumerazione sistematica della home directory (`ls`/`cat` su ogni file, anche quello che sembra "solo" un promemoria) è sufficiente a completare il livello.

## Nota di pubblicazione

Questa è la versione pensata per la pubblicazione su GitHub secondo la dottrina BreachLab (Writeups · Creators): il metodo è spiegato per intero, ma password e flag letterali sono state sostituite con `<REDACTED>` per non fornire scorciatoie a chi non ha ancora risolto il livello.

---

## Crediti

Livello risolto su BreachLab (https://breachlab.org), Ghost Track. Credito al progetto BreachLab per la piattaforma di training.
