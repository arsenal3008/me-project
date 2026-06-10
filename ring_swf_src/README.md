# MOD_MRD reload ring — single parametric SWF

Replaces the **117 pre-rendered PNG frames** (`data/sprites/{green,red,squad}/1..39.png`)
with **one** self-animating ActionScript-3 SWF: `res/gui/flash/MOD_MRD/ring.swf`.

The SWF draws the same "comet" ring of dots procedurally, spins itself every frame,
and is fully parametric — size, colour and rotation speed are controlled at runtime,
so a single file covers ally / enemy / squad and any future colour.

![preview](preview_green.png)

## Runtime API (matches the existing `_create_swf_ring()` contract)

GUIFlash can drive the movie either by assigning members directly on `comp.movie.<name>`
**or** via `comp.movie.invoke('setX', value)`. Both are supported.

| Property (`comp.movie.X`) | Type   | Default   | Meaning                                  |
|---------------------------|--------|-----------|------------------------------------------|
| `color`                   | uint   | `0xFFFFFF`| RGB tint (`0xRRGGBB`)                     |
| `ringSize`                | Number | `80`      | diameter in px (set = component px size)  |
| `dotCount`                | int    | `60`      | number of dots around the circle         |
| `dotRadius`               | Number | `4`       | max dot radius in px                     |
| `progress`                | Number | `0.0`     | manual head phase 0..1 (optional)        |
| `animSpeed`               | Number | `0.012`   | auto-spin per frame, fraction of circle  |
| `tail`                    | Number | `0.78`    | comet tail length 0..1                    |
| `minAlpha`                | Number | `0.0`     | faint-tail alpha 0..1 (0 = clean gap)    |

Invoke callbacks: `ping()` → `"pong"`, `setColor(int)`, `setProgress(Number)`,
`setSize(Number)`, `setSpeed(Number)`.

The movie auto-rotates on `ENTER_FRAME`; you do **not** need a per-frame Python
callback like the old PNG animation did. Set `animSpeed = 0` if you want rotation
driven purely by `progress` from Python instead.

## How to wire it into the mod

`_create_swf_ring()` already exists in `mod_MRD.py` and produces exactly the
component this SWF expects — it is simply **not called yet**. The live path
(`createGUIReloading` → `animateReloadRing`) still cycles PNG textures.

Replace the PNG ring with the SWF ring in your source (`src/mod_MRD.py`):

### 1) In `createGUIReloading()` — swap the `ringGUI` block

```python
# OLD (PNG sprite ring):
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

# NEW (single self-animating SWF ring):
if 'ringGUI' not in mody.shootReload_list[id]:
    clr = _pick_ring_clr(id, isAlly)                       # (r,g,b,a) 0..255
    ring = _create_swf_ring(mody.markerRing_size, clr,
                            mody.markerReload_x, mody.markerReload_y)
    if ring is not None:
        # optional: drive spin speed from the existing config value
        try: ring.movie.animSpeed = float(mody.markerRing_anim_speed)
        except Exception: pass
        GUI.addRoot(ring)
        mody.shootReload_list[id]['ringGUI'] = ring
    # NOTE: no BigWorld.callback / animateReloadRing needed — the SWF spins itself.
```

### 2) `animateReloadRing()` becomes optional

With the SWF spinning itself you no longer need to flip PNG frames. You can:
* delete `animateReloadRing` and its callback scheduling, **or**
* keep it but only use it to recolour on team change, e.g.
  `slot['ringGUI'].movie.color = _rgba_to_hex(_pick_ring_clr(id, isAlly))`.

Make sure `removeMarker()` still destroys `ringGUI` (a `GUI.Flash` component) the
same way it did the old `GUI.Simple` — `GUI.delRoot(...)` works for both.

### 3) Delete the sprites (optional cleanup)

Once wired, the whole `res/scripts/client/gui/mods/MOD_MRD/data/sprites/` folder
(117 PNGs) can be removed from the `.wotmod`.

## Rebuilding the SWF from source

No Adobe tooling required — built with the open-source Apache Flex compiler:

```bash
mxmlc -load-config= \
      -external-library-path+=playerglobal.swc \
      -target-player=32.0 -swf-version=13 \
      -default-size 80 80 -default-frame-rate 30 \
      -o ring.swf Ring.as
```

Output: `CWS` (zlib) SWF, version 13, AVM2, document class `Ring`. Verified the
tag structure (`SymbolClass → Ring`, `DoABC`, `ExternalInterface.addCallback`).

> Not yet smoke-tested inside Scaleform/WoT from this environment (no Flash player
> here). All APIs used (Sprite/Graphics.drawCircle, ENTER_FRAME, ColorTransform-free
> tinting via beginFill, ExternalInterface) are Flash 9/10-era and supported by
> Scaleform GFx. Please load it in-game once to confirm.
