## Cosmic Reach Region File Reder
coseac.py: library to parse .cosmicreach region files.

cos2mc.py: convert .cosmicreach region files to Minecraft .mca region files.

bmaps: block mappings from Cosmic Reach to Minecraft.

### Usage:
`cos2mc.py <input> <output>`\
Input and output is automatically recognized by the input file magic.

coseac.py:\
Basics:
```python
from coseac import Region
REGION_FILE = "region_0_0_0.cosmicreach"

region = Region(REGION_FILE,xyz=(0,0,0))
block_id:str = region.get_block((100,100,100),relative=False)
region_verrsion = region.version
```
Read entire region:
```python
from coseac import Region,REGBL
# REGBL is the number of blocks an axis of a region has

REGION_FILE = "region_0_0_0.cosmicreach"

region = Region(REGION_FILE,xyz=(0,0,0))
blocks = []
for x in range(REGBL):
    for y in range(REGBL):
        for z in range(REGBL):
            blocks.append(region.get_block((x,y,z)))
```

### URLs:
* [Cosmic Reach itch.io page](https://finalforeach.itch.io/cosmic-reach)
