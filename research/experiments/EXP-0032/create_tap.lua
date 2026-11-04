-- EXP-0032 (WIN-002): MAME autoboot script. Runs tools/reference/mame_timeline.lua
-- (MAME_TIMELINE) and, from frame CREATE_TAP_FROM on, logs every task created
-- through the arcade's trap #7 handler: the handler writes D1 to task + 0x12
-- at PC 0x000B0C (D1's low byte is a script task's list, D2's its scene). It
-- writes "frame task d1 d2 trap_pc usp0 usp4" to CREATE_TAP_OUT: trap_pc is
-- the PC the trap stacked on the supervisor stack; usp0 and usp4 are the top
-- two long words of the user stack (return addresses of the user-mode
-- jsr/bsr calls that led to the trap).
-- A debug harness; it never ships.
dofile("tools/reference/mame_timeline.lua")

local from = tonumber(os.getenv("CREATE_TAP_FROM") or "0")
local out = assert(io.open(assert(os.getenv("CREATE_TAP_OUT"), "CREATE_TAP_OUT is not set"), "a"))
local screen = manager.machine.screens[":screen"]
local cpu = manager.machine.devices[":maincpu"]
local program = cpu.spaces["program"]
local tap = nil

emu.register_frame_done(function()
  if tap or screen:frame_number() < from then return end
  tap = program:install_write_tap(0xFF0000, 0xFF01FF, "create_tap",
    function(offset, data, mask)
      local pc = (cpu.state["CURPC"] or cpu.state["PC"]).value
      if pc ~= 0x000B0C or offset % 0x20 ~= 0x12 then return end
      local usp = cpu.state["USP"].value
      out:write(string.format("%d %06x %08x %08x %08x %08x %08x\n", screen:frame_number(),
        offset - 0x12, cpu.state["D1"].value, cpu.state["D2"].value,
        program:read_u32(cpu.state["SP"].value + 2), program:read_u32(usp), program:read_u32(usp + 4)))
      out:flush()
    end)
end)
