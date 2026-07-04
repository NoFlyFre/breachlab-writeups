# BreachLab Writeups

Writeup dei wargame di [BreachLab](https://breachlab.org), il campo su cui mi alleno per il tradecraft offensivo e difensivo.

![Ghost Track](https://img.shields.io/badge/Ghost_Track-23%2F23-brightgreen)
![Phantom Track](https://img.shields.io/badge/Phantom_Track-18%2F31-yellow)
![Mirage Track](https://img.shields.io/badge/Mirage_Track-7%2F41-orange)
![Doctrine](https://img.shields.io/badge/doctrine-no%20spoilers-blueviolet)

## Cos'è questo repo

Qui raccolgo i writeup dei livelli di BreachLab che ho risolto, divisi in tre track: Ghost (fondamentali di enumerazione e credential hunting), Phantom (post-exploitation e tradecraft operativo) e Mirage (ricognizione e sfruttamento di applicazioni web).

Ogni writeup racconta il ragionamento, gli strumenti e i passaggi che servono a rifare il lavoro sulla tua istanza del livello.

## Struttura

Ogni livello vive nella sua cartella, con il nome nel formato `<track>/<track><NN>` numerato a due cifre così l'ordine resta quello giusto. Nel repo pubblico ogni cartella contiene un solo file:

```
ghost_track/
  ghost00/
    writeup.md      <- unico file pubblico: metodo, nessuno spoiler
phantom_track/
  phantom00/
    writeup.md
mirage_track/
  mirage00/
    writeup.md
```

Le note grezze (`notes.md`, log e output completi del terminale) e la versione integrale con i valori reali (`writeup.uncensored.md`) le tengo in locale e non finiscono mai online: sono escluse tramite `.gitignore`.

## Dottrina

BreachLab chiede due cose a chi scrive writeup:

> **Teach technique, never publish answers.** Writeups and videos are welcome when they teach the method — not the literal password or flag.
>
> **Credit BreachLab.** A link back or a name-drop in the description. That's it.

Ogni writeup qui rispetta entrambe: racconta per intero recon, vulnerabilità e sfruttamento, ma lascia fuori qualsiasi valore che permetterebbe di saltare il ragionamento.

## Ghost Track — 23/23 risolti

Fondamentali di Linux e shell: dimestichezza col terminale, filesystem, processi, rete, encoding, permessi.

| # | Livello | Stato | Writeup |
|---|---------|:-----:|---------|
| 0 | First Contact | ✅ | [writeup](ghost_track/ghost00/writeup.md) |
| 1 | Name Game | ✅ | [writeup](ghost_track/ghost01/writeup.md) |
| 2 | In The Shadows | ✅ | [writeup](ghost_track/ghost02/writeup.md) |
| 3 | Access Denied | ✅ | [writeup](ghost_track/ghost03/writeup.md) |
| 4 | Signal in the Noise | ✅ | [writeup](ghost_track/ghost04/writeup.md) |
| 5 | The Listener | ✅ | [writeup](ghost_track/ghost05/writeup.md) |
| 6 | Ghost in the Machine | ✅ | [writeup](ghost_track/ghost06/writeup.md) |
| 7 | Lost in Translation | ✅ | [writeup](ghost_track/ghost07/writeup.md) |
| 8 | Something's Running | ✅ | [writeup](ghost_track/ghost08/writeup.md) |
| 9 | Core Dump | ✅ | [writeup](ghost_track/ghost09/writeup.md) |
| 10 | Odd Token Out | ✅ | [writeup](ghost_track/ghost10/writeup.md) |
| 11 | Unwrap the Stage | ✅ | [writeup](ghost_track/ghost11/writeup.md) |
| 12 | Harvested Key | ✅ | [writeup](ghost_track/ghost12/writeup.md) |
| 13 | Credential Broker | ✅ | [writeup](ghost_track/ghost13/writeup.md) |
| 14 | TLS Only | ✅ | [writeup](ghost_track/ghost14/writeup.md) |
| 15 | Ephemeral Port | ✅ | [writeup](ghost_track/ghost15/writeup.md) |
| 16 | Config Drift | ✅ | [writeup](ghost_track/ghost16/writeup.md) |
| 17 | No Shell For You | ✅ | [writeup](ghost_track/ghost17/writeup.md) |
| 18 | Wrong User | ✅ | [writeup](ghost_track/ghost18/writeup.md) |
| 19 | Your First Script | ✅ | [writeup](ghost_track/ghost19/writeup.md) |
| 20 | Cron Discovery | ✅ | [writeup](ghost_track/ghost20/writeup.md) |
| 21 | Secrets in History | ✅ | [writeup](ghost_track/ghost21/writeup.md) |
| 22 | Graduation (classified) | ✅ | [writeup](ghost_track/ghost22/writeup.md) |

## Phantom Track — 18/31 risolti

Post-exploitation dall'inizio alla fine: privesc, raccolta e persistenza, movimento laterale, container e cloud, operazioni.

<details open>
<summary>Espandi tabella</summary>

| # | Livello | Stato | Writeup |
|---|---------|:-----:|---------|
| 0 | Recon Gateway | ✅ | [writeup](phantom_track/phantom00/writeup.md) |
| 1 | SUID Hunter | ✅ | [writeup](phantom_track/phantom01/writeup.md) |
| 2 | Sudo Games | ✅ | [writeup](phantom_track/phantom02/writeup.md) |
| 3 | Inheritance | ✅ | [writeup](phantom_track/phantom03/writeup.md) |
| 4 | Misplaced Power | ✅ | [writeup](phantom_track/phantom04/writeup.md) |
| 5 | File Authority | ✅ | [writeup](phantom_track/phantom05/writeup.md) |
| 6 | Scheduled Sins | ✅ | [writeup](phantom_track/phantom06/writeup.md) |
| 7 | Local Authority | ✅ | [writeup](phantom_track/phantom07/writeup.md) |
| 8 | Live Injection | ✅ | [writeup](phantom_track/phantom08/writeup.md) |
| 9 | Stack Day (opzionale · ephemeral) | ✅ | [writeup](phantom_track/phantom09/writeup.md) |
| 10 | The Harvest | ✅ | [writeup](phantom_track/phantom10/writeup.md) |
| 11 | Token Hunter | ✅ | [writeup](phantom_track/phantom11/writeup.md) |
| 12 | Ghost Install | ✅ | [writeup](phantom_track/phantom12/writeup.md) |
| 13 | Deep Roots | ✅ | [writeup](phantom_track/phantom13/writeup.md) |
| 14 | Shadow Mode | ✅ | [writeup](phantom_track/phantom14/writeup.md) |
| 15 | Clean Slate | ✅ | [writeup](phantom_track/phantom15/writeup.md) |
| 16 | The Tunnel | ✅ | [writeup](phantom_track/phantom16/writeup.md) |
| 17 | Internal Hunt | ✅ | [writeup](phantom_track/phantom17/writeup.md) |
| 18 | Credential Spray | 🔍 non ancora risolto | [writeup](phantom_track/phantom18/writeup.md) |
| 19 | Chain Reaction | 🔍 non ancora risolto | [writeup](phantom_track/phantom19/writeup.md) |
| 20 | Am I Contained? | 🔍 non ancora risolto | [writeup](phantom_track/phantom20/writeup.md) |
| 21 | The Breakout | 🔍 non ancora risolto | [writeup](phantom_track/phantom21/writeup.md) |
| 22 | Leaky Vessels | 🔍 non ancora risolto | [writeup](phantom_track/phantom22/writeup.md) |
| 23 | Docker API | 🔍 non ancora risolto | [writeup](phantom_track/phantom23/writeup.md) |
| 24 | Pod Games | 🔍 non ancora risolto | [writeup](phantom_track/phantom24/writeup.md) |
| 25 | Cluster Takeover | 🔍 non ancora risolto | [writeup](phantom_track/phantom25/writeup.md) |
| 26 | Cloud Reach | 🔍 non ancora risolto | [writeup](phantom_track/phantom26/writeup.md) |
| 27 | Toolsmith | 🔍 non ancora risolto | [writeup](phantom_track/phantom27/writeup.md) |
| 28 | The Heist | 🔍 non ancora risolto | [writeup](phantom_track/phantom28/writeup.md) |
| 29 | Wire Tap | 🔍 non ancora risolto | [writeup](phantom_track/phantom29/writeup.md) |
| 30 | Clean Exit | 🔍 non ancora risolto | [writeup](phantom_track/phantom30/writeup.md) |

</details>

## Mirage Track — 7/41 risolti

Sfruttamento di applicazioni web, dal recon lato client fino agli attacchi su AI e LLM.

| # | Livello | Stato | Writeup |
|---|---------|:-----:|---------|
| 0 | Nothing Is Secret | ✅ | [writeup](mirage_track/mirage00/writeup.md) |
| 1 | The Wire | ✅ | [writeup](mirage_track/mirage01/writeup.md) |
| 2 | Peel the Encoding | ✅ | [writeup](mirage_track/mirage02/writeup.md) |
| 3 | Source Maps Talk | ✅ | [writeup](mirage_track/mirage03/writeup.md) |
| 4 | Left in the Open | ✅ | [writeup](mirage_track/mirage04/writeup.md) |
| 5 | Trust the Client | ✅ | [writeup](mirage_track/mirage05/writeup.md) |
| 6 | Other People's Objects | ✅ | [writeup](mirage_track/mirage06/writeup.md) |

Il track arriva fino al livello 40. Le cartelle ci sono già; i writeup li aggiungo mano a mano che risolvo i livelli. In lavorazione adesso ci sono il 7 (Break the Logic), l'8 (Keys in the Bundle), il 9 (Over-Posting) e il 10 (Row-Level Lies), quest'ultimo ancora aperto.

## Crediti

Il lab è [BreachLab](https://breachlab.org). Se questi writeup ti sono serviti per costruire qualcosa che ti fa guadagnare, valuta una donazione: [breachlab.org/donate](https://breachlab.org/donate).

Se sei bloccato su un livello, chiedi nei thread di aiuto per track su Discord.
