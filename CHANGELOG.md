# Changelog

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

All notable user-facing changes, combat AI fixes, and system improvements to **TortoiseBots** are documented here.

---

## 2026-09-14

### Combat & Engine
- **Combat Stun Logout Guard:** Prevented gameplay stuns and dazes from erroneously flagging non-master bots for logout, eliminating rapid bot churn and server population drops ([#160](https://github.com/Sagiroth/TortoiseBots/pull/160)).
- **Capital City Non-Combat NPC Filter:** Bots roaming capital cities (for auction house trading or skill training) now ignore neutral/hostile city NPCs like Gamon while out of combat ([#158](https://github.com/Sagiroth/TortoiseBots/pull/158)).
- **Death Handler Debouncing:** Fixed graveyard teleport and spirit healer revives re-triggering death logic up to 6 times per event, preventing phantom graveyard deaths and false hopeless-relocations ([#159](https://github.com/Sagiroth/TortoiseBots/pull/159)).
- **Line-of-Sight & Obstacle Pathing:** Bots give up on unreachable targets and path around physical obstacles to reach targets outside direct line-of-sight ([#157](https://github.com/Sagiroth/TortoiseBots/pull/157)).

### Starter Zones & Rescue
- **Goblin & High Elf Mainland Routing:** Relocating stranded Goblin and High Elf bots now redirects them to canonical mainland starter areas (Valley of Trials / Northshire Abbey) rather than isolated islands or distant Hillsbrad graveyards ([#161](https://github.com/Sagiroth/TortoiseBots/pull/161)).

### Core Integration & Tooling
- **Tortoise 1181dev Core Target:** Updated canonical target core references and Docker build configurations to track Penqle's merged `1181dev` branch ([#162](https://github.com/Sagiroth/TortoiseBots/pull/162)).

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
