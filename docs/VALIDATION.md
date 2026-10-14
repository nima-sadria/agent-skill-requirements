# Validation status for Xray inbound expert

The skill package, conditional design references, and Python API helper are implemented. Live-panel behavior, autonomous agent behavior, and Iran connectivity have not been validated. Do not describe the package as having universal protocol expertise or proven DPI bypass.

## Completed on 2026-10-14

| Check | Environment | Result |
| --- | --- | --- |
| Skill-creator package validator | Windows, Python 3.12.13; PyYAML available only for the validator | Passed frontmatter/name/scaffold checks. |
| Installer and API helper suite | Windows, Python 3.12.13 | 19 tests passed. |
| Installer and API helper suite | Ubuntu 24.04.5 LTS under WSL, Python 3.12.3 | The same 19 tests passed, including POSIX snapshot permissions. |
| Actual bundle installation | Temporary projects for Codex, Antigravity, and Claude Code; custom destination | Full reference/script bundle installed; installed helper ran; repeat install and existing-edit preservation passed. |

The helper tests use a local fake HTTP panel. They cover base-path preservation, Bearer and cookie/CSRF requests, JSON and form bodies, write preview, response failure/partial-result handling, redacted console output, raw snapshots, output conflicts, redirect refusal, no automatic write retries, invalid input/response handling, and blocking known connectivity-test endpoints. No real panel or ISP was contacted.

## Remaining verification

- Discover and invoke the installed skill in actual Codex, Antigravity, and Claude Code sessions. Copying the bundle into their discovery paths does not establish agent runtime behavior.
- Apply a reviewed configuration to an authorized existing Ubuntu panel using its exact versions/schema, then verify persisted fields and core state.
- Evaluate generated configurations against real client versions and available certificate/domain/listener prerequisites.
- Have the user test connection profiles from the intended Iranian networks and supply results for revision.

The API helper is a transport utility, not a schema validator or automatic configuration generator. Expert choices are instructions and conditional references interpreted by the host agent; scenario outcomes must be evaluated in actual use. Live configuration applies can reload/restart the core, and failures can leave partial persisted state, so the skill requires snapshots and reconciliation.

## Run the maintained tests

```sh
python3 -m unittest discover -s tests -v
```

The installer and helper themselves require only Python 3.10+ standard-library modules. PyYAML is needed only for the separate bundled Codex skill-creator validator, not for normal installation or API requests.
