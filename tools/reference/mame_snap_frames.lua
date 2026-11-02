-- Copied into the Cyberbots repository from the XvSF repository, `tools/reference/mame_snap_frames.lua` at
-- commit `a1c82ba` (`ENV-003`). Notes above about MSHvSF or XvSF are their
-- history; for Cyberbots they are at most a HYPOTHESIS until re-validated.
-- MAME autoboot script: save snapshots at the frames in SNAP_FRAMES, then exit.
-- Copied unchanged from MSHvSF tools/reference/mame_snap_frames.lua at commit
-- 69c666c. It is game-independent.
-- Example: SNAP_FRAMES="1200 3000" mame mshvsfu -autoboot_script this.lua ...
local targets = {}
for f in string.gmatch(os.getenv("SNAP_FRAMES") or "1800", "%d+") do targets[tonumber(f)] = true end
local last = 0
for f in pairs(targets) do if f > last then last = f end end
local screen = manager.machine.screens[":screen"]
emu.register_frame_done(function()
  local n = screen:frame_number()
  if targets[n] then
    screen:snapshot(string.format("%s_f%05d.png", emu.romname(), n))
  end
  if n >= last then manager.machine:exit() end
end)
