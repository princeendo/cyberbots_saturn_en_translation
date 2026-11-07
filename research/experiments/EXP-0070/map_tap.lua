-- EXP-0070 (UI-002): MAME autoboot script. Runs tools/reference/mame_timeline.lua
-- (MAME_TIMELINE) and logs every block the scroll-map copier reads from the
-- shared map table 0x296542 (1 KB a block): when a read at a block's first
-- long comes from the copier's PC (MAP_TAP_PC), it writes "frame pc A6 list
-- index block dest" to MAP_TAP_OUT, where list = the long at A6 + 0x32, index
-- = D0 / 2 and dest = A0. A debug harness; it never ships.
dofile("tools/reference/mame_timeline.lua")

local out = assert(io.open(assert(os.getenv("MAP_TAP_OUT"), "MAP_TAP_OUT is not set"), "a"))
local copier = tonumber(assert(os.getenv("MAP_TAP_PC"), "MAP_TAP_PC is not set"), 16)
local screen = manager.machine.screens[":screen"]
local cpu = manager.machine.devices[":maincpu"]
local program = cpu.spaces["program"]
local base = 0x296542

tap = program:install_read_tap(0x296540, 0x2D6541, "map_tap",
  function(offset, data, mask)
    local pc = (cpu.state["CURPC"] or cpu.state["PC"]).value
    if pc ~= copier then return end
    if (offset - base) % 0x400 ~= 0 then return end
    local a6 = cpu.state["A6"].value
    local list = program:read_u32(a6 + 0x32)
    out:write(string.format("%d %06x %08x %08x %d %d %08x\n", screen:frame_number(), pc, a6, list,
      cpu.state["D0"].value // 2 % 0x10000, (offset - base) // 0x400, cpu.state["A0"].value))
    out:flush()
  end)
