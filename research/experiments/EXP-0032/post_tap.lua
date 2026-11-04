-- EXP-0032 (WIN-002): MAME autoboot script. Runs tools/reference/mame_timeline.lua
-- (MAME_TIMELINE) and, from frame POST_TAP_FROM on, logs every write of a
-- message's first long word to the arcade's message queue (0xFF1234-0xFF1433,
-- written by the post routine 0x163E at PC 0x1646) with D1 and D2 (the
-- message) and the top two long words of the stack (the caller's return
-- address, and the one above it). Output lines: "frame d1 d2 ret0 ret4", to
-- POST_TAP_OUT.
-- A debug harness; it never ships.
dofile("tools/reference/mame_timeline.lua")

local from = tonumber(os.getenv("POST_TAP_FROM") or "0")
local out = assert(io.open(assert(os.getenv("POST_TAP_OUT"), "POST_TAP_OUT is not set"), "a"))
local screen = manager.machine.screens[":screen"]
local cpu = manager.machine.devices[":maincpu"]
local program = cpu.spaces["program"]
local tap = nil

emu.register_frame_done(function()
  if tap or screen:frame_number() < from then return end
  tap = program:install_write_tap(0xFF1234, 0xFF1433, "post_tap",
    function(offset, data, mask)
      local pc = (cpu.state["CURPC"] or cpu.state["PC"]).value
      if pc ~= 0x1646 or (offset - 0xFF1234) % 8 ~= 0 then return end
      local sp = cpu.state["SP"].value
      out:write(string.format("%d %08x %08x %08x %08x\n", screen:frame_number(),
        cpu.state["D1"].value, cpu.state["D2"].value, program:read_u32(sp), program:read_u32(sp + 4)))
      out:flush()
    end)
end)
