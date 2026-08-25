# TortoiseBots

Optional native PlayerBots module for
[Tortoise WoW 1.18.1](https://github.com/Penqle/tortoise-wow) — harvests
PlayerBots behavior without the old `GetBot()` / `m_bot` coupling.

> **Harvest behavior, not architecture.**

---

## Status

> **WIP — smoke testing and upstream Headless API still pending.**

- [x] Native module, 9 Vanilla classes, Vanilla/Turtle 1.18.1 cleanup completed
- [x] Headless lifecycle + builds validated (module-enabled and `MODULES=disabled`)
- [ ] Smoke test against current Penqle `main`
- [ ] Upstream generic Headless API
- [ ] Manual owned-bot and 5-player dungeon acceptance

Validated: module-enabled/disabled builds, world-ready startup, Headless login / AI / save / logout / relogin, human reclaim, `.bot` dispatch + group invite, Goblin/High Elf fixtures, repeatable migrations. Pinned core/module SHAs in Git history.

---

## Penqle dependencies

Targets [Penqle/tortoise-wow](https://github.com/Penqle/tortoise-wow).

> [!IMPORTANT]
> **Requires [Penqle#411](https://github.com/Penqle/tortoise-wow/pull/411) (`feature/headless-world-session`) until merged.** Plain `Penqle/main` lacks `SessionTransport::Headless` and will fail to link.

Core exposes generic **Headless sessions** (not PlayerBots concepts) — network/headless types, GUID-keyed Headless lifecycle, deferred login, `World`-owned session lifetime, and generic lifecycle/packet hooks. TortoiseBots assigns bot meaning to them; no bot-specific core fork required.

---

## Features

- Same-account bots (`.bot add` / `remove`) with human reclaim
- Party: follow / stay / invite via `.bot` (group AI)
- Class AI for all 9 Vanilla classes — basic combat / heal / tank
- Loot, quest and travel / taxi handling
- Turtle Goblin / High Elf and Turtle spell / talent / mount handling where validated
- Bounded random bots for existing characters only

Targets Vanilla/Turtle 1.18.1 — Death Knights, glyphs, vehicles and arenas are not included.

---

## Architecture

Native optional module, not a vendored core fork:

```text
Penqle / Tortoise core  — generic Headless / lifecycle / packet hooks
        |
TortoiseBots — BotManager + PlayerbotAIAdapter/Storage + host adapters + PlayerbotAI (Strategy/Trigger/Action/Value)
```

- Session: `one account → at most one Network session + N Headless (GUID-keyed)`. Core owns `WorldSession` lifetime; module owns bot records/AI.
- Core gameplay never checks `IsBot()` / `GetBot()` / `m_bot` / `sPlayerBotMgr`.

Details: [`docs/HOST_API.md`](docs/HOST_API.md), [`docs/PLAN.md`](docs/PLAN.md).

---

## Commands

```text
.bot add | remove | follow | invite | uninvite | stay | list | stats | command | help
```

`.bot command` forwards to the mature PlayerBots command system. Ownership/GM checks enforced.

---

## Module layout

Consumed as `tortoise-wow/modules/TortoiseBots/`:

```text
ai/        PlayerBots AI + Turtle shims    host/      Penqle boundary
runtime/   Bot lifecycle / AI ownership    commands/  Native .bot
conf/      tortoise_bots.conf.dist         data/sql/  world/ + character migrations
src/       Native entrypoint               docs/      Architecture / provenance
```

---

## Build

```text
BUILD_LEGACY_PLAYERBOTS=OFF
MODULES=static
MODULE_TORTOISEBOTS=static
```

See [`AGENTS.md`](AGENTS.md) for workflow.

---

## Configuration

```text
conf/tortoise_bots.conf.dist
ai/playerbot/aiplayerbot.conf.dist.in
data/sql/world/  data/sql/char/
```

Inherited config is broader than validated Turtle surface — a setting existing does not mean it's gameplay-tested.

---

## References

- Canonical core: [Penqle/tortoise-wow](https://github.com/Penqle/tortoise-wow)
- Donors (behavior refs, not target): [Knowledge Base](https://github.com/tortoise-wow-stack/TortoiseWoWKnowledgeBase), [cmangos/playerbots](https://github.com/cmangos/playerbots), [Shyalya](https://github.com/Shyalya/tortoise-wow), [MangosZero](https://github.com/mangoszero/server), [mod-playerbots](https://github.com/mod-playerbots/mod-playerbots) — lineage in [`docs/PROVENANCE.md`](docs/PROVENANCE.md)

---

## Licence

- **TortoiseBots module** — GPL-2.0 (donor headers in `ai/playerbot/`)
- **Penqle/tortoise-wow** — AGPL-3.0 — combined binary is AGPL-3.0

See [`LICENCE.md`](LICENCE.md).

---

## Documentation

- [`docs/PLAN.md`](docs/PLAN.md) — architecture / roadmap
- [`docs/HOST_API.md`](docs/HOST_API.md) — host contract
- [`AGENTS.md`](AGENTS.md) — contributor / agent rules
- [`docs/PROVENANCE.md`](docs/PROVENANCE.md) — donor lineage
- [`LICENCE.md`](LICENCE.md) — licences

History in Git and `docs/archive/` if retained.
