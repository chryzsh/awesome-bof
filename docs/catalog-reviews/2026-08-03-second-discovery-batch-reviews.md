# Second Discovery Batch: Limited AI-Assisted BOF Reviews

Codex, an OpenAI GPT-5 agent, performed these limited, AI-assisted reviews on 2026-08-03. Each record covers only the stated source, build, and lint checks at the pinned revision. These notes are not a security audit, an endorsement, or a guarantee that a project is safe, stable, suitable for an engagement, or free of defects. Operators remain responsible for reviewing and testing code before use.

## ADWS-BOF

- Repository: [e-fin/ADWS-BOF](https://github.com/e-fin/ADWS-BOF)
- Review date: 2026-08-03
- Source revision: [`e6871acccb25f125ec55a233ae0012ba5be212b0`](https://github.com/e-fin/ADWS-BOF/tree/e6871acccb25f125ec55a233ae0012ba5be212b0)
- Review scope: source availability and source review. The nested project uses a Windows NMake/MSVC build with a v145 platform toolset; GNU Make cannot parse it on the Linux review host. No artifact was available for `boflint`.
- Observed result: artifact-level build and lint remain unverified in this environment.
- Operational note: connection and network operations use a 120-second timeout ([`adwsldap.cpp`](https://github.com/e-fin/ADWS-BOF/blob/e6871acccb25f125ec55a233ae0012ba5be212b0/ADWS-BOF/adwsldap.cpp#L3151)), then can request up to 100,000 elements and process up to 64 ADWS pull responses ([lines 2705–2738](https://github.com/e-fin/ADWS-BOF/blob/e6871acccb25f125ec55a233ae0012ba5be212b0/ADWS-BOF/adwsldap.cpp#L2705-L2738)). Large or slow queries can block the in-process Beacon for a substantial period.

## GeoLocation_BOF

- Repository: [CodeXTF2/GeoLocation_BOF](https://github.com/CodeXTF2/GeoLocation_BOF)
- Review date: 2026-08-03
- Source revision: [`7094e412e9996884037fa186c9d735297f6b38ed`](https://github.com/CodeXTF2/GeoLocation_BOF/tree/7094e412e9996884037fa186c9d735297f6b38ed)
- Review scope: source availability, the documented x64 and x86 builds, and `boflint`.
- Observed result: both architectures compiled and passed `boflint --loader any`; lint emitted only `.bss` and `.rdata` compatibility warnings.
- Operational note: to enable location services, the BOF can modify per-user and, with administrative rights, machine policy and service settings ([`entry.c`](https://github.com/CodeXTF2/GeoLocation_BOF/blob/7094e412e9996884037fa186c9d735297f6b38ed/entry.c#L586-L616)). It restores them only through cleanup ([lines 974–990](https://github.com/CodeXTF2/GeoLocation_BOF/blob/7094e412e9996884037fa186c9d735297f6b38ed/entry.c#L974-L990)). It may also wait roughly 60 seconds across the primary and fallback location paths, blocking Beacon during that time.

## logon-monitor-bof

- Repository: [jakobfriedl/logon-monitor-bof](https://github.com/jakobfriedl/logon-monitor-bof)
- Review date: 2026-08-03
- Source revision: [`5425ea833a057f9c06837f8f4894481ef6ab2e85`](https://github.com/jakobfriedl/logon-monitor-bof/tree/5425ea833a057f9c06837f8f4894481ef6ab2e85)
- Review scope: source availability, the documented x64 and x86 builds, and `boflint`.
- Observed result: both architectures compiled. Generic `boflint --loader any` reported unsupported `BeaconWakeup` and `BeaconGetStopJobEvent` imports; the project explicitly targets Conquest’s asynchronous object-file loader, which provides those APIs. This is a loader-compatibility constraint, not a result for conventional Cobalt Strike Beacon.
- Operational notes: the monitor intentionally runs until its stop event and must use an asynchronous framework; under a conventional synchronous loader it blocks the Beacon thread. When used with its `--steal-token` option, the accompanying Conquest module automatically dispatches `steal-token <pid> --store` for matching output ([`logon-monitor.py`](https://github.com/jakobfriedl/logon-monitor-bof/blob/5425ea833a057f9c06837f8f4894481ef6ab2e85/dist/logon-monitor.py#L29-L36)); operators should account for that additional action.
