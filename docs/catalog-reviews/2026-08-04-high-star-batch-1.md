# High-Star Batch 1: Limited AI-Assisted BOF Reviews

Codex, an OpenAI GPT-5 agent, performed these limited, AI-assisted reviews on 2026-08-04. They are not a security audit, endorsement, or guarantee. Operators remain responsible for reviewing and testing code before use.

## nanodump

- Repository: [fortra/nanodump](https://github.com/fortra/nanodump), revision [`450d5b23aeba5e0f8f6e5fc826a08997b2237be9`](https://github.com/fortra/nanodump/tree/450d5b23aeba5e0f8f6e5fc826a08997b2237be9).
- Scope: documented MinGW build and `boflint` of produced artifacts.
- Observed result: the full documented build fails because the PPL Medic header and implementation disagree on a function signature. Six artifacts are produced before failure; all checked artifacts pass lint except x86 SSP, which has an unresolved `_NtClose` import.
- Operational note: the LSASS dump path allocates 200 MiB before dumping, writing, or downloading ([`entry.c:190–230`](https://github.com/fortra/nanodump/blob/450d5b23aeba5e0f8f6e5fc826a08997b2237be9/source/entry.c#L190-L230)); it is resource- and time-intensive in Beacon.

## CS-Situational-Awareness-BOF

- Repository: [trustedsec/CS-Situational-Awareness-BOF](https://github.com/trustedsec/CS-Situational-Awareness-BOF), revision [`ecdb7e35b053cc4cfc286de431a4017a9f8b4a96`](https://github.com/trustedsec/CS-Situational-Awareness-BOF/tree/ecdb7e35b053cc4cfc286de431a4017a9f8b4a96).
- Scope: `make_all.sh` and `boflint` for generated x86 and x64 artifacts.
- Observed result: 71 source directories built 142 artifacts without logged compiler errors. 141 passed lint; `driversigs.x86.o` has an unresolved `_strlen` import.
- Operational note: the upstream README warns that `nslookup` can crash in some situations and LDAP ACL pagination may break; these upstream caveats were not independently reproduced in this review.

## SCShell

- Repository: [Mr-Un1k0d3r/SCShell](https://github.com/Mr-Un1k0d3r/SCShell), revision [`a507238682019d944f3300bd97cd6bec81c63870`](https://github.com/Mr-Un1k0d3r/SCShell/tree/a507238682019d944f3300bd97cd6bec81c63870).
- Scope: documented BOF build and `boflint` for x64, x86, and import variants.
- Observed result: all four artifacts built and passed lint.
- Operational note: the BOF changes the target service to demand start, but its restore path also sets demand start rather than the original start type ([`scshellbof.c:89,107`](https://github.com/Mr-Un1k0d3r/SCShell/blob/a507238682019d944f3300bd97cd6bec81c63870/CS-BOF/scshellbof.c#L89)); a successful run can leave persistent service-configuration drift.
