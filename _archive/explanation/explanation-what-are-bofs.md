# Explanation: What is a BOF?

A **BOF** — or **Beacon Object File** — is a compiled **COFF (Common Object File Format)** file designed to be run in-memory by a post-exploitation agent like Cobalt Strike's Beacon or Havoc's Demon. BOFs are small, self-contained C programs that execute directly inside a live process, inheriting its memory, permissions, and execution context.

---

## 🧠 Key Characteristics

- 🔧 **Compiled from C** using a Windows cross-compiler (e.g., MinGW)
- 🧵 **Executed in-memory**, inside the agent's thread or via a job system
- 🕵️‍♂️ **Stealthy** — no disk writes, no new process creation
- ⚡ **Fast and lightweight**, ideal for small, purpose-built tasks

---

## 💡 What Makes BOFs Special?

BOFs provide red teamers and malware developers with a way to extend C2 functionality without writing full post-exploitation modules or launching separate binaries. They enable fileless execution of complex logic using minimal memory and almost no forensic artifacts.

Originally popularized in **Cobalt Strike**, BOFs have now been adopted by C2 frameworks like:
- **Brute Ratel**
- **Havoc**
- **Sliver**
- **Mythic (Xenon)**
- **Meterpreter** (via extensions)

Each framework has its own method of loading and executing BOFs, but the core model remains consistent.

---

## 📦 What BOFs Are Used For
- Credential dumping (e.g., LSASS memory access)
- Enumeration and situational awareness
- Process injection and syscall execution
- Evasion (e.g., AMSI bypasses, memory unhooking)
- Persistence techniques

---

## ✅ Summary
BOFs are a powerful, stealthy, and increasingly cross-platform way to embed post-exploitation logic into an existing C2 agent. With growing support across frameworks, they’ve become a fundamental part of modern red team operations.

For how BOFs are written, parsed, and executed, check out:
- [`explanation/bof-internals-explained.md`](../explanation/bof-internals-explained.md)
- [`explanation/bof-argument-parsing.md`](../explanation/bof-argument-parsing.md)

