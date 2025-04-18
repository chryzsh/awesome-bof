# Reference: BOF Loaders Catalog

This catalog summarizes known BOF (Beacon Object File) loaders and runtimes. These tools help you execute, test, or embed `.o` object files in a variety of contexts — including inside and outside of C2 frameworks, across different platforms, and with different levels of API emulation. Each loader has its own API quirks and execution model. Always test your BOF in the target C2 to ensure compatibility.

---

## 🧰 Native Loaders (within C2 frameworks)

| Loader | C2 Framework | Platform | Async Support | Description |
|--------|--------------|----------|---------------|-------------|
| Cobalt Strike | Cobalt Strike (v4.1+) | Windows | ✅ via `async-execute` | Originator of BOFs with full API support and extensive documentation |
| Sliver | Sliver | Win/Linux | ❌ | Uses `bof upload` and `bof execute` commands with `extension.json` for registration |
| Havoc | Havoc (Demon agent) | Windows | ❌ | Supports inline execution and script-based BOF registration |
| Meterpreter | Metasploit | Windows | ❌ | Requires `bofloader` extension with limited Beacon API compatibility |
| OST (Outflank) | Outflank C2 | Windows | ❌ | Integrated BOF loader used in stealthy tradecraft operations |
| Brute Ratel | Brute Ratel | Windows | ✅ | Implements high-fidelity BOF support with asynchronous execution |
| Nighthawk | Nighthawk | Windows | ✅ | Private commercial C2 with high-performance BOF runtime |
| Mythic (Xenon) | Mythic | Windows | ❌ | Xenon agent supports `.o` execution via `execute_bof` command |

---

## 🧪 Standalone Loaders (Local Testing & Debugging)

| Tool | Language  | Description |
|------|-----------|-------------|
| [COFFLoader](https://github.com/trustedsec/COFFLoader) | C | CLI tool to run `.o` files outside Cobalt Strike for testing and development |
| [BOF.NET](https://github.com/CCob/BOF.NET) | C# / Native  | Embeds .NET runtime within BOFs to enable managed code execution |
| [BOF-PE](https://github.com/NetSPI/BOF-PE) | C / C++ | Portable Executable format for BOFs with extended capabilities and improved compatibility |
| [ELFLoader](https://github.com/trustedsec/ELFLoader) | C | Runs ELF `.o` files in-memory using libc/dlsym for Linux/macOS testing |
| [Coffee](https://github.com/hakaioffsec/coffee) | Rust  | Coffee is a custom implementation of the original Cobalt Strike's beacon_inline_execute. It is written in Rust and supports most of the features of the Cobalt Strike compatibility layer.|
| [CoffeeLdr](https://github.com/Cracked5pider/CoffeeLdr) | C | CoffeeLdr is a loader for so called Beacon Object Files.  |
| [ldr](https://github.com/yamakadi/ldr) | Rust | Unsuccessful attempt at a Rust BOF/COFF loader.|
| [COFF-Loader](https://github.com/Ap3x/COFF-Loader) | C++ | This is a reimplementation of TrustedSec COFF Loader.|
| [Invoke-Bof](https://github.com/airbus-cert/Invoke-Bof) | PowerShell | A PowerShell script to run BOFs. |
| [pybof](https://github.com/rkbennett/pybof) | Python | Python based BOF loader |
| [python-bof-runner](https://github.com/naksyn/python-bof-runner) | Python | Python-based BOF runner using inline shellcode injection |
| [RunOF](https://github.com/nettitude/RunOF) | .NET | Running BOFs in .NET |
| [NiCOFF](https://github.com/frkngksl/NiCOFF) | Nim | COFF and BOF file loader written in Nim.
| [COFFLoader2](https://github.com/Yaxser/COFFLoader2) | C | Rewrite of the TrustedSec COFF loader.
| [Jormungandr](https://github.com/Idov31/Jormungandr) | C++ | a kernel implementation of a COFF loader. 
| [bof-launcher](https://github.com/The-Z-Labs/bof-launcher) | Zig and C | Beacon Object File (BOF) launcher - library for executing BOF files in C/C++/Zig applications.
| [CS2BR BOF](https://github.com/NVISOsecurity/cs2br-bof) | C |  CS2BR implements a compatibility-layer that make CS BOFs use the BRC4 API. |
| [nim-lazy-bof](https://github.com/zimnyaa/nim-lazy-bof) | Nim | Nim port of Sliver's BOF loader |
| [coff_loader](https://github.com/soheil-01/coff_loader) | Zig | Experimental COFF loader for Cobalt Strike BOFs |
| [BOF2shellcode](https://github.com/FalconForceTeam/BOF2shellcode) | Convert BOFs into raw shellcode |

---



---

## 📚 Contribution
Want to add another loader or tool? Open a PR!