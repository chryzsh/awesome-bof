# Explanation: BOF Loaders and Execution Engines

BOF loaders are specialized programs or modules that know how to load and execute Beacon Object Files (.o files) outside or inside a C2 framework. While BOFs are most commonly used in Cobalt Strike, a growing number of loaders enable BOFs to be executed:

- Outside of a Beacon context (e.g. for debugging)
- Inside custom C2 agents
- On Linux or cross-platform implants

This article explores popular BOF loaders and execution strategies.

---

## 🧰 What is a BOF Loader?
A BOF loader is a runtime or tool that:
- Parses a COFF object file (.o)
- Resolves external function imports (e.g. `BeaconPrintf`, `kernel32!CreateFileA`, etc.)
- Allocates memory and relocates code
- Calls the BOF entrypoint function (typically `go()`)

---

## 🔄 Native vs External BOF Execution

| Loader Type | Description                                | Example                 |
|-------------|--------------------------------------------|-------------------------|
| **Internal**| Built into a C2 framework                  | Cobalt Strike, Sliver   |
| **External**| Standalone tool to test or host BOFs       | COFFLoader, BOF.NET     |
| **Cross-Platform** | Loads ELF/COFF for Linux/Mac implants | ELFLoader, Linux BOFs   |

---

## 🔧 Notable BOF Loaders

### 🐝 **Cobalt Strike (Native Loader)**
- Uses a proprietary COFF parser
- Maps functions via `beacon.h`-defined APIs
- Supports `inline-execute` to run BOFs directly
- Loads BOFs into Beacon’s memory and executes them on its thread

### 📦 **COFFLoader (TrustedSec)**
- Standalone command-line tool to execute BOFs outside Cobalt Strike
- Implements core Beacon APIs (output, argument parsing, memory)
- Great for testing BOFs without launching a full C2
- [COFFLoader on GitHub](https://github.com/trustedsec/COFFLoader)

### 🧪 **BOF.NET**
- Allows writing BOFs in C#/.NET
- Embeds a .NET runtime inside a native BOF loader
- Supports a `BeaconObject` interface that gets called like a normal BOF
- [BOF.NET on GitHub](https://github.com/CCob/BOF.NET)

### 🐧 **ELFLoader (TrustedSec)**
- Linux-native loader for `.o` (ELF) files
- Useful for testing Linux-based BOFs
- Dynamically links symbols via libc
- Compatible with x86 and x86_64 Linux
- [ELFLoader on GitHub](https://github.com/trustedsec/ELFLoader)

### 🧬 **bof-launcher and cli4bofs (Z-Labs)**
- Allows writing BOFs in C and [Zig](https://ziglang.org/)
- Supports Windows COFF (x86_64, x86) and Linux ELF (x86_64, x86, arm, aarch64)
- Provides reusable library with simple [C API for launching BOFs](https://github.com/The-Z-Labs/bof-launcher/blob/main/bof-launcher/src/bof_launcher_api.h)
- cli4bofs is standalone command-line tool for launching, injecting and organizing BOFs outside Cobalt Strike
- Supports `exec` and `inject` commands to run/inject BOFs directly
- [bof-launcher on GitHub](https://github.com/The-Z-Labs/bof-launcher)
- [cli4bofs on GitHub](https://github.com/The-Z-Labs/cli4bofs)

### 🧬 **Custom Agent Loaders (e.g., Xenon, Havoc, Brute Ratel)**
- Many modern C2s implement their own BOF loaders:
  - **Xenon** (Mythic) — parses and executes `.o` files directly
  - **Havoc** — parses and executes `.o` files directly
  - **Brute Ratel** — ships with its own loader
  - **Outflank C2** — ships with its own loader
- Most follow the CS convention of looking for `go(char*, int)`

---

## Developing your own loader
It is possible to write your own loader. Some guidance has been written on this specifically, please refer to:
- [Reference: BOF Loaders Catalog](../reference/loaders-catalog.md) for some reference projects, and
- [Reference: Blog Posts and Research on BOF Development](../reference/loaders-catalog.md) which contains articles on BOF and COFF loader development. 
- [Reference: BOF Development Training and Courses](../reference/bof-training-courses.md) which lists some training courses that involve loader development.

## 🧠 Takeaways
- BOF loaders are key to portability and flexibility
- COFFLoader and ELFLoader are ideal for testing BOFs outside of C2
- C2s implement their own BOF engines — be aware of differences in APIs and argument handling
- BOF.NET introduces a high-level approach for .NET developers

---

## 🔗 Related articles
- [`how-to/setup-visual-studio-for-bof-development.md`](../how-to/setup-visual-studio-bof.md)
- [`reference/loaders-catalog.md`](../reference/loaders-catalog.md)
