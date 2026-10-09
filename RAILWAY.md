# Railway proposal

Status: design for review, not an implemented service or authorization to provision infrastructure. Official platform documentation checked on 2026-10-09.

## Purpose

Railway would run the application that delivers campaign state and saves accepted turns. Its value is reliable access, controlled writes, recovery, and a convenient reading interface.

The GM still interprets attempts, resolves interactions, and writes fiction under the repository's rules. Hosting cannot guarantee good judgment, faithful characterization, or correct remembered facts. Long-term storage also does not make an LLM's context unlimited.

Working assumption: the player continues in a plain chat. GitHub remains the authoritative campaign record initially.

## Options

| Approach | Playing interface | Authoritative state | Benefit and cost |
| --- | --- | --- | --- |
| Current workflow | Plain chat with GitHub access | Existing Markdown files | Already usable; no Railway bill. Loading and saving depend on the chat's tools or later transcript import. |
| Small Railway service, recommended first hosted scope | Plain chat connected to our campaign tools; optional browser reader | Same GitHub files | One consistent load/save interface, revision checks, and confirmed persistence. Adds hosting, authentication, and another service to maintain. |
| Standalone campaign application | A private website with its own chat | Initially GitHub, or an explicitly planned database migration | Controls the entire turn and saving workflow. Requires a model API, its usage charges, authentication, and substantially more application work. |

A wrapper adds little if the current GitHub workflow already meets the need. Build it for a demonstrated improvement, not merely because hosting is available.

## How a turn would work

1. Select Story 3 in a compatible chat or campaign reader. The service loads the selected campaign and relevant rules from one repository revision.
2. Give the character's action. The GM resolves it using the established capabilities, knowledge, intentions, means, and circumstances, then writes the scene.
3. Under the player's standing permission to save ordinary turns, the chat submits the scene and lasting changes together. It does not need a new approval question after every routine turn.
4. The service checks the campaign, expected revision, and turn identity, then commits the scene and any changed character/world files together. A stale or conflicting update is returned for reconciliation instead of overwriting newer play.
5. Confirm the saved revision. A failed request remains visibly unsaved and can be retried without appending the turn twice.
6. A fresh chat loads that saved position. A reader can show the story and its history.

A deployment alone does not connect this workflow to ChatGPT or any other chat. We must implement and attach a compatible authenticated tool interface, such as a campaign MCP service where supported. The Railway management plugin manages infrastructure; it is not the campaign connection. Confirm the chosen client's read and write capabilities before committing to hosting. If that connection is unavailable, retain direct GitHub play or explicitly choose a standalone app.

## Initial application boundary

One small service should provide campaign listing, loading, history access, accepted-turn saving, and a readable story view. Keep the existing three-file campaign model.

- Read all files for a request from the same commit, including the applicable rules and linked source profile.
- Allow writes only to the selected campaign's permitted live files. Ordinary gameplay must not edit shared rules, other campaigns, or source archives.
- Use one commit for a turn's scene and state changes, with a revision precondition and durable duplicate-request detection.
- Return clear save status. Check structural write errors; do not claim that these checks prove every narrative fact or consequence correct.
- Keep credentials on the server and restrict the connection to the authorized user. Provide a clear way to revoke access.
- Read current campaign data at runtime. A deployed copy of the repository is not the current save.
- Keep caches disposable. A restart must not remove a campaign or turn a successful save into a duplicate.
- Preserve Git history and support explicit restoration through a new corrective commit. Reverting application code is different from restoring story state.

For longer campaigns, current character/world records remain the continuity summary and the story remains the history. Any later selection of recent scenes and on-demand history must be tested for omissions; storage and retrieval do not guarantee that the model uses every relevant fact.

This service would not introduce combat scores, an economic engine, automatic outcome categories, or background turns. Fictional time advances through authorized play, not a server clock.

## Using Railway effectively

The first version needs an app service, not a database stack. GitHub stores accepted campaign data; Railway runs the interface.

Use GitHub-connected deployment for application changes, with CI checks before releases. Configure watch paths so saving a scene does not rebuild the server. Rule and campaign updates should become available through runtime reads.

Use a test environment or local tests with separate fixtures, credentials, and a test branch. Railway's environment separation does not stop a misconfigured application from writing to the same external GitHub branch as production.

Add a deployment readiness check, useful failure logs, and resource monitoring. A Railway deployment healthcheck gates the release; it is not continuous uptime monitoring. Avoid logging credentials or full private conversations. Distinguish a failed deployment from a failed campaign save.

Keep an export or independent backup of the repository and practice restoring a test campaign. Git history helps recover edits, but is not an independent backup of a deleted or inaccessible repository.

## When additional capabilities would earn their place

- PostgreSQL: consider it if concurrent writers, many campaigns, or frequent transactional updates make GitHub unsuitable. Migrate explicitly to one authoritative store and make Markdown an export; avoid two independently editable copies of the same campaign.
- Storage buckets: consider them for large attachments or export bundles, without moving ordinary campaign text merely to use another service.
- Background jobs: use them for authorized exports, backups, or maintenance when needed. Never advance the fictional world while the player is absent.
- A standalone web chat: add it if controlling the full playing interface and automatic saving is worth a separate model API and product maintenance. It can use the same campaign rules.
- More replicas or compute: add them after measured traffic or performance warrants it. Durable state must remain outside disposable app instances.

If persistent volumes are introduced, account for their restrictions: a volume-backed service cannot use replicas and can incur downtime during deployment. Configure backups and test recovery for any database or volume that becomes authoritative. A database is not maintenance-free simply because it runs on Railway.

## Cost and operating decisions

Railway currently lists Hobby at $5 per month and Pro at $20 per month, with the subscription counting toward resource usage. Usage above the included amount increases the bill. This is a pricing baseline, not a quote for this application; measure memory, CPU, storage, and network use in the prototype.

A service that only loads and saves campaign files need not make model API calls itself. A standalone gameplay app would incur separate model-provider usage. Railway Agent usage, if used for infrastructure work, is another metered category and is not required to run the campaign service.

Set an agreed usage alert and, if desired, a hard limit. Railway's minimum hard limit is currently $10; reaching a compute hard limit takes workloads offline. The setting applies at workspace scope, so it can affect other projects. Do not change it without reviewing that scope. Sleep-on-idle may reduce compute use but needs client timeout and startup testing.

## Before building or deploying

Agree on the playing interface, the improvement expected over direct GitHub access, the permitted write scope, and the running budget. Verify client integration rather than assuming every chat can call the service.

The first authorized prototype should demonstrate one complete load, resolve, save, and fresh-session resume. Check a duplicate retry, a stale write, campaign isolation, a service restart, and restoration using test data. These are persistence checks, not a requirement to build a simulation engine or run hundreds of story turns.

Continue with hosting only if that workflow makes play easier and more dependable. No Railway resources, subscriptions, credentials, or deployment configuration were created during this design review.

## Platform sources

These establish platform behavior; the application design above is our proposal.

- [GitHub deployments and CI](https://docs.railway.com/deployments/github-autodeploys)
- [Build configuration and watch paths](https://docs.railway.com/builds/build-configuration)
- [Environments](https://docs.railway.com/environments)
- [Deployment healthchecks](https://docs.railway.com/deployments/healthchecks)
- [Volumes and their restrictions](https://docs.railway.com/volumes/reference)
- [Volume backups](https://docs.railway.com/volumes/backups)
- [Pricing](https://docs.railway.com/pricing)
- [Cost controls](https://docs.railway.com/pricing/cost-control)
