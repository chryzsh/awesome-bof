# Reference: Blog Posts and Research on BOF Development

This page catalogs key blog posts, whitepapers, and research articles related to Beacon Object Files (BOFs). These resources span introductory guides, advanced development tips, C2 integration techniques, stealth improvements, and detection engineering — all curated for offensive security professionals and researchers.

---

## 📘 Beginner-Friendly Introductions

| Title | Author | Details | Date |
|-------|--------|---------|------------------|
| [A Developer's Introduction to Beacon Object Files](https://www.trustedsec.com/blog/a-developers-introduction-to-beacon-object-files/) | Christopher Paschen (TrustedSec) | Comprehensive introduction to BOF concepts and development | 2023-11-15 |
| [BOFs for Script Kiddies](https://trustedsec.com/blog/bofs-for-script-kiddies) | TrustedSec | An introduction to what BOFs are | 2023-02-16 |
| [Beacon Object Files](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/beacon-object-files_main.htm) | Fortra (Official docs) | Official documentation on BOF implementation and usage | 2023-08-20 |
| [Beginner introduction to CobaltStrike BOF development](https://ph3n1x.com/posts/beginner-introduction-to-cobaltstrike-bof-development/) | ph3n1x | Step-by-step guide for beginners to create their first BOF | 2025-05-03 |
| [Introduction to BOF, Beacon Object Files not Buffer OverFlows](https://blog.shashwatshah.me/2023/03/26/Bofs_Part-1.html) | 0xEr3bus | Beginner-friendly blog explaining BOFs and writing custom process injector and remote Etw patching. | 2023-03-26 |
| [Developing Cobalt Strike BOFs with Visual Studio](https://www.securify.nl/en/blog/creating-cobalt-strike-bofs-with-visual-studio/) | Yasse Alhzami | 2021-11-16 | Simple tutorial to develop BOFs with VS.

---

## 🧪 Videos, Guides and Demos

| Title | Author/Org | Details | Date |
|-------|------------|---------|------------------|
| [Introduction to Beacon Object Files in Red-Teaming Operations](https://www.youtube.com/watch?v=jlLPKGDtsWY) | Rafael Felix | EKO2023 Conference Presentation on BOF usage in red team ops | 2024-11-24 |
| [RTO: Malware Development Advanced - CaFeBiBa - Coff Object Parser](https://www.youtube.com/watch?v=GSdGnIu6CII) | Sektor7 | RED TEAM Operator course teaser on COFF parsing | 2022-12-23 | 
| [Situational Awareness Beacon Object Files](https://www.youtube.com/watch?v=G_E6ggLNtbY) | TrustedSec | Demo of BOFs for host and network reconnaissance | 2022-09-30 |
| [Cobalt Strike: Beacon Object Files (NoteThief Demo)](https://www.youtube.com/watch?v=ksCVx9PbkZE) | Kandy Phan | Demo of grabbing unsaved Notepad contents with a BOF | 2022-05-14 |
| [Building Your TTP Arsenal: What Are BOFs?](https://www.youtube.com/watch?v=3yEZVBZsQzU) | TrustedSec | Introduction to BOF concepts and tactical usage | 2021-03-15 |
| [CredBandit - Part 1 - Tool Review](https://www.youtube.com/watch?v=WV34uVMxKZk) | ACCESS GRANTED (Joe Vest) | Review of in-memory minidump BOF for credential harvesting | 2021-07-15 |
| [Universal Unhooking as a Beacon Object File](https://www.youtube.com/watch?v=y6hE0rF99EU) | Cobalt Strike Archive | Demo of Cylance's Universal Unhooking capability as BOF | 2021-01-13 |
| [CVE-2020-0796 (SMBGhost) as a Beacon Object File](https://www.youtube.com/watch?v=HrYtctprUUc) | Cobalt Strike Archive | Demonstration of SMBGhost vulnerability exploitation via BOF | 2020-09-17 |
| [CVE-2020-1472 Zerologon as a Beacon Object File](https://www.youtube.com/watch?v=zGf1Rat3rEk) | Cobalt Strike Archive | Demonstration of Zerologon attack chain with Cobalt Strike | 2020-09-17 |
| [Beacon Object Files - Luser Demo](https://youtu.be/gfYswA_Ronw) | Cobalt Strike Archive | Basic demonstration of BOF usage and implementation | 2020-06-19 |
| [Cobalt Strike BOF: Enum_filter_driver](https://www.youtube.com/watch?v=MvRY0qS8XFk) | TrustedSec | Demo of the enum_filter_driver BOF | 2021-05-06
| [Building Your TTP Arsenal Video Series: Identifying Risks (BOF)](https://youtu.be/M6Y5Q8OVkSo) | TrustedSec | Demo of multiple BOFs addressing opsec | 2021-04-15
| [Advanced Audit Settings](https://www.youtube.com/watch?app=desktop&v=zeuiCrUPMAs) | TrustedSec | Covers the importance of enumerating Advanced Audit Settings using BOFs | 2021-05-28
| [LastPass in Memory Exposure](https://www.youtube.com/watch?app=desktop&v=9hC15PzcQgc) | TrustedSec | Dump lastpass using BOF demo | 2022-10-24
| [How to Dump LSASS.exe Process Memory with Nanodump BOF - Windows Defender Bypass](https://www.youtube.com/watch?v=jwETspKR6JU) | Gemini Cyber Security | Dumping lsass with nanodump demo | 2023-08-18

---

## 🧰 BOF Development and Tooling

| Title | Author | Details | Date |
|-------|-------|---------|------------------|
| [f Our Beacon Object Files (BOFs)](https://www.netspi.com/blog/technical-blog/adversary-simulation/the-future-of-beacon-object-files/) | Ceri Coburn (NetSPI) | Advanced BOF format for extended capabilities | 2025-03-19 |
| [Writing Beacon Object Files Without DFR](https://blog.cybershenanigans.space/posts/writing-bofs-without-dfr/) | Matt Ehrnschwender | Techniques for BOF development without Dynamic Function Resolution | 2024-11-18 |
| [An Operators Guide to BeaconkObject Files](https://maldev.nl/posts/operator-guide-bof/) | notb9 | Demonstrating BOF use with the Invoke-Bof project | 2024-11-01
| [Simplifying BOF Development with Visual Studio](https://www.cobaltstrike.com/blog/simplifying-bof-development) | Fortra | Using Visual Studio for streamlined BOF development | 2023-08-10 |
| [Changes in the Beacon Object File Landscape](https://trustedsec.com/blog/changes-in-the-beacon-object-file-landscape) | Christopher Paschen (TrustedSec) | Discussion on the current state of BOFs as per the time of writing. | 2023-03-28 
| [Writing BOFs: Flexible, Stealthy, and Compatible](https://www.cobaltstrike.com/blog/writing-beacon-object-files-flexible-stealthy-and-compatible) | Core Labs (Fortra) | Best practices for creating effective and stealthy BOFs | 2021-12-20 |
| [Process Injection via custom Beacon Object Files Part 2](https://cerbersec.com/2021/08/26/beacon-object-files-part-2.html) | Cerbersec | Implementing the [CobaltWhispers](https://github.com/NVISOsecurity/CobaltWhispers) BOF | 2022-08-21
| [Process Injection via custom Beacon Object Files Part 1](https://cerbersec.com/2021/08/26/beacon-object-files-part-1.html) | Cerbersec | Implementing the [CobaltWhispers](https://github.com/NVISOsecurity/CobaltWhispers) BOF | 2022-08-21
| [CredBandit (In memory BOF MiniDump) - Tool review - Part 1](https://www.cobaltstrike.com/blog/credbandit-a-review-of-a-tool-developed-built-by-the-cobalt-strike-user-community)| Joe Vest | Demonstrating the [CredBandit](https://github.com/xforcered/CredBandit) BOF | 2021-07-13 |
| [Creating the WhereAmI Cobalt Strike BOF ](https://0xboku.com/2021/08/19/Bof-WhereAmI.html) | boku7 | This is a walkthrough of creating the Cobalt Strike Beacon Object File (BOF) “Where Am I?” | 2021-08-19 |
| [Exploiting (D)COM in C; CobaltStrike BOF as PoC.](https://yaxser.github.io/CobaltStrike-BOF/) | Yaxser | Explaining the DCOM lateral movement BOF | 2020 |
---
| [Exploring WinRM plugins for lateral movement](https://falconforce.nl/exploring-winrm-plugins-for-lateral-movement/) | FalconForce | Exploring WinRM plugins for lateral movement | 2025-01-20

## 🔬 Advanced Techniques and Stealth

| Title | Author | Details | Date |
|-------|--------|---------|------------------|
| [Cobalt Strike 4.11: Shhhhhh, Beacon is Sleeping....](https://www.cobaltstrike.com/blog/cobalt-strike-411-shh-beacon-is-sleeping) | William Burgess (Fortra) | Introduction to asynchronous BOF execution capabilities | 2025-04-15 |
| [Cobalt Strike 4.10: Through the BeaconGate](https://www.cobaltstrike.com/blog/cobalt-strike-410-through-the-beacongate) | William Burgess (Fortra) | Introducing custom Sleepmask BOFs and other BOF updates | 2024-07-16 |
| [BOFRyptor: Encrypting Your Beacon During BOF Execution to Avoid Memory Scanners](https://www.securify.nl/en/blog/bofryptor-encrypting-your-beacon-during-bof-execution-to-avoid-memory-scanners/) | Yasser Alhazmi | BOFRyptor, a BOF that will encrypt the beacon during execution to avoid memory scanners. | 2024-10-09 | 
| [Your BOFs Are Gross, Put on a Mask](https://www.ibm.com/think/x-force/how-to-hide-beacon-during-bof-execution) | Joshua Magri (IBM X-Force Red) | Techniques for hiding Beacon during BOF execution. See [BOFMask on Github](https://github.com/passthehashbrowns/BOFMask) | 2023-05-30 |
| [Using RPC in BOFs](https://www.trustedsec.com/blog/using-rpc-in-bofs) | Christopher Paschen (TrustedSec) | Demonstration of using RPC in BOFs | 2023-03-28 |
| [No Consolation – Reflective PE Loader as a BOF](https://www.coresecurity.com/core-labs/articles/running-pes-inline-without-console) | Fortra | Loading PE files as BOFs without console artifacts | 2023-02-15 |
| [FalconFriday: Direct System Calls and Cobalt Strike BOFs](https://falconforce.nl/falconfriday-direct-system-calls-and-cobalt-strike-bofs-0xff14/) | FalconForce | Analysis of direct syscall techniques in BOFs | 2022-11-04 |
| [Direct Syscalls in Beacon Object Files](https://www.outflank.nl/blog/2020/12/26/direct-syscalls-in-beacon-object-files/) | Cornelis de Plaa (Outflank) | Implementation of direct syscalls in BOFs to evade EDR hooks | 2020-12-10 |
| [BOF2shellcode — a tutorial converting a stand-alone BOF loader into shellcode](https://falconforce.nl/bof2shellcode-a-tutorial-converting-a-stand-alone-bof-loader-into-shellcode/) | FalconForce | Converting BOFs to shellcode | 2021
| [Introducing the Mutator Kit: Creating Object File Monstrosities with Sleep Mask and LLVM](https://www.cobaltstrike.com/blog/introducing-the-mutator-kit-creating-object-file-monstrosities-with-sleep-mask-and-llvm) | William Burgess (Fortra) | Mutator kit to compile BOFs | 2024
| [	
Cobalt Strike 4.9: Take Me To Your Loader](https://www.cobaltstrike.com/blog/cobalt-strike-49-take-me-to-your-loader) | Greg Darwin (Fortra) | Storing BOFs in beacon data store | 2023

--- 

## Loaders
| Title | Author | Details | Date |
|-------|--------|---------|------------------|
| [CoffLoader ](https://otterhacker.github.io/Malware/CoffLoader.html) | An introduction to writing a COFF loader | otterhacker | 2025 | 
| [Introducing Goffloader: A Pure Go Implementation of an In-Memory COFFLoader and PE Loader](https://www.praetorian.com/blog/introducing-goffloader-a-pure-go-implementation-of-an-in-memory-coffloader-and-pe-loader/)| Michael Weber (Praetorian) | Go implementation of an in-memory COFFLoader and PE loader. | 2024-09-02 |
| [Operator's Guide to the Meterpreter BOFLoader](https://trustedsec.com/blog/operators-guide-to-the-meterpreter-bofloader)| Kevin Clark (TrustedSec) | Demonstrate uses of the Meterpreter BOFLoader. | 2023-01-24 |
| [Coffee: A COFF loader made in Rust](https://hakaisecurity.io/coffee-a-coff-loader-made-in-rust/research-blog/) | Rafael "biscoito" Felix | Demo of a COFF loader made in Rust | 2023-06-22|
| [Introducing RunOF - Arbitrary BOF tool ](https://www.lrqa.com/en/cyber-labs/introducing-runof-arbitrary-bof-tool/) | Joel Snape | A .NET based BOF loader | 2022-03-02
| [Malware development part 8 - COFF injection and in-memory execution](https://0xpat.github.io/Malware_development_part_8/) | Explanation of COFF injection |  0xpat | 2021-03-16 | 
| [Invoke-Bof](https://skyblue.team/posts/invoke-bof/) | Sky Blueteam | A PowerShell based BOF loader | 2021-12-09
| [COFFLoader: Building your own in memory loader or how to run BOFs](https://trustedsec.com/blog/coffloader-building-your-own-in-memory-loader-or-how-to-run-bofs)| Kevin Haubris (TrustedSec) | Building a BOF loader | 2021-02-22 |
| [Running Cobalt Strike BOFs from Python ](https://www.naksyn.com/injection/2022/02/16/running-cobalt-strike-bofs-from-python.html) | Naksyn | Demonstrating python-bof-runner | 2022-02-16 |

---

## Linux and ELF loading
| Title | Author | Details | Date |
|-------|--------|---------|------------------|
| [Write, debug and execute BOFs with bof-launcher (part 2)](https://blog.z-labs.eu/2025/01/15/write-debug-and-execute-bofs-part2.html) | Z-Labs | Developing BOFs in Zig with the bof-launcher project | 2025-01-15
| [Write, debug and execute BOFs with bof-launcher (part 1)](https://blog.z-labs.eu/2024/12/02/write-debug-and-execute-bofs-part1.html) | Z-Labs | Developing BOFs in Zig with the bof-launcher project | 2024-12-02
| [Executing Cobalt Strike's BOFs on ARM-based Linux devices](https://blog.z-labs.eu/2024/05/10/bofs-on-arm-based-devices.html) | Z-Labs | Demonstrating running BOFs on Linux ARM-based devices. | 2024-05-10
| [Running BOFs with 'bof-launcher' library](https://blog.z-labs.eu/2024/02/08/bof-launcher.html) | Z-Labs | An open-source library for loading, relocating and launching Cobalt Strike’s BOFs on Windows and UNIX/Linux systems. | 2024-02-08
[ELFLoader: Another In Memory Loader Post](https://trustedsec.com/blog/elfloader-another-in-memory-loader-post) | Kevin Haubris | Demonstrating a Linux based BOF loader | 2022-05-04 | 

---

## 🌐 Cross-C2 Usage and Integration

| Title | Author | Details | Date |
|-------|--------|---------|------------------|
| [Let's write a Beacon Object File for Havoc C2 - Part 1/5](https://www.100daysofredteam.com/p/lets-write-a-beacon-object-file-for-havoc-c2-part-1) | Uday Mittal | First part of 5-part series on BOF development for Havoc C2 | 2025-02-27 |
| [Creating a simple beacon object file for Havoc C2](https://www.100daysofredteam.com/p/creating-a-simple-beacon-object-file-for-havoc-c2) | Uday Mittal | Tutorial for creating basic BOFs for Havoc C2 framework | 2025-02-23 |
| [Enhancing C2 agent via Beacon Object Files](https://www.100daysofredteam.com/p/enhancing-c2-agent-via-beacon-object-files-bof) | Uday Mittal | Using BOFs to extend C2 agent capabilities | 2025-01-10 |
| [Sliver BOF](https://www.redteaming.org/sliverbof.html) | RedTeaming.org | Demo of BOF in Sliver C2 | 2023-10-18 |
| [Introducing CS2BR pt. III – Knees deep in Binary](https://blog.nviso.eu/2023/10/26/introducing-cs2br-pt-iii-knees-deep-in-binary/) | Nviso | Running CS BOFs in Brute Ratel | 2023-10-26
| [Introducing CS2BR pt. II – One tool to port them all](https://blog.nviso.eu/2023/07/17/introducing-cs2br-pt-ii-one-tool-to-port-them-all/) | Nviso | Running CS BOFs in Brute Ratel | 2023-07-17
| [Introducing CS2BR pt. I – How we enabled Brute Ratel Badgers to run Cobalt Strike BOFs](https://blog.nviso.eu/2023/05/15/introducing-cs2br-pt-i-how-we-enabled-brute-ratel-badgers-to-run-cobalt-strike-bofs/) | Nviso | Running CS BOFs in Brute Ratel | 2023-05-15
| [BOFs in Mythic with Xenon Agent](https://github.com/MythicAgents/xenon) | Mythic Contributors | BOF implementation for the Mythic C2 framework | 2023-04-30 |
| [Learning Sliver C2 (12) - Extensions](https://dominicbreuker.com/post/learning_sliver_c2_12_extensions/) | dominicbreuker.com |  | 2023-03-23 |
| [Meterpreter & Beacon Object Files (BOF)](https://moulinette.org/posts/msf-bof/) | moulinette.org | French article on using BOFs in MSF | 2023-05-29 

---

## 🛡️ Detection, Defense & Simulation

| Title | Author | Details | Date |
|-------|--------|---------|------------------|
| [Detonating Beacons to Illuminate Detection Gaps](https://www.elastic.co/security-labs/detonating-beacons-to-illuminate-detection-gaps) | Elastic Security Labs | Analysis of BOF detection techniques and evasion methods | 2025-01 |
| [FalconFriday — Direct system calls and Cobalt Strike BOFs — 0xFF14](https://falconforce.nl/falconfriday-direct-system-calls-and-cobalt-strike-bofs-0xff14/) | FalconForce | Deep-dive into how direct system calls could be detected based on some example Cobalt Strike BOFs |  2021-07-21 |
---

## 📚 Contributing

If you know of a blog post, paper, or project that should be listed here, feel free to open a pull request!
