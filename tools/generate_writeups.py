#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = "<!-- breachlab-note-format:v1 -->"
NOTE_NAMES = {"notes.md", "note.md", "notes1.md", "noted.md"}
TRACK_LABELS = {
    "ghost_track": "Ghost Track",
    "phantom_track": "Phantom Track",
    "mirage_track": "Mirage Track",
}

SECRET_WORDS = re.compile(
    r"(?i)(password|passwd|credential|credentials|flag|token|secret|api[_-]?digest|runtime[_-]?token|private key|verification code|verify-code|next_environment|key\":|unlock-)"
)
HASH_LINE = re.compile(r"^(root|daemon|bin|sys|sync|games|man|lp|mail|news|uucp|proxy|www-data|backup|list|irc|gnats|nobody|_apt|systemd-[^:]+|redis|tcpdump|sshd|phantom\d+|ghost\d+|flagkeeper\d+):")
LONG_SECRET = re.compile(r"(?<![A-Za-z0-9_/+=.-])([A-Za-z0-9_/+=.-]{18,})(?![A-Za-z0-9_/+=.-])")
JSON_SECRET_FIELD = re.compile(r'("(?:password|passwd|flag|token|secret|key|user|url)"\s*:\s*)"[^"]*"', re.I)
ENV_SECRET = re.compile(r"^(export\s+(?:API_DIGEST|RUNTIME_TOKEN|TRACE_SALT|CACHE_SEED|SESSION_HASH)\s*=).*$", re.I)
ASSIGN_SECRET = re.compile(r"((?:password|passwd|flag|token|secret|key|credential)\s*[:=]\s*)\S+", re.I)

COMMAND_RE = re.compile(
    r"^(?:sudo\b|ssh\b|cat\b|ll\b|ls\b|find\b|grep\b|ps\b|id\b|whoami\b|groups\b|env\b|printenv\b|base64\b|xxd\b|hashcat\b|john\b|curl\b|fetch\(|python3?\b|gcc\b|chmod\b|cd\b|echo\b|unset\b|export\b|tar\b|strings\b|file\b|readelf\b|objdump\b|gdb\b|nc\b|openssl\b|git\b|crontab\b|/[^\s]+)"
)
HTML_START = re.compile(r"^\s*<(?:!doctype\s+html|html\b|head\b|body\b|main\b|style\b|script\b|div\b)", re.I)
JSON_START = re.compile(r"^\s*[\[{]")
C_START = re.compile(r"^\s*(?:#include\b|#ifndef\b|#define\b|__attribute__\b|int\s+main\b|void\s+\w+\s*\(|FILE\s*\*)")
PY_START = re.compile(r"^\s*(?:import\s+\w+|from\s+\w+\s+import|def\s+\w+\(|while\s+True:|libc\s*=|secret\s*=)")

TECHNIQUE_KEYWORDS = [
    ("LD_PRELOAD", "abuso controllato di variabili d'ambiente preservate da sudo"),
    ("env_keep", "analisi della policy sudo e delle variabili ereditate"),
    ("/proc", "enumerazione di processi e memoria tramite procfs"),
    ("ptrace", "ispezione runtime con strumenti di debugging"),
    ("base64", "decodifica a strati e validazione del dato prima dell'uso"),
    ("/etc/shadow", "lettura autorizzata di database account e cracking offline"),
    ("hashcat", "cracking offline con dizionari, senza brute force sull'infrastruttura"),
    ("cron", "revisione di job pianificati e permessi associati"),
    ("capability", "analisi delle capability Linux e del loro impatto"),
    ("sudo -l", "lettura della superficie concessa da sudo prima di agire"),
    ("git", "ricostruzione di storia e artefatti da repository locali"),
    ("fetch(\"/unlock\"", "interazione con endpoint web e formato richiesto dall'API"),
    ("/etc/passwd", "enumerazione account e superfici leggibili"),
]


def note_files() -> list[Path]:
    return sorted(
        path for path in ROOT.rglob("*.md")
        if path.name in NOTE_NAMES and path.name not in {"writeup.clean.md", "writeup.censored.md"}
    )


def labels(path: Path) -> tuple[str, str, str]:
    rel = path.relative_to(ROOT)
    track_dir = rel.parts[0]
    level_dir = rel.parts[1]
    track_label = TRACK_LABELS.get(track_dir, track_dir.replace("_", " ").title())
    match = re.match(r"([A-Za-z]+)(\d+)$", level_dir)
    level_label = f"{match.group(1).title()} {match.group(2)}" if match else level_dir.replace("_", " ").title()
    return track_label, level_label, rel.as_posix()


def extract_raw(path: Path) -> str:
    text = path.read_text(errors="replace")
    if "````text\n" in text:
        start = text.index("````text\n") + len("````text\n")
        end = text.rfind("\n````")
        if end > start:
            return text[start:end].strip("\n")
    if "_Nessuna nota registrata._" in text:
        return ""
    return text.strip("\n")


def find_mission(raw: str) -> str | None:
    patterns = [
        r"\[\s*(?:Phantom\s*·\s*)?Level\s+[^\]]+\]\s+([^\n]+)",
        r"MISSION:\s*([^\n]+)",
        r"<title>(.*?)</title>",
        r"<h1>(.*?)</h1>",
    ]
    for pattern in patterns:
        match = re.search(pattern, raw, re.I)
        if match:
            value = re.sub(r"\s+", " ", match.group(1)).strip()
            value = re.sub(r"\s{2,}.*$", "", value).strip()
            if value:
                return value
    return None


def find_goal(raw: str) -> str:
    goal_lines = []
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith(("Goal:", "Full brief:", "MISSION:")):
            goal_lines.append(stripped)
        elif "Goal:" in stripped:
            goal_lines.append(stripped)
    if goal_lines:
        return " ".join(goal_lines[:2])
    if raw.strip():
        return "Ricostruire il percorso risolutivo dagli appunti raccolti nel livello."
    return "Nessuna procedura registrata in questa nota."


def infer_techniques(raw: str) -> list[str]:
    found = []
    low = raw.lower()
    for needle, description in TECHNIQUE_KEYWORDS:
        if needle.lower() in low and description not in found:
            found.append(description)
    if not found and raw.strip():
        found.append("enumerazione manuale, lettura degli indizi e verifica incrementale")
    return found


def strip_banner(lines: list[str]) -> list[str]:
    cleaned = []
    banner_chars = set("█╗╔╝═║╚─· ")
    skipping = True
    for line in lines:
        stripped = line.strip()
        if skipping and (not stripped or set(stripped) <= banner_chars or "breachlab.org" in stripped.lower() or "profile" in stripped.lower()):
            continue
        skipping = False
        cleaned.append(line.rstrip())
    return cleaned


def guess_lang(block: list[str]) -> str:
    sample = "\n".join(block[:8]).strip()
    first = block[0].strip() if block else ""
    if not sample:
        return "text"
    if HTML_START.search(first) or "<html" in sample.lower() or "</html>" in sample.lower():
        return "html"
    if first.startswith("fetch(") or "JSON.stringify" in sample or "Promise" in sample:
        return "javascript"
    if JSON_START.search(first):
        try:
            json.loads("\n".join(block))
            return "json"
        except Exception:
            if first.startswith("{") or first.startswith("["):
                return "json"
    if C_START.search(first) or "#include" in sample:
        return "c"
    if PY_START.search(first) or sample.startswith("```python"):
        return "python"
    if COMMAND_RE.search(first):
        return "bash"
    return "text"


def chunk_raw(raw: str) -> list[tuple[str, str]]:
    lines = strip_banner(raw.splitlines())
    chunks: list[tuple[str, str]] = []
    prose: list[str] = []

    def flush_prose() -> None:
        nonlocal prose
        text = "\n".join(prose).strip("\n")
        if text:
            chunks.append((guess_lang(prose), text))
        prose = []

    index = 0
    while index < len(lines):
        line = lines[index].rstrip()
        stripped = line.strip()

        if not stripped:
            prose.append(line)
            index += 1
            continue

        if HTML_START.search(stripped):
            flush_prose()
            block = [line]
            index += 1
            while index < len(lines):
                block.append(lines[index].rstrip())
                if "</html>" in lines[index].lower():
                    index += 1
                    break
                index += 1
            chunks.append(("html", "\n".join(block).strip("\n")))
            continue

        if stripped.startswith("fetch("):
            flush_prose()
            block = [line]
            index += 1
            while index < len(lines):
                next_line = lines[index].rstrip()
                if not next_line.strip() and block and block[-1].strip() == "}":
                    break
                block.append(next_line)
                if next_line.strip() in {"})", "});"}:
                    index += 1
                    break
                index += 1
            chunks.append(("javascript", "\n".join(block).strip("\n")))
            continue

        if stripped.startswith("{") or stripped.startswith("["):
            flush_prose()
            block = [line]
            depth = stripped.count("{") + stripped.count("[") - stripped.count("}") - stripped.count("]")
            index += 1
            while index < len(lines) and depth > 0:
                next_line = lines[index].rstrip()
                block.append(next_line)
                depth += next_line.count("{") + next_line.count("[") - next_line.count("}") - next_line.count("]")
                index += 1
            chunks.append(("json", "\n".join(block).strip("\n")))
            continue

        if re.search(r"cat\s+<<\s*['\"]?EOF['\"]?\s*>\s*\S+\.c", stripped):
            flush_prose()
            chunks.append(("bash", line))
            index += 1
            block = []
            while index < len(lines):
                next_line = lines[index].rstrip()
                if next_line.strip() == "EOF":
                    index += 1
                    break
                block.append(next_line)
                index += 1
            if block:
                chunks.append(("c", "\n".join(block).strip("\n")))
            continue

        if C_START.search(stripped):
            flush_prose()
            block = [line]
            index += 1
            while index < len(lines):
                next_line = lines[index].rstrip()
                if COMMAND_RE.search(next_line.strip()) and not next_line.startswith((" ", "\t")):
                    break
                block.append(next_line)
                index += 1
            chunks.append(("c", "\n".join(block).strip("\n")))
            continue

        if PY_START.search(stripped):
            flush_prose()
            block = [line]
            index += 1
            while index < len(lines):
                next_line = lines[index].rstrip()
                if COMMAND_RE.search(next_line.strip()) and not next_line.startswith((" ", "\t")):
                    break
                block.append(next_line)
                index += 1
            chunks.append(("python", "\n".join(block).strip("\n")))
            continue

        if COMMAND_RE.search(stripped):
            flush_prose()
            block = [line]
            index += 1
            while index < len(lines):
                next_line = lines[index].rstrip()
                next_stripped = next_line.strip()
                if HTML_START.search(next_stripped) or next_stripped.startswith(("fetch(", "{", "[")) or C_START.search(next_stripped) or PY_START.search(next_stripped):
                    break
                if COMMAND_RE.search(next_stripped) and block and not block[-1].strip():
                    break
                block.append(next_line)
                index += 1
            chunks.append(("bash", "\n".join(block).strip("\n")))
            continue

        prose.append(line)
        index += 1

    flush_prose()
    return [(lang, text) for lang, text in chunks if text.strip()]


def redact_line(line: str) -> str:
    stripped = line.strip()
    line = JSON_SECRET_FIELD.sub(r'\1"<REDACTED>"', line)
    if HASH_LINE.match(stripped):
        account = stripped.split(":", 1)[0]
        return f"{account}:<REDACTED_HASH_FIELDS>"
    if ENV_SECRET.match(line):
        return ENV_SECRET.sub(r"\1<REDACTED>", line)
    if SECRET_WORDS.search(line):
        line = ASSIGN_SECRET.sub(r"\1<REDACTED>", line)
        line = re.sub(r"(token\s*:\s*)\"[^\"]*\"", r"\1\"<REDACTED_TOKEN>\"", line, flags=re.I)
        line = re.sub(r"(<code\s+id=\"verify-code\">)[^<]+", r"\1<REDACTED_CODE>", line, flags=re.I)
        line = re.sub(r"(code is wrapped.*$)", "verification code details redacted.", line, flags=re.I)
        line = re.sub(r"unlock-[A-Za-z0-9_-]+", "unlock-<REDACTED>", line)
        line = LONG_SECRET.sub("<REDACTED>", line)
        return line
    if re.fullmatch(r"[A-Za-z0-9+/=_-]{12,}", stripped):
        return "<REDACTED_SECRET>"
    return line


def redact_text(text: str) -> str:
    redacted = [redact_line(line) for line in text.splitlines()]
    final = []
    redact_next = False
    for line in redacted:
        if redact_next and line.strip() and not COMMAND_RE.search(line.strip()):
            final.append("<REDACTED_SECRET>")
            redact_next = False
            continue
        final.append(line)
        if re.search(r"(?i)^\s*cat\s+(?:credentials?|.*flag.*|.*secret.*)", line):
            redact_next = True
    return "\n".join(final)


def fence(lang: str, text: str) -> str:
    fence_marks = "````" if "```" in text else "```"
    return f"{fence_marks}{lang}\n{text.rstrip()}\n{fence_marks}"


def render(path: Path, censored: bool) -> str:
    track_label, level_label, rel = labels(path)
    raw = extract_raw(path)
    title = f"{track_label} - {level_label}"
    mission = find_mission(raw)
    goal = find_goal(raw)
    techniques = infer_techniques(raw)
    source_label = "censored" if censored else "clean"

    lines = [
        f"# {title}",
        "",
        "## Sommario",
        "",
        f"- Track: {track_label}",
        f"- Livello: {level_label}",
        f"- Fonte appunti: `{rel}`",
        f"- Variante: `{source_label}`",
    ]
    if mission:
        lines.append(f"- Missione: {redact_text(mission) if censored else mission}")
    lines.extend([
        "",
        "## Obiettivo",
        "",
        redact_text(goal) if censored else goal,
        "",
        "## Tecniche usate",
        "",
    ])
    if techniques:
        lines.extend(f"- {item}" for item in techniques)
    else:
        lines.append("- Nessuna tecnica annotata.")

    if censored:
        lines.extend([
            "",
            "## Nota di pubblicazione",
            "",
            "Questa versione e' pensata per GitHub e segue la dottrina BreachLab: spiega il metodo, ma rimuove password, flag, token, chiavi, hash crackabili e valori che permetterebbero di saltare il ragionamento.",
        ])

    lines.extend([
        "",
        "## Procedura",
        "",
    ])

    if not raw.strip():
        lines.append("_Nessuna nota registrata per questo livello._")
    else:
        chunks = chunk_raw(raw)
        for index, (lang, text) in enumerate(chunks, start=1):
            material = redact_text(text) if censored else text
            if not material.strip():
                continue
            heading = "Passo" if lang in {"bash", "javascript", "html", "json", "c", "python"} else "Evidenza"
            lines.extend([
                f"### {heading} {index}",
                "",
                fence(lang, material),
                "",
            ])

    if lines[-1] != "":
        lines.append("")
    lines.extend([
        "## Conclusione operativa",
        "",
    ])
    if raw.strip():
        if censored:
            lines.append("Il livello si chiude validando la tecnica individuata e mantenendo fuori dal writeup pubblico ogni valore risolutivo diretto.")
        else:
            lines.append("Il livello si chiude con le evidenze complete conservate per uso personale e revisione privata.")
    else:
        lines.append("Non ci sono evidenze sufficienti per ricostruire una soluzione completa.")
    lines.extend([
        "",
        "## Crediti",
        "",
        "Lab: BreachLab. Pubblicare sempre con credito al progetto e senza spoiler risolutivi.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    files = note_files()
    for path in files:
        path.with_name("writeup.clean.md").write_text(render(path, censored=False), encoding="utf-8")
        path.with_name("writeup.censored.md").write_text(render(path, censored=True), encoding="utf-8")
    print(f"Generati {len(files) * 2} writeup da {len(files)} note.")


if __name__ == "__main__":
    main()
