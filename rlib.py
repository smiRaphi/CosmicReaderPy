import struct,os,io,sys
from types import NoneType
from typing import TypeVar

FileType = TypeVar('FileType',io.IOBase,io.BytesIO)
ENDS = '<>@!='
BYTEORDER = '<' if sys.byteorder == 'little' else '>'

class File:
    def __init__(self,f:str|bytes|FileType,mode:str=None,endian:str='<',encoding='utf-8'):
        if f == None: f = b''
        self.f:io.IOBase = None

        path = None
        if type(f) == str:
            if os.path.exists(f):
                mode = mode or 'rb'
                self.f = open(f,mode)
                path = os.path.abspath(f)
            else: f = f.encode()
        if type(f) == bytes:
            self.f = io.BytesIO(f)
            mode = 'w+b'
        elif self.f == None:
            self.f = f
            if hasattr(f,'path'): path = os.path.abspath(f.path)
            elif hasattr(f,'name'): path = os.path.abspath(f.name)
            if hasattr(f,'mode'): mode = f.mode
        self.mode = mode
        self.path = self.name = path
        self.closed = self.f.closed if hasattr(self.f,'closed') else False

        self.endian = self.__end(endian)
        self.encoding = encoding
    @classmethod
    def new0(cls,nulls=0xff): return cls(bytes(nulls))

    def close(self):
        if not self.closed:
            self.f.close()
            self.closed = True
    def __del__(self):
        try: self.close()
        except: pass

    def write(self,inp:bytes) -> int:
        self.__c
        return self.f.write(inp)
    def read(self,inp:int|None=None) -> None|bytes:
        self.__c
        return self.f.read(inp)
    def reads(self,inp:int=1):
        assert type(inp) == int
        return self.read(inp)
    def readall(self) -> bytes: return self.read()

    def tell(self): return self.f.tell()
    def seek(self,offset:int=0,whence:int=0): return self.f.seek(offset,whence)
    def step(self,offset:int=1): return self.seek(offset,1)

    def pack(self,fmt:str,*inp:int|float):
        if not fmt[0] in ENDS: fmt = self.endian + fmt
        return struct.pack(fmt,*inp)
    def unpack(self,fmt:str,inp:bytes) -> int|float|tuple[int|float]:
        if not fmt[0] in ENDS: fmt = self.endian + fmt
        if len(fmt) > 2: return self.unpackm(fmt,inp)
        return struct.unpack(fmt,*inp)[0]
    def unpackm(self,fmt:str,inp:bytes) -> tuple[int|float]:
        if not fmt[0] in ENDS: fmt = self.endian + fmt
        return struct.unpack(fmt,inp)
    def packa(self,inp:int,end=None):
        end = self.__end(end)
        tm = struct.pack(end + 'Q',inp)
        if end == '>': tm = tm.lstrip(b'\x00')
        elif end == '<': tm = tm.rstrip(b'\x00')
        return tm
    def unpacka(self,inp:bytes,end=None) -> int:
        end = self.__end(end)
        if end == '>': inp = inp.rjust(8,b'\x00')
        elif end == '<': inp = inp.ljust(8,b'\x00')
        tm = struct.unpack(end + 'Q',inp)[0]
        return tm

    def aread(self,fmt:str) -> tuple[int|float]:
        if not fmt[0] in ENDS: fmt = self.endian + fmt
        return struct.unpack(fmt,self.read(struct.calcsize(fmt)))
    def awrite(self,fmt:str,*inp:int|float):
        if not fmt[0] in ENDS: fmt = self.endian + fmt
        return self.write(self.pack(fmt,*inp))
    def writea(self,inp:bytes,end=None): return self.write(self.packa(inp,end))
    def reada(self,siz:int,end=None): return self.unpacka(self.read(siz),end)

    def writeS8(self,inp:int): return self.awrite('b',inp)
    def readS8(self) -> int: return self.aread('b')[0]
    def writeU8(self,inp:int): return self.awrite('B',inp)
    def readU8(self) -> int: return self.aread('B')[0]
    def writeS16(self,inp:int,end=None): return self.awrite(self.__end(end) + 'h',inp)
    def readS16(self,end=None) -> int: return self.aread(self.__end(end) + 'h')[0]
    def writeU16(self,inp:int,end=None): return self.awrite(self.__end(end) + 'H',inp)
    def readU16(self,end=None) -> int: return self.aread(self.__end(end) + 'H')[0]
    def writeU24(self,inp:int,end=None):
        end = self.__end(end)
        d = self.pack(end + 'I',inp)
        if end == '<':
            assert d[-1] == 0
            d = d[:-1]
        elif end == '>':
            assert d[0] == 0
            d = d[1:]
        return self.write(d)
    def readU24(self,end=None): return self.unpacka(self.read(3),end)
    def writeS32(self,inp:int,end=None): return self.awrite(self.__end(end) + 'i',inp)
    def readS32(self,end=None) -> int: return self.aread(self.__end(end) + 'i')[0]
    def writeU32(self,inp:int,end=None): return self.awrite(self.__end(end) + 'I',inp)
    def readU32(self,end=None) -> int: return self.aread(self.__end(end) + 'I')[0]
    def writeS64(self,inp:int,end=None): return self.awrite(self.__end(end) + 'q',inp)
    def readS64(self,end=None) -> int: return self.aread(self.__end(end) + 'q')[0]
    def writeU64(self,inp:int,end=None): return self.awrite(self.__end(end) + 'Q',inp)
    def readU64(self,end=None) -> int: return self.aread(self.__end(end) + 'Q')[0]

    def writeE6(self,inp:float,end=None): return self.awrite(self.__end(end) + 'e',inp)
    def readE6(self,end=None) -> float: return self.aread(self.__end(end) + 'e')[0]
    def writeF16(self,inp:float,end=None): return self.writeE6(inp,end)
    def readF16(self,end=None): return self.readE6(end)
    def writeFloat(self,inp:float,end=None): return self.awrite(self.__end(end) + 'f',inp)
    def readFloat(self,end=None) -> float: return self.aread(self.__end(end) + 'f')[0]
    def writeF32(self,inp:float,end=None): return self.writeFloat(inp,end)
    def readF32(self,end=None): return self.readFloat(end)
    def writeDouble(self,inp:float,end=None): return self.awrite(self.__end(end) + 'd',inp)
    def readDouble(self,end=None) -> float: return self.aread(self.__end(end) + 'd')[0]
    def writeF64(self,inp:float,end=None): return self.writeDouble(inp,end)
    def readF64(self,end=None): return self.readDouble(end)

    def writeBool(self,inp:bool): return self.awrite('?',inp)
    def readBool(self) -> bool: return self.aread('?')[0]
    def writeSTR(self,inp:str,enc:str=None): return self.write(inp.encode(enc or self.encoding))
    def readSTR(self,siz:int,enc:str=None): return self.read(siz).decode(enc or self.encoding)

    def writeSBYT(self,inp:bytes,fnc=writeU8,end=None):
        self.__c
        if type(fnc) == str:
            if fnc[:4] == 'read': fnc = globals()[fnc]
        return self.write(fnc(b'',len(inp),self.__end(end)) + inp)
    def readSBYT(self,fnc=readU8,end=None,inc=False) -> bytes:
        self.__c
        if type(fnc) == str:
            if fnc[:4] == 'read': fnc = globals()[fnc]
        cs = self.tell()
        ln = fnc(self.f,self.__end(end))
        if inc:
            cl = self.tell()-cs
            self.step(-4)
            ln += cl
        return self.read(ln)
    def writeSNUM(self,inp:int,end=None): return self.writeSBYT(self.packa(inp,end))
    def readSNUM(self,end=None): return self.unpacka(self.readSBYT(end),end)
    def writeSSTR(self,inp:str,enc:str=None,fnc=writeU8,end=None): return self.writeSBYT(inp.encode(enc or self.encoding),fnc,end)
    def readSSTR(self,enc:str=None,fnc=readU8,end=None): return self.readSBYT(fnc,end).decode(enc or self.encoding)

    def writeNibble(self,i1=0,i2=0):
        assert i1 < 16 and i2 < 16
        self.writeU8(i1 << 4 | i2)
    def readNibble(self):
        d = self.readU8()
        return d >> 4,d & 15
    def writeHalfNibble(self,i1=0,i2=0,i3=0,i4=0):
        assert i1 < 3 and i2 < 3 and i3 < 3 and i4 < 3
        self.writeU8(i1 << 6 | i2 << 4 | i3 << 2 | i4)
    def readHalfNibble(self):
        d = self.readU8()
        return d >> 6,d >> 4 & 3,d >> 2 & 3,d & 3

    def check(self,inp:bytes|str,error=False,errmsg:str=None):
        if type(inp) == str: inp = inp.encode()
        data = self.read(len(inp)) == inp
        if error: assert data,errmsg
        return data

    def __getitem__(self,inp:str|int):
        if type(inp) == int: return self.reada(inp)
        return self.aread(inp)
    @property
    def nempty(self):
        p = self.pos
        r = bool(self.read(1))
        self.seek(p)
        return r
    @property
    def pos(self): return self.tell()

    @property
    def __c(self): assert not self.closed,'file is closed'
    def __end(self,i=None) -> str:
        if isn(i): return self.endian or '<'
        if type(i) == str:
            assert i in '<>@!=','invalid endian'
            r = i
        elif type(i) == int:
            assert 0 <= i <= 4,'invalid endian'
            r = '<>@!='[i]
        else: r = '<' if i else '>'
        if r == '!': r = '>'
        elif r in '@=': r = BYTEORDER
        return r

FileType = TypeVar('FileType',io.IOBase,File)

def isn(i) -> bool: return type(i) == NoneType
def isnn(i) -> bool: return type(i) != NoneType
def _end(end):
    if type(end) == str:
        if end not in ENDS: raise Exception('invalid endian')
    else: end = ('>' if end else '<')
    return end

def unpacka(inp:bytes,end='<') -> int:
    end = _end(end)
    if end == '>': inp = inp.rjust(8,b'\x00')
    else: inp = inp.ljust(8,b'\x00')
    tm = struct.unpack(end + 'Q',inp)[0]
    return tm
def packa(inp:int,end='<') -> bytes:
    end = _end(end)
    tm = struct.pack(end + 'Q',inp)
    if end == '>': tm = tm.lstrip(b'\x00')
    else: tm = tm.rstrip(b'\x00')
    return tm

def write(fs,inp:bytes) -> bytes|None:
    if type(fs) == bytes: return fs + inp
    else: fs.write(inp)
def writea(fs,inp:bytes,end='<'):
    return write(fs,packa(inp,end))
def writeS8(fs,inp:int,end=None): return write(fs,struct.pack('b',inp))
def writeU8(fs,inp:int,end=None): return write(fs,struct.pack('B',inp))
def writeS16(fs,inp:int,end='<'): return write(fs,struct.pack(_end(end) + 'h',inp))
def writeU24(fs,inp:int,end='<') -> int:
    dat = struct.pack(_end(end) + 'I',inp)
    if end == '>': dat = dat[:-1]
    else: dat = dat[1:]
    return write(fs,dat)
def writeU16(fs,inp:int,end='<'): return write(fs,struct.pack(_end(end) + 'H',inp))
def writeS32(fs,inp:int,end='<'): return write(fs,struct.pack(_end(end) + 'i',inp))
def writeU32(fs,inp:int,end='<'): return write(fs,struct.pack(_end(end) + 'I',inp))
def writeS64(fs,inp:int,end='<'): return write(fs,struct.pack(_end(end) + 'q',inp))
def writeU64(fs,inp:int,end='<'): return write(fs,struct.pack(_end(end) + 'Q',inp))
def writeE6(fs,inp:float,end='<'): return write(fs,struct.pack(_end(end) + 'e',inp))
def writeFloat(fs,inp:float,end='<'): return write(fs,struct.pack(_end(end) + 'f',inp))
def writeDouble(fs,inp:float,end='<'): return write(fs,struct.pack(_end(end) + 'd',inp))
def writeBool(fs,inp:bool): return write(fs,(b'\x01' if bool(inp) else b'\x00'))
def writeString(fs,inp:str,enc:str='utf-8'): return write(fs,bytes(inp,enc))
def writeBools(fs,inp:list[bool]): return writeU8(fs,int(''.join(['1' if x else '0' for x in inp]).zfill(8),2))
def writeSNUM(fs,inp:int,end='<'):
	pd = packa(inp,end)
	return write(fs,writeU8(b'',len(pd)) + pd)
def writeSSTR(fs,inp:str,enc:str='utf-8',fnc=writeU8):
	pd = writeString(b'',inp)
	return write(fs,fnc(b'',len(pd)) + pd)
def writeSBYT(fs,inp:bytes,fnc=writeU8): return write(fs,fnc(b'',len(inp)) + inp)

def read(fs,siz=1) -> bytes:
    if type(fs) == bytes: out = fs[:siz]
    else: out = fs.read(siz)
    return out
def reada(fs,siz:int,end='<'):
    return unpacka(read(fs,siz),end)
def readS8(fs,end=None) -> int: return struct.unpack('b',read(fs,1))[0]
def readU8(fs,end=None) -> int: return struct.unpack('B',read(fs,1))[0]
def readS16(fs,end='<') -> int: return struct.unpack(_end(end) + 'h',read(fs,2))[0]
def readU16(fs,end='<') -> int: return struct.unpack(_end(end) + 'H',read(fs,2))[0]
def readU24(fs,end='<') -> int: return reada(fs,3,end)
def readS32(fs,end='<') -> int: return struct.unpack(_end(end) + 'i',read(fs,4))[0]
def readU32(fs,end='<') -> int: return struct.unpack(_end(end) + 'I',read(fs,4))[0]
def readS64(fs,end='<') -> int: return struct.unpack(_end(end) + 'q',read(fs,8))[0]
def readU64(fs,end='<') -> int: return struct.unpack(_end(end) + 'Q',read(fs,8))[0]
def readE6(fs,end='<') -> float: return struct.unpack(_end(end) + 'e',read(fs,2))[0]
def readFloat(fs,end='<') -> float: return struct.unpack(_end(end) + 'f',read(fs,4))[0]
def readDouble(fs,end='<') -> float: return struct.unpack(_end(end) + 'd',read(fs,8))[0]
def readBool(fs) -> bool: return bool(readU8(fs))
def readString(fs,siz:int,enc:str='utf-8'): return read(fs,siz).decode(enc)
def readBools(fs,cnt=8) -> list[bool]: return [x == '1' for x in bin(ord(read(fs)))[2:].zfill(8)][:cnt]
def readSNUM(fs,end='<'):
	ln = readU8(fs)
	return reada(fs,ln,end)
def readSSTR(fs,enc:str='utf-8',fnc=readU8):
	ln = fnc(fs)
	return readString(fs,ln,enc)
def readSBYT(fs,fnc=readU8): return read(fs,fnc(fs))
