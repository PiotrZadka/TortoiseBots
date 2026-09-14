#include "BotAddonAdapter.h"

#include "../commands/BotCommands.h"
#include "Chat.h"
#include "ModuleLog.h"
#include "Player.h"
#include "WorldSession.h"

#include <string>

namespace TortoiseBots {
namespace {

// Prefix owned by this module. The payload keeps the chat grammar, so one
// parser serves both transports: the chat path sends ".bot <verb> [args]" and
// the addon path sends "<verb> [args]" behind this prefix. The core writes an
// addon payload as "<prefix>\t<message>".
char const* const AddonPrefix = "TBM";

// Reply sink for the addon transport. The command layer answers through
// ChatHandler, so overriding the one virtual sender redirects every reply -
// human text and the structured TBM: protocol lines alike - to the requester's
// addon channel without touching a single command handler.
class AddonReplyHandler final : public ChatHandler
{
public:
    AddonReplyHandler(Player* requester, char const* prefix)
        : ChatHandler(requester), m_requester(requester), m_prefix(prefix)
    {
    }

    void SendSysMessage(char const* str) override
    {
        if (!str || !m_requester || !m_requester->GetSession())
        {
            ChatHandler::SendSysMessage(str);
            return;
        }

        // The base class emits one chat line per newline-delimited segment.
        std::string const text(str);
        size_t start = 0;
        while (start < text.size())
        {
            size_t const end = text.find('\n', start);
            std::string const line = text.substr(start, end == std::string::npos ? std::string::npos : end - start);
            if (!line.empty())
                m_requester->SendAddonMessage(m_prefix, line);
            if (end == std::string::npos)
                break;
            start = end + 1;
        }
    }

private:
    Player* m_requester;
    char const* m_prefix;
};

} // namespace

BotAddonAdapter::BotAddonAdapter()
    : PlayerScript("tortoisebots_addon", { PLAYERHOOK_ON_ADDON_MESSAGE })
{
}

bool BotAddonAdapter::OnAddonMessage(Player* from, std::string const& msg)
{
    std::string const prefix = std::string(AddonPrefix) + "\t";
    if (msg.compare(0, prefix.size(), prefix) != 0)
        return false;

    // Payloads under the module prefix are ours even when they turn out to be
    // unusable: consuming them keeps the group chat clean and the protocol
    // single-writer.
    if (!from || !from->GetSession())
        return true;

    std::string const payload = msg.substr(prefix.size());
    TB_LOG_DEBUG("TortoiseBots: addon command from %s: %s", from->GetName(), payload.c_str());

    // One command entry point for both transports: authorization, grammar and
    // replies stay identical to `.bot`.
    AddonReplyHandler handler(from, AddonPrefix);
    BotCommands::HandleChatCommand(&handler, payload.c_str());
    return true;
}

} // namespace TortoiseBots
