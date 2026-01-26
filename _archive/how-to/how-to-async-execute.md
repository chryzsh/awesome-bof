# How-To: Run BOFs asynchronously with `async-execute` in Cobalt Strike

This guide will show you how to use the `async-execute` Postex DLL in Cobalt Strike to run Beacon Object Files (BOFs) asynchronously. This enables BOFs to run in their own threads without blocking the Beacon process.

---

## 🎯 Goal
- Understand what the purpose of `async-execute` is
- Load and run BOFs using `async-execute`
- Manage and monitor asynchronous jobs

---

## 🧠 Why Use `async-execute`?
Traditionally, BOFs run synchronously. They take over the Beacon thread and must finish before you can issue another command. `async-execute` allows:

- Running multiple BOFs in parallel
- Avoiding long delays or lock-ups in Beacon from long-running jobs
- Improved operational flexibility

With CS 4.11, the CS team introduced a way to run BOFs async with a moduled developed in the Postex kit.


---

## 📦 Requirements
- Cobalt Strike 4.11+
- `async-execute` module (downloaded from the Postex Kit)
- A compiled BOF (`.o` file)

---

## 📁 Step 1: Download and load it from the Postex Kit
- Download the artifact kit (requires valid CS license)
- Load the `async-execute.cna` through the Script Manager in CS
- From Beacon, the `async-execute` command should be exposed:

```
 help async-execute
Usage: async-execute --pid <pid> --arch <arch> --mode <mode> --bof <bof_path> --syscall <syscall_method> --fmt <bof_arguments_fmt> --argX <bof_argument>
```

## ▶️ Step 2: Run a BOF Asynchronously
Execute multiple BOFs with the `async-execute` command
```powershell
async-execute --arch x64 --bof first-bof.o
```

```powershell
async-execute --arch x64 --bof second-bof.o
```

Output appears in the job-specific console in the GUI.

---

## 📋 Step 3: Monitor Asynchronous Jobs
Each async BOF appears as its own *job*. You can follow the BOFs in the `Right click -> Jobs ...` menu for a Beacon, or `View -> All Jobs` menu to see jobs across all beacons.

![alt text](../resources/async-bof.png)

---

## ⚠️ Limitations
- `BeaconDataStore` and some internal APIs are not supported in async mode.

---

### References
- [Blog post referencing Asynchronous BOFs](https://www.cobaltstrike.com/blog/cobalt-strike-411-shh-beacon-is-sleeping)
- [Postex kit](https://hstechdocs.helpsystems.com/manuals/cobaltstrike/current/userguide/content/topics/post-exploitation_postex-kit.htm)

---
