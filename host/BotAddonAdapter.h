#pragma once

#include "ScriptObjects.h"

#include <string>

class Player;

namespace TortoiseBots {

// Native addon-message command seam. TortoiseBotsManager sends
// "TBM\t<verb> [args]" over a PARTY/RAID addon message once the core
// dispatches LANG_ADDON for the requester's group (core #476); this adapter
// consumes those payloads, runs them through the same native command layer as
// `.bot`, and answers over the addon channel so a UI click never reaches the
// chat frame.
class BotAddonAdapter final : public PlayerScript
{
public:
    BotAddonAdapter();

    // Returns true for payloads under the module prefix so the core neither
    // relays them to the group nor writes them to the chat log.
    bool OnAddonMessage(Player* from, std::string const& msg) override;
};

} // namespace TortoiseBots
