# Changelog

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
