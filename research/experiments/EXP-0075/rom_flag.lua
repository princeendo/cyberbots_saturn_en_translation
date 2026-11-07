-- EXP-0075 (TXT-011): set one byte of the main CPU's ROM data, then run the
-- standard timeline player (tools/reference/mame_timeline.lua, unchanged).
-- ROM_POKE="<cpu address hex>=<byte hex>": written into the ":maincpu"
-- region before the first frame. The region may hold 16-bit words in host
-- order, so the byte is written at the address, and if the program space
-- does not read it back, restored there and written at address XOR 1.
-- The program-space byte before and after is printed as the check.
local poke = os.getenv("ROM_POKE")
if poke and poke ~= "" then
  local a, v = poke:match("^(%x+)=(%x+)$")
  a, v = tonumber(a, 16), tonumber(v, 16)
  local region = manager.machine.memory.regions[":maincpu"]
  local space = manager.machine.devices[":maincpu"].spaces["program"]
  local before = space:read_u8(a)
  local off = a
  local old = region:read_u8(off)
  region:write_u8(off, v)
  if space:read_u8(a) ~= v then
    region:write_u8(off, old)
    off = a ~ 1
    region:write_u8(off, v)
  end
  print(string.format("ROM_POKE 0x%06X: program %02X -> %02X (region offset 0x%06X)",
    a, before, space:read_u8(a), off))
end
dofile("tools/reference/mame_timeline.lua")
