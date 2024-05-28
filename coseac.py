from rlib import File

CHUNKL = 16
REGL = 16
REGBL = REGL * CHUNKL

class Chunk:
    def __init__(self,data:bytes=None,xyz=(0,0,0)):
        self.d = File(data,endian='>')
        self.layers = []
        if data:
            self.version = self.d.readU32()
            self.xyz = (self.d.readU32(),self.d.readU32(),self.d.readU32())
            self.typ = self.d.readU8()
            if self.typ == 1: self.pallet = self.d.readSSTR(fnc='readU32')
            elif self.typ == 2:
                self.pallet = [self.d.readSSTR(fnc='readU32') for _ in range(self.d.readU32())]
                for _ in range(CHUNKL):
                    t = self.d.readU8()
                    if t == 1: self.layers.append(self.d.readU8())
                    elif t == 2: self.layers.append(self.d.readU32())
                    elif t == 3: self.layers.append(sum([list(self.d.readHalfNibble()) for _ in range(CHUNKL**2//4)],[]))
                    elif t == 4: self.layers.append(sum([list(self.d.readNibble()) for _ in range(CHUNKL**2//2)],[]))
                    elif t == 5: self.layers.append(list(self.d.read(CHUNKL**2))) # readU8 * CHUNKL
                    elif t == 6: self.layers.append([self.d.readU16() for _ in range(CHUNKL**2)])
                    else:
                        print('Chunk:',self.d.read())
                        raise Exception(f'Layer type {t} not implemented')
        else:
            self.version = 1
            self.xyz = xyz
            self.pallet = []
    def get_block(self,xyz:tuple[int]) -> str:
        assert xyz[0] < CHUNKL and xyz[1] < CHUNKL and xyz[2] < CHUNKL,"Coordinates out of bounds"
        if type(self.pallet) == str: return self.pallet
        try: l = self.layers[xyz[2]]
        except: return 'base:air[default]'
        if type(l) == int: ix = l
        else: ix = l[xyz[0] * CHUNKL + xyz[1]]
        return self.pallet[ix]

class Region:
    def __init__(self,f:str=None,xyz=(0,0,0)):
        self.chunks = []
        self.xyz = xyz
        if f:
            tf = File(f,"rb",'>')
            tf.check(b'\xff\xec\xce\xac',True,'Magic not found') # 0xFFECCEAC = FinalForEachCosmiCrEACh
            self.version = tf.readU32()
            self.compr = tf.readU32()
            self.chunkn = tf.readU32()
            chofs = [tf.readU32() for _ in range(self.chunkn)]
            for x in chofs:
                if x == 0xffffffff: continue
                tf.seek(x)
                self.chunks.append(Chunk(tf.readSBYT('readU32')))
            self.chunksxyz = {x.xyz:x for x in self.chunks}
        else:
            self.version = 1
            self.compr = 0
            self.chunkn = 0
    def get_block(self,xyz:tuple[int],relative=False) -> str:
        if not relative: xyz = (xyz[0] - self.xyz[0]*REGL,xyz[1] - self.xyz[1]*REGL,xyz[2] - self.xyz[2]*REGL)
        assert xyz[0] < REGBL and xyz[1] < REGBL and xyz[2] < REGBL,"Coordinates out of bounds"
        cxyz = (xyz[0]//REGL,xyz[1]//REGL,xyz[2]//REGL)
        assert cxyz in self.chunksxyz,f"Chunk {cxyz} isn't saved"
        return self.chunksxyz[cxyz].get_block((xyz[2]%REGL,xyz[0]%REGL,xyz[1]%REGL))

if __name__ == '__main__':
    from sys import argv
    r = Region('region_0_0_0.cosmicreach')
    print('Version:',r.version)
    print('Compression:',r.compr)
    print('Coords:',r.xyz)
    print('Chunk Number:',r.chunkn)
    print('Chunk Number (Actual):',len(r.chunks))

    while True:
        try:
            i = input(': ')
            exec(i)
        except KeyboardInterrupt: exit()
        except Exception as e: print(e)
