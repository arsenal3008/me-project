# Integration patch for `src/mod_MRD.py`

Apply these **4 edits** to your source, then recompile to `mod_MRD.pyc`.
This fixes all three issues from in-game testing:

* SWF spinning in the **top-left corner** → it was the auto-running test harness.
* **PNG frames still showing** → the live ring was never switched to the SWF.
* **Keyboard input broken** → an interactive Flash root was capturing input
  (also hardened on the SWF side — see note 5).

---

## 1. Remove the auto-running SWF test (fixes corner ring + keyboard)

At the very bottom of the module:

```python
# DELETE this line:
BigWorld.callback(3.0, _mrd_swf_test)
```

You can also delete both `_mrd_swf_test` definitions and the `_swf_test_state`
globals — they are pure debug scaffolding and no longer referenced.

---

## 2. Use the SWF ring instead of the PNG `GUI.Simple` (in `createGUIReloading`)

Replace this block:

```python
                    if 'ringGUI' not in mody.shootReload_list[id]:
                        ring = GUI.Simple('')
                        ring.materialFX = GUI.Simple.eMaterialFX.BLEND
                        ring.widthMode = GUI.Simple.eSizeMode.PIXEL
                        ring.heightMode = GUI.Simple.eSizeMode.PIXEL
                        ring.verticalPositionMode = GUI.Simple.ePositionMode.CLIP
                        ring.horizontalPositionMode = GUI.Simple.ePositionMode.CLIP
                        ring.size = (mody.markerRing_size, mody.markerRing_size)
                        ring.position = (mody.markerReload_x, mody.markerReload_y, 0.2)
                        ring.colour = _pick_ring_clr(id, isAlly)
                        ring.visible = True
                        GUI.addRoot(ring)
                        mody.shootReload_list[id]['ringGUI'] = ring
                        mody.shootReload_list[id]['ringFrame'] = 1
                        BigWorld.callback(mody.markerRing_anim_speed, (lambda : animateReloadRing(id)))
```

with:

```python
                    if 'ringGUI' not in mody.shootReload_list[id]:
                        ring = _create_swf_ring(mody.markerRing_size,
                                                _pick_ring_clr(id, isAlly),
                                                mody.markerReload_x, mody.markerReload_y)
                        if ring is not None:
                            # Map the existing "seconds-per-frame" speed slider to the SWF's
                            # per-frame rotation fraction, preserving the original cadence
                            # (markerRing_frames per full turn @ 30 fps). Smaller slider = faster.
                            try:
                                _frames = float(getattr(mody, 'markerRing_frames', 39)) or 39.0
                                _sec = max(0.001, float(mody.markerRing_anim_speed))
                                ring.movie.animSpeed = 1.0 / (_sec * _frames * 30.0)
                            except Exception:
                                pass
                            ring.visible = True
                            GUI.addRoot(ring)
                            mody.shootReload_list[id]['ringGUI'] = ring
                        # NB: no ringFrame / animateReloadRing — the SWF spins itself.
```

`updateMarkerPos` keeps working unchanged: it already sets `ringGUI.position`,
`.visible` and `.alpha` every tick, and `GUI.Flash` supports all three.

---

## 3. Recolour the SWF ring on team change

Find (≈ the marker-recolour block):

```python
                if slot.get('ringGUI') is not None:
                    try:
                        slot['ringGUI'].colour = _pick_ring_clr(id, isAlly)
                    except Exception:
                        pass
```

`GUI.Flash` has no `.colour`; tint via the movie instead:

```python
                if slot.get('ringGUI') is not None:
                    try:
                        slot['ringGUI'].movie.color = _rgba_to_hex(_pick_ring_clr(id, isAlly))
                    except Exception:
                        pass
```

---

## 4. Remove the second `animateReloadRing` scheduler (in `setnewReloadTime`)

There is a second place that schedules the PNG frame loop. Delete it:

```python
                # DELETE these two lines in setnewReloadTime():
                if not was_reloading:
                    BigWorld.callback(mody.markerRing_anim_speed, (lambda vid=id: animateReloadRing(vid)))
```

After this, `animateReloadRing` is never called (it cycled `.textureName`, which
`GUI.Flash` doesn't have). Leave the function body or delete it — it's dead.

---

## 5. Notes

* **Delete the sprites** once this works: the whole
  `res/scripts/client/gui/mods/MOD_MRD/data/sprites/` folder (117 PNGs) is unused.
* The shipped `ring.swf` is now **keyboard-safe**: the movie sets
  `mouseEnabled=false / mouseChildren=false / tabEnabled=false / tabChildren=false`
  and never requests focus, so it can't capture WASD/keys even as a GUI root.
  `_create_swf_ring()` already sets `comp.focus=False` / `comp.moveFocus=False`.
* The `.wotmod` is now packed as a **STORE (uncompressed) ZIP**.
* Runtime knobs on the movie: `color` (uint RGB), `ringSize` (px), `dotCount`,
  `dotRadius`, `progress` (0..1), `animSpeed` (auto-spin/frame), `tail`, `minAlpha`.
