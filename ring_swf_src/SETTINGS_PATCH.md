# Settings-menu patch — expose ring (SWF) settings in ModsSettingsApi

Goal: configure **ring colour**, **horizontal/vertical correction**, **animation
speed** and **size** from the in-hangar settings window.

## Good news — most of it already exists

The MSA template (`_mrd_build_template`) **already** has working widgets for:

| Setting (requested)            | Existing widget / `varName`                                  |
|--------------------------------|--------------------------------------------------------------|
| Horizontal correction          | `Slider markerReload_x` (clip-space, column1)                |
| Vertical correction            | `Slider markerReload_y` (clip-space, column1)                |
| Animation speed                | `Slider markerRing_anim_speed` (column2)                     |
| Ring size                      | `Slider markerRing_size` (px, column2)                       |
| Ring on/off (ally / enemy)     | `CheckBox markerRingShow_ally` / `markerRingShow_enemy`      |

These already feed `mrl_mod` via the `on_change` handler, and after the
integration patch they drive the SWF directly:
`markerReload_x/y → comp.position`, `markerRing_size → movie.ringSize`,
`markerRing_anim_speed → movie.animSpeed`, colour → `movie.color`.

## The one missing piece — ring colour widgets

The ring colours `markerRingAllyClr` / `markerRingEnemyClr` / `markerRingSquadClr`
**already exist** in factory defaults *and* are already handled by `on_change`
(`CLR_VARS`) and by the reset defaults dict — but there are **no UI widgets** for
them, so they can't be changed from the menu yet (only the *timer-text* colours
`markerReloadAllyClr/...` have widgets).

### Add 3 `ColorChoice` widgets

In `_mrd_build_template`, in the **column2** ring block — right after the two
`markerRingShow_*` checkboxes and before the `markerRing_size` slider — insert:

```python
                 {'type': 'ColorChoice', 'varName': 'markerRingAllyClr',
                    'text': u'цвет кольца (союзники)',
                    'tooltip': _tt(u'цвет кольца союзников', u'Цвет анимации перезарядки над союзными танками.'),
                    'value': _mrd_clr_to_msa(getattr(m, 'markerRingAllyClr', (0, 255, 36, 255)))},
                 {'type': 'ColorChoice', 'varName': 'markerRingEnemyClr',
                    'text': u'цвет кольца (враги)',
                    'tooltip': _tt(u'цвет кольца врагов', u'Цвет анимации перезарядки над противниками.'),
                    'value': _mrd_clr_to_msa(getattr(m, 'markerRingEnemyClr', (255, 255, 0, 255)))},
                 {'type': 'ColorChoice', 'varName': 'markerRingSquadClr',
                    'text': u'цвет кольца (взвод)',
                    'tooltip': _tt(u'цвет кольца взвода', u'Цвет анимации перезарядки над танками взвода.'),
                    'value': _mrd_clr_to_msa(getattr(m, 'markerRingSquadClr', (255, 200, 0, 255)))},
```

That's the whole change for colour — no handler edits needed (the keys are already
in `CLR_VARS` and in the reset-defaults dict).

## Optional: apply changes to rings already on screen

`on_change` updates `mrl_mod` values; existing ring instances refresh on the next
reload/marker tick (and `updateMarkerPos` repositions every frame), so hangar
changes take effect on the next battle/reload. If you want **instant** live update
while in battle, after `on_change` finishes you can walk current rings:

```python
            for slot in mody.shootReload_list.values():
                rg = slot.get('ringGUI')
                if rg is None:
                    continue
                try:
                    rg.movie.ringSize = float(mody.markerRing_size)
                    _frames = float(getattr(mody, 'markerRing_frames', 39)) or 39.0
                    rg.movie.animSpeed = 1.0 / (max(0.001, float(mody.markerRing_anim_speed)) * _frames * 30.0)
                except Exception:
                    pass
```

(Colour per team is already re-applied on the team-recolour tick — see integration
patch edit #3.)

## Summary of what to change
1. Add the 3 `ColorChoice` widgets above (ring colour ally/enemy/squad).
2. Nothing else — offset/speed/size sliders already exist and now drive the SWF.
3. (Optional) the live-refresh loop for instant in-battle updates.
