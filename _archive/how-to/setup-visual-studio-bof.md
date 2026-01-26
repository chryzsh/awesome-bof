# How-To: Setting Up Visual Studio for BOF Development

This guide will show you how to configure Visual Studio (VS) for BOF (Beacon Object File) development. Visual Studio provides a powerful IDE for C/C++ with features like IntelliSense, build configuration, and debugging.

---

## 🎯 Goal
- Create a Visual Studio project for BOF development
- Use templates to simplify the process
- Build .o (COFF) files compatible with Cobalt Strike and other C2s
- Test your code outside of Beacon

---

## 🔧 Prerequisites
- Visual Studio 2019 or later (Community Edition is fine)
- C++ Desktop Development workload installed
- Git (optional, for pulling templates)

---

## 📁 Step 1: Use the Fortra BOF Visual Studio Template
Fortra provides a [Beacon Object File Visual Studio Template](https://github.com/Cobalt-Strike/bof-vs) designed to streamline the BOF development workflow. The project is preconfigured to:
- Build a `.o` file when targeting for `Release`
- Build a `.dll` or `.exe` for local testing when targeting for `Debug`
- Include `beacon.h`

Steps

- Download their latest release ZIP.
- Copy `bof-vs.zip` to `%USERPROFILE%\Documents\Visual Studio 2022\Templates\ProjectTemplates`. You do not need to extract it.

---

## 🛠️ Step 2: Create Your Project

- Open Visual Studio.
- Select `Create a new project`, search for `BOF` and you will see a BOF project template.
![alt text](../resources/image.png)

---

## ⚙️ Step 3: Explore Project Structure
![alt text](../resources/image-1.png)
- `bof.c` — Your main BOF source file with the `go()` entry point.
- `beacon.h` — Cobalt Strike Beacon API header.
- `Makefile` - For building

---

## 🧪 Step 4: Test Locally

The template allows running your BOF logic outside of Beacon:

- Build the project in `x64/Debug` mode.
- Start debugging in VS, or:
   - Run the generated `.exe` or `.dll` to simulate execution.

> Great for debugging logic and argument parsing before loading into a C2.

---

## 📤 Step 5: Use the .o File in Beacon

After building for `Release`, you'll find the `.o` file in your `x64/Release` directory.

To execute it, in Cobalt Strike:
```powershell
inline_execute mybof.o
```

---

## ✅ Summary
With the Visual Studio template from Fortra, you can:
- Develop BOFs in a familiar IDE
- Test code outside of C2
- Export `.o` files with minimal effort

---