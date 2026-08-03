# First Discovery Batch: Limited AI-Assisted BOF Reviews

Codex, an OpenAI GPT-5 agent, performed these limited, AI-assisted reviews on 2026-08-03. Each record covers only the stated source, build, and lint checks at the pinned revision. These notes are not a security audit, an endorsement, or a guarantee that a project is safe, stable, suitable for an engagement, or free of defects. Operators remain responsible for reviewing and testing code before use.

## COM-Hunter

- Repository: [nickvourd/COM-Hunter](https://github.com/nickvourd/COM-Hunter)
- Review date: 2026-08-03
- Source revision: [`f410d2633cb5c9a2de67246535a024805bcc1466`](https://github.com/nickvourd/COM-Hunter/tree/f410d2633cb5c9a2de67246535a024805bcc1466)
- Review scope: source availability, the documented MinGW build, and `boflint` for x64 and x86 artifacts from all five modules.
- Observed result: `make_all.sh` completed, and all ten artifacts passed `boflint --loader any`; lint emitted only `.rdata` compatibility warnings.
- Operational notes: the five modules do not validate extracted BOF arguments before use ([persist](https://github.com/nickvourd/COM-Hunter/blob/f410d2633cb5c9a2de67246535a024805bcc1466/BOF/com_hunter_persist/entry.c#L238-L240), [remove](https://github.com/nickvourd/COM-Hunter/blob/f410d2633cb5c9a2de67246535a024805bcc1466/BOF/com_hunter_remove/entry.c#L179-L181), [search](https://github.com/nickvourd/COM-Hunter/blob/f410d2633cb5c9a2de67246535a024805bcc1466/BOF/com_hunter_search/entry.c#L200-L202), [Task Scheduler](https://github.com/nickvourd/COM-Hunter/blob/f410d2633cb5c9a2de67246535a024805bcc1466/BOF/com_hunter_tasksch/entry.c#L234-L235), and [TreatAs](https://github.com/nickvourd/COM-Hunter/blob/f410d2633cb5c9a2de67246535a024805bcc1466/BOF/com_hunter_treatas/entry.c#L315-L318)). A malformed argument buffer can lead to a null dereference in Beacon. Fixed 512-byte registry-key buffers also use unchecked `_snprintf` ([example](https://github.com/nickvourd/COM-Hunter/blob/f410d2633cb5c9a2de67246535a024805bcc1466/BOF/com_hunter_persist/entry.c#L10-L14)); oversized inputs can yield a truncated, unterminated path.

## CLR-Stomp

- Repository: [nettitude/CLR-Stomp](https://github.com/nettitude/CLR-Stomp)
- Review date: 2026-08-03
- Source revision: [`c6b995a1c27daab11ffbcb149c7a423e4ce69080`](https://github.com/nettitude/CLR-Stomp/tree/c6b995a1c27daab11ffbcb149c7a423e4ce69080)
- Review scope: source availability and source review. The documented build requires Visual Studio `cl.exe`; it could not run on the Linux review host, and MinGW lacks `metahost.h`. No checked-in artifact was available for `boflint`.
- Observed result: artifact-level build and lint remain unverified in this environment.
- Operational notes: CLR-Stomp temporarily changes the Beacon process environment while starting the CLR ([`go.c`](https://github.com/nettitude/CLR-Stomp/blob/c6b995a1c27daab11ffbcb149c7a423e4ce69080/go.c#L529-L575)); another thread initializing the CLR during that interval can inherit those settings. It also redirects stdout to a synchronous named pipe with no timeout and reads it only after managed invocation returns ([`go.c`](https://github.com/nettitude/CLR-Stomp/blob/c6b995a1c27daab11ffbcb149c7a423e4ce69080/go.c#L694-L735)); a blocking payload, inherited pipe handle, or back-pressure can block Beacon indefinitely.

## ShellHWEventExec

- Repository: [0xHossam/ShellHWEventExec](https://github.com/0xHossam/ShellHWEventExec)
- Review date: 2026-08-03
- Source revision: [`310f5ddcbcff339dc03e20c6e95c612449273621`](https://github.com/0xHossam/ShellHWEventExec/tree/310f5ddcbcff339dc03e20c6e95c612449273621)
- Review scope: source availability, lint of the checked-in x64 object, and a MinGW x64 rebuild check.
- Observed result: the checked-in `compiled/autoplay_hwevent_bof.x64.o` passed `boflint --loader any` with only `.rdata` compatibility warnings. The MinGW rebuild compiled but emitted a `___chkstk_ms` dependency because of local buffers, so it needs loader-compatible toolchain validation before use.
- Operational note: optional event and device strings are converted into fixed 256-wide-character buffers without checking `MultiByteToWideChar` ([`autoplay_hwevent_bof.c`](https://github.com/0xHossam/ShellHWEventExec/blob/310f5ddcbcff339dc03e20c6e95c612449273621/autoplay_hwevent_bof.c#L77-L78)). Oversized inputs can leave the subsequent COM call ([line 114](https://github.com/0xHossam/ShellHWEventExec/blob/310f5ddcbcff339dc03e20c6e95c612449273621/autoplay_hwevent_bof.c#L114)) with a non-guaranteed terminated buffer, causing incorrect behavior or a Beacon crash.
