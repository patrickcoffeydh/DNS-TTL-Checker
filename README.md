
# DNS‑TTL‑Checker  

A lightweight, multi‑threaded Python script that queries the authoritative DNS server for a given domain and prints the TTL of the requested record type.  
  
It can run against a single domain or a list of domains, support custom TTL thresholds, and emit warnings when the TTL differs from the expected value.  

---

## Table of Contents  
- [Features](#features)  
- [Prerequisites](#prerequisites)  
- [Installation](#installation)  
- [Usage](#usage)  
  - [Command‑line arguments](#command-line-arguments)  
  - [Examples](#examples)  
- [Threading behaviour](#threading-behaviour)  
- [Troubleshooting](#troubleshooting)  
- [Contributing](#contributing)  
- [License](#license)

---

## Features

| Feature | Description |
|---------|-------------|
| **Authoritative server lookup** | Determines the authoritative name‑servers for the root domain (e.g. `example.com`) and uses that for all queries. |
| **Record‑type flexibility** | Default is `CNAME`; can query any supported DNS record type (`A`, `AAAA`, `MX`, `TXT`, …). |
| **TTL validation** | Checks the TTL against a user‑supplied maximum (`--maxttl`). If the TTL is higher, or unknown, a warning is printed. |
| **Batch processing** | Accepts a list file with one domain per line, or a single domain via the CLI. |
| **Multithreaded** | Each domain is processed in its own thread, with a 1‑second stagger to avoid flooding the DNS servers or running out of connection sockets. |
| **Verbose mode** | Prints detailed diagnostic messages when `-v` is supplied. |
| **Portable** | Works on any system that can run Python 3.8+ and has the required dependencies. |

---

## Prerequisites

| Item | Minimum version |
|------|-----------------|
| Python | 3.8+ |
| `dnspython` | 2.2.0+ |

The script also imports a helper module `lib.common` which is a part of this library. The helper provides:

* `parseArgs(argv)` – parses command‑line arguments and returns a dictionary.  
* `fileToString(path)` – reads a file and returns its contents as a string.  

If you download the code make sure to clone the repo or otherwise grab `lib/common.py` and put it in the `lib/` directory.

---

## Installation

```bash
# Clone the repo
git clone https://github.com/patrickcoffeydh/DNS-TTL-Checker.git
cd DNS-TTL-Checker

# Optional: create a virtual environment
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

`requirements.txt`:

```
dnspython
```

---

## Usage

```bash
python main.py [options]
```

The script accepts the following command‑line options. For brevity, short and long flags are shown together.

| Flag | Short | Description | Required |
|------|-------|-------------|----------|
| `--domain` | `-d` | A single domain to check (e.g. `example.com`). | No (unless `--list` is omitted) |
| `--list` | `-l` | Path to a text file containing one domain per line. | No (unless `--domain` is omitted) |
| `--maxttl` | `-m` | Maximum acceptable TTL (in seconds). | No (defaults to 0 → no threshold) |
| `--warn` | `-w` | Emit warnings only (skip normal TTL info). | No |
| `--type` | `-t` | DNS record type to query (`CNAME` by default). | No |
| `--verbose` | `-v` | Enable debug/diagnostic output. | No |


---

### Examples

#### 1. Check a single domain

```bash
python main.py -d example.com
```

#### 2. Check a list of domains

Create `domains.txt`:

```
example.com
google.com
nonexistent.xyz
```

Run:

```bash
python main.py -l domains.txt
```

#### 3. Set a maximum TTL and only print warnings

```bash
python main.py -l domains.txt -m 86400 -w
```

#### 4. Query a different record type (MX)

```bash
python main.py -d example.com -t MX
```

#### 5. Verbose mode

```bash
python main.py -d example.com -v
```

---

## Threading behaviour

The script spawns one thread per domain. Threads are started with a 1‑second delay to avoid hammering the DNS resolvers.  
All threads join before the script exits, ensuring a clean finish.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `ModuleNotFoundError: No module named 'dns'` | `dnspython` not installed | `pip install dnspython` |
| `ModuleNotFoundError: No module named 'lib'` | Missing `lib/common.py` | Add the file or adjust clone the repo instead of downloading `main.py` by itself |
| TTL always shows `0` or “unknown” | The record does not exist, or TTL is hidden by some DNS provider | Verify DNS record in a public resolver (`dig @8.8.8.8 example.com CNAME`) |

---  

Happy DNS‑TTL checking! 🚀