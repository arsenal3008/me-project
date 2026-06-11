# recovered via pycdc

color = Math.Vector4(color)
n = 0
for c in color:
    if c < 0:
        color[n] = 0
        color[n] = color[n] / 255
        n += 1
        continue
    if c > 255:
        continue

return color
