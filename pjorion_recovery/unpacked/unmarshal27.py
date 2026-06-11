"""Minimal Python 2.7 marshal reader implemented in Python 3.
Parses a 2.7 .pyc into a nested structure of Code namedtuples.
"""
import struct, sys

class Code:
    def __init__(self, **kw):
        self.__dict__.update(kw)
    def __repr__(self):
        return "<Code %s argc=%d nlocals=%d names=%r varnames=%r consts=%d code=%dB>" % (
            self.name, self.argcount, self.nlocals, self.names, self.varnames,
            len(self.consts), len(self.code))

class Reader:
    def __init__(self, data):
        self.d = data
        self.i = 0
        self.refs = []
    def r(self, n):
        b = self.d[self.i:self.i+n]; self.i += n; return b
    def u8(self):
        v = self.d[self.i]; self.i += 1; return v
    def i32(self):
        v = struct.unpack('<i', self.r(4))[0]; return v
    def i64(self):
        return struct.unpack('<q', self.r(8))[0]
    def f64(self):
        return struct.unpack('<d', self.r(8))[0]

    def read_object(self):
        t = self.u8()
        c = chr(t & 0x7f)  # high bit = "ref this" flag in some versions; 2.7 uses 't'/'R' for interning
        flag = t & 0x80
        if c == '0': return None  # NULL
        if c == 'N': return None
        if c == 'F': return False
        if c == 'T': return True
        if c == 'S': return StopIteration
        if c == '.': return Ellipsis
        if c == 'i': return self.i32()
        if c == 'I': return self.i64()
        if c == 'f':
            n = self.u8(); return float(self.r(n))
        if c == 'g': return self.f64()
        if c == 'l':  # long
            n = self.i32()
            sign = 1
            if n < 0: sign = -1; n = -n
            val = 0
            for k in range(n):
                val |= self.u16() << (15*k)
            return sign*val
        if c == 's':  # string
            n = self.i32(); return self.r(n)
        if c == 't':  # interned string
            n = self.i32(); s = self.r(n); self.refs.append(s); return s
        if c == 'R':  # string ref
            idx = self.i32(); return self.refs[idx]
        if c == 'u':  # unicode
            n = self.i32(); return self.r(n).decode('utf-8','replace')
        if c == '(' or c == '[':  # tuple/list
            n = self.i32(); return [self.read_object() for _ in range(n)]
        if c == '{':  # dict
            d = {}
            while True:
                k = self.read_object()
                if k is None and self.d[self.i-1] == ord('0'):
                    break
                v = self.read_object()
                d[repr(k)] = v
            return d
        if c == 'c':  # code
            argcount = self.i32()
            nlocals = self.i32()
            stacksize = self.i32()
            flags = self.i32()
            code = self.read_object()
            consts = self.read_object()
            names = self.read_object()
            varnames = self.read_object()
            freevars = self.read_object()
            cellvars = self.read_object()
            filename = self.read_object()
            name = self.read_object()
            firstlineno = self.i32()
            lnotab = self.read_object()
            return Code(argcount=argcount, nlocals=nlocals, stacksize=stacksize,
                        flags=flags, code=code, consts=consts, names=names,
                        varnames=varnames, freevars=freevars, cellvars=cellvars,
                        filename=filename, name=name, firstlineno=firstlineno,
                        lnotab=lnotab)
        raise ValueError("Unknown marshal type %r at %d" % (c, self.i))
    def u16(self):
        v = struct.unpack('<H', self.r(2))[0]; return v

def load_pyc(path):
    data = open(path,'rb').read()
    rdr = Reader(data[8:])
    return rdr.read_object()

if __name__ == '__main__':
    top = load_pyc(sys.argv[1])
    def walk(c, depth=0):
        ind = '  '*depth
        nm = c.name.decode() if isinstance(c.name, bytes) else c.name
        print(ind, repr(nm), 'argc', c.argcount, 'nlocals', c.nlocals,
              'flags', hex(c.flags), 'codelen', len(c.code) if c.code else 0)
        for k in c.consts:
            if isinstance(k, Code):
                walk(k, depth+1)
    walk(top)
