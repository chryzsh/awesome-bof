# Explanation: BOF Arguments and Argument Parsing

Beacon Object Files (BOFs) often require input from the operator — such as hostnames, usernames, file paths, or raw data — to operate effectively. However, because BOFs are small, position-independent C object files with no standard input or command-line environment, they rely on custom argument-passing mechanisms implemented by the C2 framework.

This article explains how arguments are passed into BOFs, how they are parsed inside different C2 frameworks, and provides a reference for Cobalt Strike’s argument format specifiers. If you are looking for how to execute BOFs in different C2 frameworks, see [How-To: Run BOFs in Common C2 Frameworks](../how-to/how-to-execute-bofs-in-c2.md).

---

## 🧠 Core Concept

A BOF has one required entrypoint:
```c
void go(char *args, int length);
```

- `args`: a pointer to the raw argument data buffer
- `length`: the size of the data buffer in bytes

The actual format and encoding of `args` varies depending on the C2 framework.

---

## 🐝 Cobalt Strike Argument Parsing

Cobalt Strike offers a full API for structured argument parsing through the `BeaconDataParse` family of functions. This allows complex argument formats including integers, strings, blobs, and even nested data.

### General principles
- Args are packed in binary format using bof_pack function
- Args are unpacked via functions (eg BeaconDataParse and BeaconDataExtract) exported by beacon.h
- Args are unpacked in the same order they were packed

### ✅ Example
This is a simple example just to demonstrate arg parsing.
```c
#include "beacon.h"

void go(char *args, int len) {
    datap parser;
    BeaconDataParse(&parser, args, len);

    char *host = BeaconDataExtract(&parser, NULL);
    int port = BeaconDataInt(&parser);

    BeaconPrintf(CALLBACK_OUTPUT, "Host: %s, Port: %d", host, port);
}
```

### 💡 Usage in Aggressor Script
Pay attention to the `bof_pack` function.

```aggressor
# Register a new Beacon command called 'connect_test'
beacon_command_register(
    "connect_test", 
    "Test BOF with hostname and port arguments", 
    "Usage: connect_test [hostname] [port]"
);

# Define the alias that will be called when the command is used
alias connect_test {
    # $1 = Beacon ID
    # $2 = hostname argument
    # $3 = port argument
    
    # Validate arguments
    if ($2 eq "" || $3 eq "") {
        berror($1, "Please provide both hostname and port arguments");
        return;
    }
    
    # Parse port as integer
    local('$port');
    $port = int($3);
    
    # Pack arguments using format specifiers:
    # - 'Z' for null-terminated string (hostname)
    # - 'i' for 4-byte integer (port)
    $args = bof_pack($1, "Zi", $2, $port);
    
    # Log what we're doing
    blog($1, "Executing connect_test BOF with Host: $2, Port: $port");
    
    # Execute the BOF with our packed arguments
    # Assuming the BOF file is in the same directory as the script
    beacon_inline_execute($1, script_resource("connect_test.o"), $args);
}

```

### Usage from Beacon
```powershell
inline-execute bof.o example.com 8080
```
Cobalt Strike internally packs these arguments into a buffer using its scripting language.

---

## 🔤 Format Specifiers for Argument Packing

When using Aggressor Script or a compatible scripting interface to invoke BOFs, arguments are packed into a binary blob using format strings.

| Specifier | Meaning                         | C Type                |
|-----------|----------------------------------|------------------------|
| `Z`       | Null-terminated string           | `char *`              |
| `z`       | Binary blob (length-prefixed)    | `char *, int`         |
| `i`       | 4-byte integer                   | `int`                 |
| `b`       | Boolean (1-byte integer)         | `char` or `int`       |
| `r`       | Raw buffer (returns length too)  | `char *, int`         |

> These format specifiers tell the loader how to serialize and pass values to the BOF.

---


## ⚠️ Pitfalls

- 🧨 **No bounds checking**: If you parse arguments manually, always validate input length.
- 🧵 **Thread-safety**: Do not store parsed args in static/global memory.
- 🧪 **Test with malformed input**: Make your BOFs resilient to invalid arg formats.
- 🧱 **Avoid assumptions**: Not every C2 packs arguments the same way — always test per framework.

---

## 🧪 Testing Argument Parsing

Use standalone loaders like [`COFFLoader`](https://github.com/trustedsec/COFFLoader).

---
