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

| Tool | Language  | Description | Stars | Last commit |
|------|-----------|-------------|-------|-------------|
| [COFFLoader](https://github.com/trustedsec/COFFLoader) | C | CLI tool to run `.o` files outside Cobalt Strike for testing and development | ![](https://img.shields.io/github/stars/trustedsec/COFFLoader?label=&style=flat) | ![](https://img.shields.io/github/last-commit/trustedsec/COFFLoader?label=&style=flat) 
| [BOF.NET](https://github.com/CCob/BOF.NET) | C# / Native  | Embeds .NET runtime within BOFs to enable managed code execution | ![](https://img.shields.io/github/stars/CCob/BOF.NET?label=&style=flat) | ![](https://img.shields.io/github/last-commit/CCob/BOF.NET?label=&style=flat) 
| [BOF-PE](https://github.com/NetSPI/BOF-PE) | C / C++ | Portable Executable format for BOFs with extended capabilities and improved compatibility | ![](https://img.shields.io/github/stars/NetSPI/BOF-PE?label=&style=flat) | ![](https://img.shields.io/github/last-commit/NetSPI/BOF-PE?label=&style=flat) 
| [ELFLoader](https://github.com/trustedsec/ELFLoader) | C | Runs ELF `.o` files in-memory using libc/dlsym for Linux/macOS testing | ![](https://img.shields.io/github/stars/trustedsec/ELFLoader?label=&style=flat) | ![](https://img.shields.io/github/last-commit/trustedsec/ELFLoader?label=&style=flat) 
| [Coffee](https://github.com/hakaioffsec/coffee) | Rust  | Coffee is a custom implementation of the original Cobalt Strike's beacon_inline_execute. It is written in Rust and supports most of the features of the Cobalt Strike compatibility layer.| ![](https://img.shields.io/github/stars/hakaioffsec/coffee?label=&style=flat) | ![](https://img.shields.io/github/last-commit/hakaioffsec/coffee?label=&style=flat) 
| [CoffeeLdr](https://github.com/Cracked5pider/CoffeeLdr) | C | CoffeeLdr is a loader for so called Beacon Object Files.  | ![](https://img.shields.io/github/stars/Cracked5pider/CoffeeLdr?label=&style=flat) | ![](https://img.shields.io/github/last-commit/Cracked5pider/CoffeeLdr?label=&style=flat) 
| [ldr](https://github.com/yamakadi/ldr) | Rust | Unsuccessful attempt at a Rust BOF/COFF loader.| ![](https://img.shields.io/github/stars/yamakadi/ldr?label=&style=flat) | ![](https://img.shields.io/github/last-commit/yamakadi/ldr?label=&style=flat) 
| [COFF-Loader](https://github.com/Ap3x/COFF-Loader) | C++ | This is a reimplementation of TrustedSec COFF Loader.| ![](https://img.shields.io/github/stars/Ap3x/COFF-Loader?label=&style=flat) | ![](https://img.shields.io/github/last-commit/Ap3x/COFF-Loader?label=&style=flat) 
| [Invoke-Bof](https://github.com/airbus-cert/Invoke-Bof) | PowerShell | A PowerShell script to run BOFs. | ![](https://img.shields.io/github/stars/airbus-cert/Invoke-Bof?label=&style=flat) | ![](https://img.shields.io/github/last-commit/airbus-cert/Invoke-Bof?label=&style=flat) 
| [pybof](https://github.com/rkbennett/pybof) | Python | Python based BOF loader | ![](https://img.shields.io/github/stars/rkbennett/pybof?label=&style=flat) | ![](https://img.shields.io/github/last-commit/rkbennett/pybof?label=&style=flat) 
| [python-bof-runner](https://github.com/naksyn/python-bof-runner) | Python | Python-based BOF runner using inline shellcode injection | ![](https://img.shields.io/github/stars/naksyn/python-bof-runner?label=&style=flat) | ![](https://img.shields.io/github/last-commit/naksyn/python-bof-runner?label=&style=flat) 
| [RunOF](https://github.com/nettitude/RunOF) | .NET | Running BOFs in .NET | ![](https://img.shields.io/github/stars/nettitude/RunOF?label=&style=flat) | ![](https://img.shields.io/github/last-commit/nettitude/RunOF?label=&style=flat) 
| [NiCOFF](https://github.com/frkngksl/NiCOFF) | Nim | COFF and BOF file loader written in Nim.| ![](https://img.shields.io/github/stars/frkngksl/NiCOFF?label=&style=flat) | ![](https://img.shields.io/github/last-commit/frkngksl/NiCOFF?label=&style=flat) 
| [COFFLoader2](https://github.com/Yaxser/COFFLoader2) | C | Rewrite of the TrustedSec COFF loader.| ![](https://img.shields.io/github/stars/Yaxser/COFFLoader2?label=&style=flat) | ![](https://img.shields.io/github/last-commit/Yaxser/COFFLoader2?label=&style=flat) 
| [Jormungandr](https://github.com/Idov31/Jormungandr) | C++ | a kernel implementation of a COFF loader. | ![](https://img.shields.io/github/stars/Idov31/Jormungandr?label=&style=flat) | ![](https://img.shields.io/github/last-commit/Idov31/Jormungandr?label=&style=flat) 
| [bof-launcher](https://github.com/The-Z-Labs/bof-launcher) | Zig and C | Beacon Object File (BOF) launcher - library for executing BOF files in C/C++/Zig applications.| ![](https://img.shields.io/github/stars/The-Z-Labs/bof-launcher?label=&style=flat) | ![](https://img.shields.io/github/last-commit/The-Z-Labs/bof-launcher?label=&style=flat) 
| [CS2BR BOF](https://github.com/NVISOsecurity/cs2br-bof) | C |  CS2BR implements a compatibility-layer that make CS BOFs use the BRC4 API. | ![](https://img.shields.io/github/stars/NVISOsecurity/cs2br-bof?label=&style=flat) | ![](https://img.shields.io/github/last-commit/NVISOsecurity/cs2br-bof?label=&style=flat) 
| [nim-lazy-bof](https://github.com/zimnyaa/nim-lazy-bof) | Nim | Nim port of Sliver's BOF loader | ![](https://img.shields.io/github/stars/zimnyaa/nim-lazy-bof?label=&style=flat) | ![](https://img.shields.io/github/last-commit/zimnyaa/nim-lazy-bof?label=&style=flat) 
| [coff_loader](https://github.com/soheil-01/coff_loader) | Zig | Experimental COFF loader for Cobalt Strike BOFs | ![](https://img.shields.io/github/stars/soheil-01/coff_loader?label=&style=flat) | ![](https://img.shields.io/github/last-commit/soheil-01/coff_loader?label=&style=flat) 
| [BOF2shellcode](https://github.com/FalconForceTeam/BOF2shellcode) | Convert BOFs into raw shellcode || ![](https://img.shields.io/github/stars/FalconForceTeam/BOF2shellcode?label=&style=flat) | ![](https://img.shields.io/github/last-commit/FalconForceTeam/BOF2shellcode?label=&style=flat) 
| [warlock](https://github.com/cyberphor/warlock) | C | Beacon Object File (BOF) generator, client, and loader.| ![](https://img.shields.io/github/stars/cyberphor/warlock?label=&style=flat) | ![](https://img.shields.io/github/last-commit/cyberphor/warlock?label=&style=flat) 
| [GOFFER](https://github.com/Real-Cryillic/GOFFER) | Go | Beacon Object File loaderin Go.| ![](https://img.shields.io/github/stars/Real-Cryillic/GOFFER?label=&style=flat) | ![](https://img.shields.io/github/last-commit/Real-Cryillic/GOFFER?label=&style=flat) 
| [bof-loader](https://github.com/cirosec/bof-loader) | C++ | Beacon Object File (BOF) Runtime/Loader| ![](https://img.shields.io/github/stars/cirosec/bof-loader?label=&style=flat) | ![](https://img.shields.io/github/last-commit/cirosec/bof-loader?label=&style=flat) 
| [BOF-Exec](https://github.com/nseckt/BOF-Exec) | C++ | A small tool that loads and executes a Beacon Object File (BOF) and optionally passes arguments to it.| ![](https://img.shields.io/github/stars/nseckt/BOF-Exec?label=&style=flat) | ![](https://img.shields.io/github/last-commit/nseckt/BOF-Exec?label=&style=flat) 

---

## 📚 Contribution
Want to add another loader or tool? Open a PR!
