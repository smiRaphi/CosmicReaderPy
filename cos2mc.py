import json,os,anvil
from tqdm import tqdm

from anvil import Region as mcRegion,Block
from coseac import Region as csRegion,REGBL as csREGBL,ChunkNotSaved

def load_bmap(i) -> dict:
    if type(i) == dict: return i
    if os.path.exists(i): return json.load(open(i,encoding='utf-8'))
    elif os.path.exists('bmaps/' + i + '.json'): return json.load(open('bmaps/' + i + '.json',encoding='utf-8'))
    raise Exception('block map not found')

def cos2mc(i:str,o:str,block_map:dict|str='default',take_xy=True):
    bm = load_bmap(block_map)
    bm = {x:Block.from_name(bm[x]) for x in bm}

    cs = csRegion(i)
    if take_xy: xy = cs.xyz[:2]
    else: xy = (0,0)
    mc = anvil.EmptyRegion(*xy)

    tq = tqdm(total=csREGBL**3,unit_scale=True)
    for x in range(csREGBL):
        for y in range(csREGBL):
            for z in range(csREGBL):
                try: b = cs.get_block((x,y,z)).replace('[default]','')
                except ChunkNotSaved: b = 'base:air'
                if not b in bm:
                    print('WARNING: unknown block:',b)
                    b = 'base:debug'
                mc.set_block(bm[b],x,y,z)
                tq.update()
    mc.save(o)
def mc2cos(i:str,o:str,block_map:dict|str='default',take_xy=True):
    bm = load_bmap(block_map)

    mc = mcRegion.from_file(i)
    if take_xy: xy = (mc.x,mc.y)
    else: xy = (0,0)
    cs = csRegion(x=xy[0],y=xy[1])

if __name__ == '__main__':
    from sys import argv

    i,o = argv[1:]
    cs = open(i,'rb').read(4) == b'\xff\xec\xce\xac'

    if cs: cos2mc(i,o)
    else: mc2cos(i,o)
