#pragma once
//
// ModuleLog — verbosity control for the native module layer (host/ and
// runtime/). The core's own LogLevel governs engine output; this governs
// the module's, so a server can trace bot lifecycle without turning on
// engine-wide debug output, and vice versa.
//
// Set TortoiseBots.LogLevel in tortoise_bots.conf:
//   0 minimal  errors only
//   1 basic    one-off startup, shutdown and diagnostic results
//   2 detail   per-bot state transitions (default)
//   3 debug    per-tick and per-packet traces
//
// Errors keep calling sLog.outError directly and are never gated.
//
// The macros expand to sLog at the call site, so a translation unit that
// routes sLog through BotLog (see playerbot.h) keeps writing where it did
// before; only the decision to write at all is added.
//

#include "Common.h"
#include "Log.h"

#include <atomic>

namespace TortoiseBots {

enum class ModuleLogLevel : uint8
{
    Minimal = 0,
    Basic   = 1,
    Detail  = 2,
    Debug   = 3,
};

class ModuleLog
{
public:
    static ModuleLog& Instance();

    // Reads TortoiseBots.LogLevel. Called from BotHostAdapter on startup and
    // again after every config load, so `.reload config` takes effect without
    // a restart.
    void ApplyConfig();

    bool HasLevel(ModuleLogLevel level) const
    {
        return static_cast<uint8>(level) <= m_level.load(std::memory_order_relaxed);
    }

private:
    std::atomic<uint8> m_level{ static_cast<uint8>(ModuleLogLevel::Detail) };
};

} // namespace TortoiseBots

// outBasic/outDetail/outDebug test the core's own LogLevel internally, which
// would make module output depend on two unrelated settings. These route to
// outString so TortoiseBots.LogLevel is the only gate.
#define TB_LOG_BASIC(...)                                                                          \
    do {                                                                                           \
        if (TortoiseBots::ModuleLog::Instance().HasLevel(TortoiseBots::ModuleLogLevel::Basic))      \
            sLog.outString(__VA_ARGS__);                                                           \
    } while (0)

#define TB_LOG_DETAIL(...)                                                                         \
    do {                                                                                           \
        if (TortoiseBots::ModuleLog::Instance().HasLevel(TortoiseBots::ModuleLogLevel::Detail))     \
            sLog.outString(__VA_ARGS__);                                                           \
    } while (0)

#define TB_LOG_DEBUG(...)                                                                          \
    do {                                                                                           \
        if (TortoiseBots::ModuleLog::Instance().HasLevel(TortoiseBots::ModuleLogLevel::Debug))      \
            sLog.outString(__VA_ARGS__);                                                           \
    } while (0)
