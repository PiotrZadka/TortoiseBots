# HOST_API — current TortoiseBots host contract

**Target:** Tortoise WoW 1.18.1 core
**Purpose:** describe the implemented generic core/module boundary used by TortoiseBots.

This file describes the current contract. Historical Phase 1 discovery and design
proposals remain available in Git history and are not active implementation
instructions.

## 1. Boundary rule

The core exposes generic capabilities. TortoiseBots assigns bot meaning to those
capabilities.

```text
Tortoise core
    -> session / lifecycle / packet / module primitives
TortoiseBots
    -> bot records / AI / commands / gameplay behavior
```

Normal gameplay systems should not require PlayerBots-specific state. Do not
reintroduce `WorldSession::GetBot()`, `WorldSession::SetBot()`, `m_bot`,
`sPlayerBotMgr`, `PlayerBotEntry`, or scattered bot checks in normal gameplay
code.

## 2. Compatible baseline

The supported local host boundary is validated against:

```text
Pinned Tortoise core checkpoint:     7353989c94399f80572a2f8ec2eb73c63a6c79f8 (historical pin; branch `cleanup/f03-f27-code-freeze`)
TortoiseBots tested code checkpoint: 07cf7976c546fac27083c7b46e73299c25b095f3
```

Validated local core checkpoint:
`7353989c94399f80572a2f8ec2eb73c63a6c79f8` (historical branch `cleanup/f03-f27-code-freeze`)

Upstream status:
generic Headless capability proposed as draft PR [#411](https://github.com/Penqle/tortoise-wow/pull/411)
(`feature/headless-world-session` @ `c37e28b`, based on upstream `main`
`61a8269`; merge-base `93a5faa`). Not yet merged; the pinned branch remains the validated baseline until #411 lands.

When the core changes, record the exact tested core/module pair
(e.g. in the commit message and README) instead of assuming compatibility from a branch name.

## 3. Session transport

`WorldSession` distinguishes transport capability from gameplay identity:

```text
SessionTransport::Network
SessionTransport::Headless
```

Generic transport queries include `IsHeadless()` and
`HasNetworkTransport()`. TortoiseBots interprets a Headless session as
module-controlled; the core does not expose a bot object through
`WorldSession`.

Headless initialization uses the core's null/no-network anticheat path rather
than pretending a real socket exists.

## 4. Session registry and lifetime

The supported invariant is:

```text
one account
    +-- at most one active Network session
    +-- zero or more active Headless character sessions
```

Network sessions are account-keyed. Headless sessions are character-GUID keyed.
`World` owns both Network and Headless `WorldSession` lifetime.

The generic Headless lifecycle supports queue/register, GUID lookup, pending
inspection/cancellation, removal and shutdown cleanup. Headless sessions do not
become extra real Network sessions for the normal account-session map.

TortoiseBots owns lifecycle records and AI adapters, not `WorldSession*`
lifetime.

## 5. Async login dispatch

Async login state carries identity instead of a retained raw session pointer:

```text
accountId
characterGuid
SessionTransport
```

Completion resolves the appropriate registry:

```text
Network  -> account-keyed session
Headless -> character-GUID-keyed session
```

This keeps one Network master plus multiple Headless characters unambiguous.
`BotSessionAdapter` queues the Headless session and then uses the normal
Tortoise character-login path rather than duplicating player loading or map
entry.

## 6. Human reclaim

A real Network session takes precedence when the same character returns under
human control. The core performs normal session/player lifecycle work;
TortoiseBots releases or rebinds its record/AI state as appropriate.

The durable master relationship remains module-owned. The core only owns the
generic session/player lifecycle.

## 7. Native lifecycle hooks

TortoiseBots integrates through the native module/script system rather than
hard-wired manager calls in unrelated core files.

Current adapters:

| Adapter | Responsibility |
| --- | --- |
| `BotHostAdapter` | startup, shutdown and world update |
| `BotSessionAdapter` | Headless session lifecycle |
| `BotPlayerAdapter` | player lifecycle/reclaim attachment |
| `BotChatAdapter` | native `.bot` command integration |
| `BotPacketAdapter` | packet bridge into Existing PlayerBots (primarily AzerothCore/mod-playerbots) |

The module should prefer an existing generic hook before requesting a new core
seam.

## 8. World update

Bot AI runs on the normal world/game thread. The core exposes a generic world
update listener mechanism, and `BotHostAdapter` drives `BotManager` / AI updates
from that tick.

The core listener is generic; it does not call a PlayerBots singleton.

## 9. Ownership model

| Responsibility | Owner |
| --- | --- |
| Network `WorldSession` lifetime | Tortoise `World` |
| Headless `WorldSession` lifetime | Tortoise `World` |
| Pending Headless queue | Tortoise `World` |
| Bot record lifecycle | `BotManager` |
| AI lifetime | `PlayerbotAIAdapter` |
| AI lookup | `PlayerbotAIStorage` |
| Gameplay decisions | `PlayerbotAI` |
| Movement semantics | Existing PlayerBots (primarily AzerothCore/mod-playerbots) actions/strategies |
| Durable master GUID | `BotRecord.masterGuid` |
| Live master pointer | `PlayerbotAI` |

A second owner for session lifetime, AI state, movement or master identity is an
architecture warning.

## 10. Packet bridge

The core exposes generic packet send/receive hooks. `BotPacketAdapter` is the
module packet interpretation layer:

```text
Headless outgoing
    -> PlayerbotAI::HandleBotOutgoingPacket

Network master outgoing
    -> owned AIs HandleMasterOutgoingPacket

Network master incoming
    -> owned AIs HandleMasterIncomingPacket
```

No bot-specific opcode branches belong in core packet handlers.

The recorded fixture exercised Headless outgoing delivery, Network-master
outgoing delivery and the existing group-invite Trigger -> Action acceptance
path. Real-client incoming delivery remains a separate manual-client acceptance
boundary.

## 11. Command contract

TortoiseBots owns the native `.bot` surface. Current commands include:

```text
add
remove
follow
invite
uninvite
stay
list
stats
command
help
```

`.bot command` delegates to `PlayerbotAI::HandleCommand` for Existing PlayerBots (primarily AzerothCore/mod-playerbots)
command behavior. Authorization uses the normal account/GM policy implemented
by the module/core boundary.

## 12. Native module/build contract

The core consumes the repository at:

```text
modules/TortoiseBots/
```

`src/TortoiseBotsModule.cpp` is intentionally the only loader-recursed source.
The broader source graph is registered by `TortoiseBots.cmake`.

Normal native selection:

```text
BUILD_LEGACY_PLAYERBOTS=OFF
MODULES=static
MODULE_TORTOISEBOTS=static
```

`BUILD_LEGACY_PLAYERBOTS` controls the separate legacy escape hatch; it is not
the native module selector.

Static module compile definitions/includes/PCH are isolated to the
TortoiseBots module target before it is folded into the combined modules
archive (local integration baseline; not yet upstream in #411 — separate
follow-up).

## 13. Configuration and database contract

The module owns:

```text
conf/tortoise_bots.conf.dist
ai/playerbot/aiplayerbot.conf.dist.in
data/sql/world/
data/sql/char/
```

Schema belongs in migrations, not surprise runtime DDL. Missing optional data
should fail closed or use an explicit supported fallback. Expensive travel/cache
generation must not start implicitly on the world thread.

The inherited AI config is broader than the currently accepted Turtle product;
a config key existing is not itself a support claim.

## 14. Turtle data contract

Turtle-specific legality/content should come from the target core/data where
possible:

- race/class legality from core player data;
- race/team identity from core data;
- start locations from `playercreateinfo`;
- Turtle spells/talents/items from local DBC/SQL;
- collection mounts from the target mapping;
- LFG/meeting-stone and taxi behavior from native core APIs.

Do not replace target data with old Vanilla tables when the target already owns
the answer.

**Goblin / High Elf spawn — closed / fixed:** `TravelNodeMap::generateStartNodes()` (`ai/playerbot/TravelNode.cpp`) and `PlayerbotAIConfig` legality derive start positions and race/class validity from core `PlayerInfo` (`sObjectMgr.GetPlayerInfo` over `playercreateinfo`); `ReleaseSpiritAction::RepopAction` uses that `PlayerInfo` position with `homebind` fallback only when no row exists. No `RACE_GOBLIN`→Durotar / `RACE_HIGH_ELF`→Elwynn donor hack is present and none should be re-added. Shipped `maps/0013245.map`+`mmaps/0013245.mmtile` (Goblin) and `maps/0002536.map`+`mmaps/0002536.mmtile` (High Elf) complete the data path — no module code or data change required. Movement/LoS acceptance and the separate High Elf `vmaps/000_25_36` gap remain distinct (tracked in `08_VMAPS_HIGHELF.md` / audit F-06) and are not claimed as tested here.

## 15. Unsupported capabilities

When a donor behavior has no meaningful equivalent in the pinned core, adapt it
to a real API, remove/disable it, or fail closed. Do not return fake success
only to satisfy a donor interface.

The completed audit removed or disabled several such compatibility surfaces;
see [PLAYERBOTS_AUDIT.md](archive/PLAYERBOTS_AUDIT.md) for evidence.

**RNDBOT auto-create — deferred gate:** `AccountMgr::CreateAccount` and the generic
Headless session lifecycle (§4–§5) are reusable generic boundaries. The pinned target
core exposes no generic character-materialization API; do not copy `CharacterHandler`
validation or run `Player::Create` / `SaveToDB` / `PlayerbotFactory` on a database
worker. `RNDBOT` auto-create remains deferred until a generic core-owned
character-creation seam is proven and documented here. Default discover-only
`RandomBotService` behavior is retained (existing `RNDBOT%` accounts/characters only,
no `INSERT`), and this contract claims no module, core, or data changes for
auto-create.

**LFT / RNDBOT auto-fill — deferred gate:** Current pinned-core `LFTManager` (`src/game/LFT/LFTMgr.h/cpp`, queue/offer bodies in its intentionally named `LFTQeueue.cpp`) owns private `m_queue` (`QueueMap`/`QueuedPlayer`), `m_offers`/`m_rolechecks`/`m_listings` and offer/rolecheck/group lifecycle (`Update`/`TryMakeOffers`/`CancelOffer`/`CompleteOffer`); TortoiseBots has no generic participant/proposal hook. LFT/RNDBOT auto-fill remains deferred until the 5-player dungeon MVP and a proven type-agnostic, core-owned lifecycle. Prohibited: direct `m_queue` mutation, owning a second queue, `RNDBOT` hardwire in core, or fake config/behavior (`LFTBotFill.Enabled`/`DelaySeconds`). Native LFT/meeting-stone and manual `.bot invite` remain authoritative; no module, core, or data changes claimed.

**AH market (AhBot) — deferred gate:** Current per-bot `AhAction` (`ai/playerbot/strategy/actions/AhAction.cpp` via `GetCheckedAuctionHouseForAuctioneer` + `HandleAuctionSellItem`/`HandleAuctionPlaceBid` and `sAuctionMgr.GetAuctionsMap(...)->GetAuctionsSnapshot()` under `sRandomBotFacade.m_ahActionMutex.try_lock()`) uses live auctioneer/session native handlers; no population market service exists (`ahbot/*` absent, no `RandomBotService::SeedAhMarket()`). Market seeding is deferred until the 5-player dungeon MVP and a verified native transaction/item-ownership acceptance path. Prohibited: donor 900-second update thread, direct `AuctionHouseMgr`/`auctionhouse` DB ownership, fabricated `AddAuction`/`Category::GetBag`/`AhAction::Sell`/`RandomBotFacade::GetAuctionsSnapshot` APIs, and default-on/per-tick scans. No code/config/data change is claimed.

**BG auto-queue (WSG/AB/AV) — deferred gate:** Manual `BattleGroundJoinAction` (`BGStatusAction`/`BGStatusCheckAction`/`BGLeaveAction` via `WorldSession::HandleBattlefieldStatusOpcode`/`HandleBattleFieldPortOpcode`/`HandleLeaveBattlefieldOpcode` + `InBattleGroundQueue`/`InBattleGround`/`GetBattleGroundQueueTypeId` and `sServerFacade.BGTemplateId`) and `BattlegroundStrategy`/`BattleGroundTactics` (Vanilla WSG/AB/AV) remain present and manual-only (`runtime/RandomBotService` has zero BG queue code; `BotPacketAdapter` remains a generic packet bridge with no BG queue provider); pinned-core `BattleGroundMgr`/`BattleGroundQueue` (`src/game/Battlegrounds/BattleGroundMgr.*`) owns queue/invite/cancellation state and TortoiseBots has no generic module lifecycle hook for auto-fill. `RNDBOT` BG auto-queue remains deferred until the 5-player dungeon/LFT work and a proven type-agnostic, core-owned participant/invite/cancellation lifecycle on the world thread. Prohibited: direct queue mutation, owning a second queue/thread, donor `CheckBgQueueThread` copy, arena/vehicle/expansion BG behavior, and fake config (`RandomBotJoinBG`/`RandomBotAutoJoinBG`/`RandomBotBracketCount` absent from `ai/playerbot/aiplayerbot.conf.dist.in`). No code/config/data change is claimed.

## 16. New core seam test

Before adding another core seam, establish that:

1. the behavior cannot live entirely inside TortoiseBots;
2. no current generic hook/API exposes it;
3. the proposed seam is a real generic core concept, not a bot special case.

If the design would make PlayerBots-specific checks spread through normal
core gameplay code, redesign it.

## 17. Historical closure

F-03/F-27 closure and validation boundary are recorded in `PLAN.md` §6.1 and `PROVENANCE.md`; see `archive/PLAYERBOTS_AUDIT.md` for full evidence. This contract covers only the current host API.
