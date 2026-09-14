# Changelog

## 2026-09-14

### Combat & AI
- New `.bot role <name> tank|healer|dps|clear` forces a bot's role; tank kits now mirror native AiFactory strategies (`protection`/`tank feral`, `tank assist`, `pull`, `pull back`, `close`) (#167)
- Pull candidate selection is now deterministic: explicit role > designated tank > native spec. Bots attach `+pull` dynamically and never guess DPS (#167)
- Fixed the movement freeze during pull/pullback sequences — bots now reposition cleanly instead of stalling (#167)
- Ranged bots correctly fall back to ranged attacks when a melee pull isn't viable (#167)
- DPS bots hold their threat during the tank's pull window instead of ripping aggro immediately (#167)

### Addon Integration & Commands
- New silent TBM addon command channel: the companion addon can drive `.bot` commands as addon messages, with responses returned on the same transport (#165)
- UI clicks no longer spam the chat frame or echo to nearby players — quieter, cleaner bot management (#165)
- `BotAddonAdapter` hooks `PLAYERHOOK_ON_ADDON_MESSAGE`, consumes `TBM`-prefixed payloads, and routes them through the existing `BotCommands::HandleChatCommand` entry point (same grammar, same GM authorization) (#165)

### Documentation & Contracts
- `docs/HOST_API.md` baseline realigned to merged upstream core `main` @ `5fafe43b` (#164)
- Documented the module chat-hook contract settled by core PR #476, recording merged carriers for every dependent seam (#438, #469, #475, #476, #493) (#164)

## 2026-09-14

### Combat & AI
- Bots now path around obstacles to reach targets that are out of line of sight instead of walking into walls; targets that stay unreachable for 15s get blacklisted per-bot for 5 minutes, killing the `invalid target` trigger spam (#157)
- Capital city critters and NPCs are no longer grind targets — no more random bots picking fights with Gamon while the player is just trying to use the auction house; anything that attacks the bot still gets fought back (#158)

### Starter Zones & World
- Goblin and High Elf bots rescued by `TeleportMisplacedBot` are now routed to their homebind instead of being dumped on Blackstone Island or stranded in Hillsbrad at level 5 — no more bots stuck in zones with no way out (#161)

### Core Sync & Fixes
- Death is now logged and counted exactly once: repeated `OnDeath` fires during graveyard teleport and spirit-healer revive no longer inflate death counts several times per second (#159)
- Removed the bogus `UNIT_STAT_STUNNED` logout check — combat stuns no longer trigger a bot logout, restoring correct `isLogingOut()`-based behavior from the donor core (#160)

### Tooling & Docs
- Added `tools/generate_changelog.py` plus a `CHANGELOG.md` seed and a `generate-changelog.yml` workflow, so releases can be generated from merged PRs with OpenCode AI instead of hand-writing notes (#163)
- Updated canonical target core branch references from `bot-helpers` to `1181dev` in `README.md` and `CONTRIBUTING.md` after the upstream merge (#162)

---

## 2026-09-13

### Starter Zones & Survival
- **Unsurvivable Zone Repatriation:** Repatriate alive bots stranded in zones significantly above their level range ([#155](https://github.com/Sagiroth/TortoiseBots/pull/155)).
- **Custom Starter Island Blacklist:** Route Goblin and High Elf bots to standard starter zones and blacklist custom islands lacking egress paths ([#149](https://github.com/Sagiroth/TortoiseBots/pull/149)).
- **Classic Zone Level Population:** Populated `ai_playerbot_zone_level` with classic zone level mappings ([#148](https://github.com/Sagiroth/TortoiseBots/pull/148)).
- **Low-Level Travel Gating:** Reject travel destinations whose route crosses zones the bot cannot survive, keeping bots below level 10 within their starter regions ([#147](https://github.com/Sagiroth/TortoiseBots/pull/147), [#150](https://github.com/Sagiroth/TortoiseBots/pull/150), [#153](https://github.com/Sagiroth/TortoiseBots/pull/153)).

### Observability & AI
- **Rage Telemetry Units:** Converted rage values to normal 0-100 display units for dashboard visualization ([#154](https://github.com/Sagiroth/TortoiseBots/pull/154)).
- **Stuck Detector Sampling:** Throttled stuck evaluation to once per second rather than every world tick ([#152](https://github.com/Sagiroth/TortoiseBots/pull/152)).
- **AI Texts & Item Casting:** Seeded `ai_playerbot_texts` and repaired item cast validation checks ([#151](https://github.com/Sagiroth/TortoiseBots/pull/151)).
