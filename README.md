# BreachLab Writeups

Writeup tecnici dei wargame di [BreachLab](https://breachlab.org) — un campo di addestramento per tradecraft offensivo e difensivo reale.

![Ghost Track](https://img.shields.io/badge/Ghost_Track-23%2F23-brightgreen)
![Phantom Track](https://img.shields.io/badge/Phantom_Track-18%2F33-yellow)
![Mirage Track](https://img.shields.io/badge/Mirage_Track-7%2F41-orange)
![Doctrine](https://img.shields.io/badge/doctrine-no%20spoilers-blueviolet)

## Cos'è questo repo

Questo repository raccoglie i writeup dei livelli di BreachLab che ho risolto, in tre track: **Ghost** (fondamentali di enumerazione e credential hunting), **Phantom** (post-exploitation e tradecraft operativo) e **Mirage** (ricognizione e sfruttamento di applicazioni web).

Ogni writeup **insegna la tecnica**, non pubblica la soluzione: niente flag, password, chiavi o hash in chiaro. Solo il ragionamento, gli strumenti, e i passaggi che servono a chiunque per rifare il lavoro sulla propria istanza del livello.

## Struttura

Ogni livello vive nella propria cartella (`<track>/<track><N>/`) e contiene, in questo repo pubblico, un solo file:

```
ghost_track/
  ghost0/
    writeup.md      <- unico file pubblico: metodo, nessuno spoiler
phantom_track/
  phantom0/
    writeup.md
mirage_track/
  mirage0/
    writeup.md
```

Le note grezze (`notes.md`, log di terminale/output completi) e la versione integrale del writeup con i valori reali (`writeup.uncensored.md`) restano **locali** e non vengono mai pubblicate — sono escluse via `.gitignore`, in conformità alla dottrina "teach technique, never publish answers" di BreachLab.

## Dottrina

> **Teach technique, never publish answers.** Writeups and videos are welcome when they teach the method — not the literal password or flag.
>
> **Credit BreachLab.** A link back or a name-drop in the description. That's it.

Ogni writeup in questo repo rispetta questi due principi: spiega per intero la ricognizione, la vulnerabilità e i passaggi di sfruttamento, ma omette qualunque valore che permetterebbe di saltare il ragionamento.

## Ghost Track — 23/23 risolti

| # | Livello | Stato | Writeup |
|---|---------|:-----:|---------|
| 0 | — | ✅ | [writeup](ghost_track/ghost0/writeup.md) |
| 1 | — | ✅ | [writeup](ghost_track/ghost1/writeup.md) |
| 2 | — | ✅ | [writeup](ghost_track/ghost2/writeup.md) |
| 3 | — | ✅ | [writeup](ghost_track/ghost3/writeup.md) |
| 4 | Signal in the Noise | ✅ | [writeup](ghost_track/ghost4/writeup.md) |
| 5 | — | ✅ | [writeup](ghost_track/ghost5/writeup.md) |
| 6 | Ghost in the Machine | ✅ | [writeup](ghost_track/ghost6/writeup.md) |
| 7 | Lost in Translation | ✅ | [writeup](ghost_track/ghost7/writeup.md) |
| 8 | Something's Running | ✅ | [writeup](ghost_track/ghost8/writeup.md) |
| 9 | — | ✅ | [writeup](ghost_track/ghost9/writeup.md) |
| 10 | Odd Token Out | ✅ | [writeup](ghost_track/ghost10/writeup.md) |
| 11 | Unwrap the Stage | ✅ | [writeup](ghost_track/ghost11/writeup.md) |
| 12 | Harvested Key | ✅ | [writeup](ghost_track/ghost12/writeup.md) |
| 13 | — | ✅ | [writeup](ghost_track/ghost13/writeup.md) |
| 14 | TLS Only | ✅ | [writeup](ghost_track/ghost14/writeup.md) |
| 15 | — | ✅ | [writeup](ghost_track/ghost15/writeup.md) |
| 16 | Config Drift | ✅ | [writeup](ghost_track/ghost16/writeup.md) |
| 17 | Commands Only | ✅ | [writeup](ghost_track/ghost17/writeup.md) |
| 18 | Wrong User | ✅ | [writeup](ghost_track/ghost18/writeup.md) |
| 19 | Piece by Piece | ✅ | [writeup](ghost_track/ghost19/writeup.md) |
| 20 | Cron Discovery | ✅ | [writeup](ghost_track/ghost20/writeup.md) |
| 21 | — | ✅ | [writeup](ghost_track/ghost21/writeup.md) |
| 22 | Graduation | ✅ | [writeup](ghost_track/ghost22/writeup.md) |

## Phantom Track — 18/33 risolti

<details open>
<summary>Espandi tabella</summary>

| # | Livello | Stato | Writeup |
|---|---------|:-----:|---------|
| 0 | Recon Gateway | ✅ | [writeup](phantom_track/phantom0/writeup.md) |
| 1 | — | ✅ | [writeup](phantom_track/phantom1/writeup.md) |
| 2 | Sudo Games | ✅ | [writeup](phantom_track/phantom2/writeup.md) |
| 3 | — | ✅ | [writeup](phantom_track/phantom3/writeup.md) |
| 4 | Misplaced Power | ✅ | [writeup](phantom_track/phantom4/writeup.md) |
| 5 | — | ✅ | [writeup](phantom_track/phantom5/writeup.md) |
| 6 | — | ✅ | [writeup](phantom_track/phantom6/writeup.md) |
| 7 | — | ✅ | [writeup](phantom_track/phantom7/writeup.md) |
| 8 | Live Injection | ✅ | [writeup](phantom_track/phantom8/writeup.md) |
| 9 | Stack Day | ✅ | [writeup](phantom_track/phantom9/writeup.md) |
| 10 | The Harvest | ✅ | [writeup](phantom_track/phantom10/writeup.md) |
| 11 | Token Hunter | ✅ | [writeup](phantom_track/phantom11/writeup.md) |
| 12 | — | ✅ | [writeup](phantom_track/phantom12/writeup.md) |
| 13 | — | ✅ | [writeup](phantom_track/phantom13/writeup.md) |
| 14 | Shadow Mode | ✅ | [writeup](phantom_track/phantom14/writeup.md) |
| 15 | — | ✅ | [writeup](phantom_track/phantom15/writeup.md) |
| 16 | — | ✅ | [writeup](phantom_track/phantom16/writeup.md) |
| 17 | Internal Hunt | ✅ | [writeup](phantom_track/phantom17/writeup.md) |
| 18 | — | 🔍 non ancora risolto | [writeup](phantom_track/phantom18/writeup.md) |
| 19 | — | 🔍 non ancora risolto | [writeup](phantom_track/phantom19/writeup.md) |
| 20 | — | 🔍 non ancora risolto | [writeup](phantom_track/phantom20/writeup.md) |
| 21 | — | 🔍 non ancora risolto | [writeup](phantom_track/phantom21/writeup.md) |
| 22 | — | 🔍 non ancora risolto | [writeup](phantom_track/phantom22/writeup.md) |
| 23 | — | 🔍 non ancora risolto | [writeup](phantom_track/phantom23/writeup.md) |
| 24 | — | 🔍 non ancora risolto | [writeup](phantom_track/phantom24/writeup.md) |
| 25 | — | 🔍 non ancora risolto | [writeup](phantom_track/phantom25/writeup.md) |
| 26 | — | 🔍 non ancora risolto | [writeup](phantom_track/phantom26/writeup.md) |
| 27 | — | 🔍 non ancora risolto | [writeup](phantom_track/phantom27/writeup.md) |
| 28 | — | 🔍 non ancora risolto | [writeup](phantom_track/phantom28/writeup.md) |
| 29 | — | 🔍 non ancora risolto | [writeup](phantom_track/phantom29/writeup.md) |
| 30 | — | 🔍 non ancora risolto | [writeup](phantom_track/phantom30/writeup.md) |
| 31 | — | 🔍 non ancora risolto | [writeup](phantom_track/phantom31/writeup.md) |
| 32 | — | 🔍 non ancora risolto | [writeup](phantom_track/phantom32/writeup.md) |

</details>

## Mirage Track — 7/41 risolti

| # | Livello | Stato | Writeup |
|---|---------|:-----:|---------|
| 0 | — | ✅ | [writeup](mirage_track/mirage0/writeup.md) |
| 1 | — | ✅ | [writeup](mirage_track/mirage1/writeup.md) |
| 2 | — | ✅ | [writeup](mirage_track/mirage2/writeup.md) |
| 3 | Nimbus AI — Dashboard | ✅ | [writeup](mirage_track/mirage3/writeup.md) |
| 4 | Nimbus AI | ✅ | [writeup](mirage_track/mirage4/writeup.md) |
| 5 | — | ✅ | [writeup](mirage_track/mirage5/writeup.md) |
| 6 | — | ✅ | [writeup](mirage_track/mirage6/writeup.md) |

*Mirage arriva fino al livello 40: le cartelle sono già pronte, i writeup verranno aggiunti man mano che i livelli vengono risolti.*

## Crediti

Lab: [BreachLab](https://breachlab.org). Se questi writeup ti hanno aiutato a costruire qualcosa che genera revenue, considera una donazione: [breachlab.org/donate](https://breachlab.org/donate).

Se sei bloccato su un livello, usa i thread di aiuto per track su Discord — non chiedere spoiler qui.
