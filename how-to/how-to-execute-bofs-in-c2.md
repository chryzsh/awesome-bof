# How-To: Run BOFs in Common C2 Frameworks

This guide walks through how to execute Beacon Object Files (BOFs) across major C2 frameworks. While BOFs were originally built for Cobalt Strike, many open-source and commercial frameworks have since adopted them. Each C2 has different loading mechanisms, argument handling, and feature suppor. Always consult your C2 documentation to verify current syntax and API support.

---

## 🐝 Cobalt Strike

### 🔧 Setup
- BOFs are supported natively
- Requires `inline-execute` or `async-execute`

### ▶️ Run a BOF
```powershell
inline-execute /path/to/bof.o "arg1 arg2"
```

### ✅ Async Mode (v4.11+)
See [How-To: Run BOFs asynchronously with `async-execute` in Cobalt Strike](../how-to/how-to-async-execute.md)

---

## 🐺 Sliver C2

### 🔧 Sliver BOF support
- Sliver supports BOFs via extensions
- Official extensions can be installed with `Armory`
- Requires 32-bit and 64-bit `.o` files
- Commands must be registered with `extension.json`

### ▶️ Run a BOF in Sliver
> This article is incomplete. Refer to the documentation for details on how to execute BOFs.

### References
- [Armory (Sliver Docs)](https://sliver.sh/docs?name=Armory)
- [Sliver BOF (Redteaming.org)](https://www.redteaming.org/sliverbof.html)
- [Feeding Sliver — Extension Guide (Medium)](https://medium.com/@l4rry/feeding-sliver-extension-guide-1c14fae42a2a)

---

## 👾 Havoc Framework

### 🔧 Setup
- Havoc supports inline BOF execution
- Use `.register_extension` to define commands (GUI or script)

### ▶️ Run a BOF
```bash
inline-execute /path/to/bof.o "arg1 arg2"
```

---

## 🧬 Meterpreter (Metasploit)

### 🔧 Setup
- Load the `bofloader` extension
- Ensure `.o` file is compatible with CS-style BOFs

### ▶️ Run a BOF
Examples with and without arguments.
```bash
meterpreter > load bofloader
meterpreter > execute_bof /path/to/bof.o
meterpreter > execute_bof --format-string Zs /path/to/bof.o c:\\ 0
```

### References
- [Operator's Guide to the Meterpreter BOFLoader](https://trustedsec.com/blog/operators-guide-to-the-meterpreter-bofloader)

---

## 🎩 Outflank OST

### 🔧 Setup
- BOFs integrated as part of OST internal toolset
- Can be executed with `execute_bof`
- BOFs are exposed through Python scripts.
- BOFs are uploaded to the implant from a browser window (not specified by path like with CS).

### ▶️ Run a BOF
```powershell
execute_bof <upload BOF>
execute_bof Zz arg1 arg2 <upload BOF>
```

> No direct `inline_execute`. Uses internal resolution and configuration.

---

## 🧠 Mythic (Xenon Agent)
TODO

See [Forge on Github](https://github.com/MythicAgents/forge)

---

## 🦊 Brute Ratel (BRC4)
TODO

---

## 🦉 Nighthawk
TODO

---

Want to add usage for another C2? Submit a PR!
