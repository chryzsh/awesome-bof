# Explanation: BOF Internals – How Beacon Object Files Work

Beacon Object Files (BOFs) are small compiled C programs designed to run directly within the memory space of a C2 agent (like Cobalt Strike’s Beacon). This execution model allows stealthy, fast, and fileless tasking of post-exploitation actions without creating new processes or touching disk.

This article explains the internal structure, lifecycle, memory model, and API integration of a typical BOF.

---

## 🧱 1. BOF Structure Overview

- **Format:** COFF (Common Object File Format)
- **Compiled From:** C source code using `gcc`/`clang` (typically MinGW for Windows)
- **Entrypoint:** `void go(char *args, int len)`
- **Output API:** `BeaconPrintf(CALLBACK_OUTPUT, "message")`

BOFs are not executables — they lack a PE header and are never intended to run as standalone binaries. Instead, they are loaded into a running process (e.g. Beacon) and executed in-memory.

---

## 🧬 2. Lifecycle of a BOF

1. **Authoring:** Write a small C function that uses Beacon APIs (e.g. for printing or parsing arguments).
2. **Compilation:** Compile to `.o` (COFF object file) using `-c` flag:
   ```bash
   x86_64-w64-mingw32-gcc -c mybof.c -o mybof.o
   ```
3. **Loading:** The C2 (e.g. Cobalt Strike) injects the object file into memory and parses the COFF format.
4. **Linking/Resolution:** The loader resolves any function symbols (e.g. `BeaconPrintf`, `memcpy`, etc.).
5. **Execution:** The C2 calls the `go()` function and passes argument data.
6. **Output Handling:** BOFs must output data using Beacon API functions — no `printf()` or `stdout`.
7. **Cleanup:** Memory is optionally freed. Some C2s auto-clean the job after BOF finishes.

---

## 🧠 3. Function Naming and Dynamic Linking

All external function calls must be **statically declared** using special macros or headers (e.g. `beacon.h`). C2 frameworks typically do one of the following:

- **Match symbol names:** Expect functions like `BeaconPrintf` to exist in the `.o` file
- **Patch symbol table:** New reesarch reveals it is possible rewrite symbols after compilation (e.g. using `objcopy` techniques), see [Writing Beacon Object Files Without DFR](https://blog.cybershenanigans.space/posts/writing-bofs-without-dfr/)
- **Manual linking:** In some frameworks (like Sliver or Mythic), function pointers are passed manually

---

## 🧵 4. Threading and Execution Context

- **Cobalt Strike (Sync):** BOF runs inline on the Beacon thread
- **Cobalt Strike (Async):** Using `async-execute`, each BOF runs in a new thread
- **Sliver / Havoc / Meterpreter:** BOFs typically run synchronously
- **Memory Space:** BOFs inherit Beacon’s context — same PID, token, architecture, etc.
- **Stack Constraints:** Keep memory use minimal; avoid recursion and large stack frames

---

## 📦 5. Argument Handling

### Cobalt Strike:
```c
datap parser;
BeaconDataParse(&parser, args, len);
char *input = BeaconDataExtract(&parser, NULL);
```

### Sliver, Meterpreter, Havoc:
- Arguments passed as a format string (e.g. `"arg1 arg2"`) and parsed manually

---

## 🔐 6. Beacon APIs Used in BOFs

| Function | Purpose |
|----------|---------|
| `BeaconPrintf()` | Send output back to C2 GUI or job window |
| `BeaconDataParse()` | Parse incoming arguments |
| `BeaconFormat/Output()` | Build dynamic output buffers |
| `BeaconUseToken()` | Set token for impersonation |
| `BeaconGetSpawnTo()` | Retrieve configured sacrificial process |

Note: Not all C2s implement all Beacon APIs. Some, like async loaders, may not support certain calls.

---

## ⚠️ 7. Common Pitfalls

- ❌ Using `printf`, `malloc`, or globals
- ❌ Expecting console or stdin/stdout access
- ❌ Writing large or long-running loops (blocks the agent thread)
- ❌ Assuming BOFs are DLLs — they’re not

---

## ✅ 8. Best Practices

- Keep BOFs small and purpose-built
- Always test outside C2 with loaders like `COFFLoader`
- Use `BeaconPrintf` for all output
- Test 32-bit and 64-bit variants
- Avoid using C++ STL or exceptions

---

## 🧠 Summary
BOFs are minimalistic, thread-safe C routines compiled as COFF files. They rely on the C2's loader to inject, resolve, and execute them. When written properly, they provide low-overhead, high-stealth capabilities for red team operations — especially when combined with async execution and direct syscalls.

For examples and loaders, see:
- [`reference/bofs-catalog.md`](../reference/bofs-catalog.md)
- [`reference/loaders-catalog.md`](../reference/loaders-catalog.md)

