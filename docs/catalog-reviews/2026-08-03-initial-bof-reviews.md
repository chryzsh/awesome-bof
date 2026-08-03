# Initial BOF reviews

## Scope and disclaimer

Codex, an OpenAI GPT-5 agent, performed these limited, AI-assisted reviews on 2026-08-03. Each record covers only the stated source, build, and lint checks at the pinned revision. These notes are not a security audit, an endorsement, or a guarantee that a project is safe, stable, suitable for an engagement, or free of defects. Operators remain responsible for reviewing and testing code before use.

## RawHive

- Repository: [nmht3t/RawHive](https://github.com/nmht3t/RawHive)
- Review date: 2026-08-03
- Source revision: [`2ffc0ffaa92e5652c11e93d630ac70480a036885`](https://github.com/nmht3t/RawHive/tree/2ffc0ffaa92e5652c11e93d630ac70480a036885)
- Review scope: source availability, x64 MinGW build, and `boflint`.
- Observed result: the x64 object compiled, and `boflint` exited with status 0.
- Operational note: the fallback path scans up to 500,000 MFT records ([source](https://github.com/nmht3t/RawHive/blob/2ffc0ffaa92e5652c11e93d630ac70480a036885/rawhive.c#L430)). The scan may block Beacon for a long time on large volumes.

## evtxsearch-bof

- Repository: [tothi/evtxsearch-bof](https://github.com/tothi/evtxsearch-bof)
- Review date: 2026-08-03
- Source revision: [`638f94a54ba1a4af5e6fb374df7e841515c06f8f`](https://github.com/tothi/evtxsearch-bof/tree/638f94a54ba1a4af5e6fb374df7e841515c06f8f)
- Review scope: source availability, x64 and x86 MinGW builds, and `boflint`.
- Observed result: the x64 and x86 objects compiled, and `boflint` exited with status 0 for both.
- Operational note: the event loop calls `EvtNext` with an infinite wait ([source](https://github.com/tothi/evtxsearch-bof/blob/638f94a54ba1a4af5e6fb374df7e841515c06f8f/bof/evtxsearch.c#L309)). A stalled query may block Beacon indefinitely.

## DNSRPC-BOF

- Repository: [Paradoxis/DNSRPC-BOF](https://github.com/Paradoxis/DNSRPC-BOF)
- Review date: 2026-08-03
- Source revision: [`cc3978f74c40fc356cd36ebc3458901d18913d88`](https://github.com/Paradoxis/DNSRPC-BOF/tree/cc3978f74c40fc356cd36ebc3458901d18913d88)
- Review scope: source availability and the documented MinGW build.
- Observed result: the documented MinGW build failed because of incompatible RPC-hook declarations and types.
- Operational note: the project's README states that its exception hook may destabilize Beacon ([README](https://github.com/Paradoxis/DNSRPC-BOF/blob/cc3978f74c40fc356cd36ebc3458901d18913d88/README.md)).
