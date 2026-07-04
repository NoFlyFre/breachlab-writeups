# Ghost Track - Ghost 3

[← Torna all'indice](../../README.md)

## Sommario

- Track: Ghost Track
- Livello: Ghost 3 ("Access Denied")
- Fonte appunti: `ghost_track/ghost03/notes.md`

## Obiettivo

Il livello non presenta un banner con "Goal/Connect" esplicito nelle note; l'obiettivo emerge dal contenuto della home: recuperare le credenziali riservate lasciate da un operatore precedente in una directory ad accesso ristretto, descritta come accessibile solo in base all'appartenenza a un gruppo Unix specifico.

## Ricognizione

Nella home utente è presente un file di testo lasciato da un operatore precedente che descrive la struttura di una gerarchia di directory sensibili:

- una directory leggibile da tutti
- una directory ad accesso ristretto
- una directory accessibile solo a root

La nota chiarisce esplicitamente che l'accesso segue lo schema dei gruppi Unix, e suggerisce di verificare la propria identità/appartenenza tramite gli strumenti standard della shell.

## Tecnica

La tecnica è enumerazione dei permessi Unix basata sui gruppi. Verificando l'appartenenza ai gruppi dell'utente corrente, si scopre che appartiene non solo al proprio gruppo primario ma anche a un gruppo aggiuntivo. Osservando i permessi della directory ristretta, si nota che è leggibile ed eseguibile proprio da quel gruppo aggiuntivo — non serve alcuna escalation di privilegi, basta che l'utente sia già membro del gruppo giusto perché il kernel gli conceda l'accesso alla directory e ai file al suo interno.

## Sfruttamento

1. Enumerazione della home utente e lettura della nota lasciata dall'operatore precedente:

```bash
ll
cat map.txt
```

La nota rivela la struttura delle directory riservate e il fatto che l'accesso dipende dal gruppo di appartenenza.

2. Verifica dell'identità e dei gruppi dell'utente corrente:

```bash
whoami
groups
```

L'output mostra che l'utente appartiene anche a un gruppo secondario oltre al proprio gruppo primario.

3. Ispezione dei permessi delle sottodirectory della gerarchia riservata:

```bash
ll /var/intel
```

Una delle sottodirectory risulta leggibile/eseguibile proprio dal gruppo secondario di cui l'utente fa parte — quindi accessibile senza ulteriori privilegi.

4. Accesso diretto alla directory riservata e lettura dei file al suo interno:

```bash
ll
cat access_codes.dat operative_list.txt
```

## Risultato

Le credenziali riservate al gruppo "Analyst Only" sono state recuperate con successo tramite semplice enumerazione dei permessi di gruppo, senza necessità di privilege escalation (valore del codice omesso in questa versione pubblica).

## Nota di pubblicazione

Questa è la versione pubblicabile su GitHub secondo la dottrina BreachLab: spiega per intero il metodo (enumerazione dell'appartenenza ai gruppi Unix e sfruttamento dei permessi di directory già concessi) ma omette il codice di accesso recuperato, per non fornire una scorciatoia a chi non ha ancora risolto il livello.

---

## Crediti

Livello risolto su BreachLab (https://breachlab.org), Ghost Track. Writeup pubblicato nel rispetto della dottrina "no spoilers" della piattaforma.
