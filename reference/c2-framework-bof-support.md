# Reference: BOF Support Across C2 Frameworks

This reference provides a comprehensive overview of how Beacon Object Files (BOFs) are supported across major Command and Control (C2) frameworks. It covers implementation details, compatibility, execution methods, and key differences to help red team operators understand how BOFs work in different environments.


---
## 🧭 BOF Support Overview by C2

| C2 Framework     | BOF Support | Platform(s) | Async Execution | Beacon API Compatibility | Argument Handling | Notes | Docs |
|------------------|-------------|-------------|-----------------|--------------------------|-------------------|-------|------|
| **Cobalt Strike**| ✅ Native   | Windows     | ✅ `async-execute` | ✅ Full API support        | `BeaconDataParse`  | Original BOF host. Mature and stable. |
| **Sliver**       | ✅ Native   | Win/Linux   | ❌                | ⚠️ Partial                 | Format string       | Requires `extension.json` for BOF commands. | [Documentation](https://sliver.sh/docs?name=BOF+and+COFF+Support)
| **Havoc**        | ✅ Native   | Windows     | ❌                | ⚠️ Partial (Beacon-style)  | Format string       | Uses inline-execute or register command. | [Documentation](https://havocframework.com/docs/object_files)
| **Meterpreter**  | ✅ Native   | Windows     | ❌                | ⚠️ Partial                 | Format string       | `bofloader` extension added in 2023. | [Documentation](https://docs.metasploit.com/docs/using-metasploit/advanced/meterpreter/meterpreter-executebof-command.html)
| **Outflank OST** | ✅ Native   | Windows     | ❌                | ⚠️ Partial (custom)        | Hardcoded/config    | Custom loader used in enterprise red teams. |
| **Brute Ratel**  | ✅ Native   | Windows     | ✅                | ✅ Full (Beacon-style)     | `BeaconDataParse`   | Commercial tool with async BOF threading. |
| **Nighthawk**    | ✅ Native   | Windows     | ✅                | ✅ Full (internal runtime) | `BeaconDataParse`   | High-end C2 focused on stealth and OPSEC. |
| **Mythic (Xenon)**| ✅ Partial | Windows     | ❌                | ⚠️ Minimal                 | Manual/C-style      | BOF support added via `execute_bof`. |
| **AdaptixC2**| ✅ Partial | Windows     | ❌                | ⚠️ Minimal                 | Manual/C-style      | BOF support added via `execute_bof`. |
---

---

## 🔍 Key Differences

### Execution Model
- **Synchronous Execution**: Most frameworks (Sliver, Havoc, Meterpreter, OST, Mythic) run BOFs in the main agent thread, which blocks until completion.
- **Asynchronous Execution**: Cobalt Strike (4.11+), Brute Ratel, and Nighthawk support running BOFs in separate threads, allowing the agent to remain responsive.

### API Compatibility
- **Full API**: Cobalt Strike, Brute Ratel, and Nighthawk implement the complete Beacon API.
- **Partial API**: Sliver, Havoc, Meterpreter, and OST implement core functions but may lack some advanced features.
- **Minimal API**: Mythic (Xenon) provides basic functionality but requires more adaptation for complex BOFs.

### Argument Handling
- **BeaconDataParse**: Cobalt Strike, Brute Ratel, and Nighthawk use the standard Beacon argument parsing.
- **Format Strings**: Sliver, Havoc, and Meterpreter use format string-based argument parsing.
- **Custom**: OST and some others use custom argument handling mechanisms.

### Platform Support
- **Windows-only**: Most frameworks only support BOFs on Windows.
- **Cross-platform**: Sliver stands out by supporting BOFs on both Windows and Linux.

---

## 🔗 Related Resources
- [`reference/loaders-catalog.md`](./loaders-catalog.md)

## Contributions
Please contribute by adding PRs to track new C2s adopting BOF support!
