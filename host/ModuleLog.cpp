#include "ModuleLog.h"

#include "Config/Config.h"

namespace TortoiseBots {

ModuleLog& ModuleLog::Instance()
{
    static ModuleLog instance;
    return instance;
}

void ModuleLog::ApplyConfig()
{
    int32 configured = sConfig.GetIntDefault("TortoiseBots.LogLevel",
        static_cast<int32>(ModuleLogLevel::Detail));

    if (configured < static_cast<int32>(ModuleLogLevel::Minimal))
        configured = static_cast<int32>(ModuleLogLevel::Minimal);
    else if (configured > static_cast<int32>(ModuleLogLevel::Debug))
        configured = static_cast<int32>(ModuleLogLevel::Debug);

    m_level.store(static_cast<uint8>(configured), std::memory_order_relaxed);
}

} // namespace TortoiseBots
