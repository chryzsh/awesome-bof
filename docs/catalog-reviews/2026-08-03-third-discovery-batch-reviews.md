# Third Discovery Batch: Limited AI-Assisted BOF Reviews

Codex, an OpenAI GPT-5 agent, performed these limited, AI-assisted reviews on 2026-08-03. Each record covers only the stated source, build, and lint checks at the pinned revision. These notes are not a security audit, an endorsement, or a guarantee that a project is safe, stable, suitable for an engagement, or free of defects. Operators remain responsible for reviewing and testing code before use.

## Entropia

- Repository: [entropykit/entropia](https://github.com/entropykit/entropia)
- Review date: 2026-08-03
- Source revision: [`05acaba2a1a5fbde8cec3318319d053265ddb7ca`](https://github.com/entropykit/entropia/tree/05acaba2a1a5fbde8cec3318319d053265ddb7ca)
- Review scope: source availability, release build, compilation of the `bof_pslist` example, and `boflint`.
- Observed result: `cargo build --release` and example compilation succeeded. The generated x64 object has a `go` entry point and DFR imports; `boflint --loader any` emitted only `.rdata` and `.bss` compatibility warnings.
- Operational note: the project labels itself experimental. Generated BOFs should be tested with the intended loader because `.rdata` and `.bss` are not supported by every loader.

## async-pico-hub

- Repository: [nccgroup/async-pico-hub](https://github.com/nccgroup/async-pico-hub)
- Review date: 2026-08-03
- Source revision: [`e88b19552cc5f716542094bcb4b1a0fbba5fe4c5`](https://github.com/nccgroup/async-pico-hub/tree/e88b19552cc5f716542094bcb4b1a0fbba5fe4c5)
- Review scope: source and build documentation. The project requires Windows MSVC plus Crystal Palace and Tradecraft Garden. A Linux GNU C++ build is unsupported and produced no object to lint.
- Observed result: artifact-level build and lint remain unverified in this environment.
- Operational note: the framework requires a modified sleepmask and uses shared global state across concurrent PICOs. Its stop control path can synchronously wait up to 30 seconds for a PICO to exit ([`handle_stop.h`](https://github.com/nccgroup/async-pico-hub/blob/e88b19552cc5f716542094bcb4b1a0fbba5fe4c5/async-pico-mgr-bof/src/commands/handle_stop.h#L20-L25)).

## GDID-Extractor

- Repository: [5mukx/GDID-Extractor](https://github.com/5mukx/GDID-Extractor)
- Review date: 2026-08-03
- Source revision: [`2c9bceacbdd20a814b5c800a7a23a3706996664c`](https://github.com/5mukx/GDID-Extractor/tree/2c9bceacbdd20a814b5c800a7a23a3706996664c)
- Review scope: source availability, documented MinGW x64/x86 builds, and `boflint`.
- Observed result: both architectures compiled. Rebuilt x64 passed lint with an `.rdata` warning. Rebuilt x86 has an unresolved `___udivmoddi4` helper, so it may not load in loaders that cannot resolve that compiler runtime symbol.
- Provenance note: at review, the owner account was created on 2026-07-05 and the repository on 2026-07-16; the pinned source had one commit and the account had two public repositories. This is limited public history, not evidence of malicious intent; inspect source and build artifacts independently before use.
