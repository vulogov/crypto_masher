##
## This is an experimental psk block cipher
##
import os
import bitstring

class MasherError:
    def __init__(self, *args):
        pass

class SYSTEM_RANDOM:
    def randint(self, _min, _max):
        import random
        return random.randint(_min, _max)
    def block(self, size):
        return os.urandom(size)

class QUANTUM_RANDOM:
    def __init__(self):
        self.attempts = 10
    def cmd(self, _cmd, args, kw):
        c = 0
        while True:
            try:
                print 1,_cmd,args,kw
                return apply(_cmd, args, kw)
            except:
                c += 1
            if c > self.attempts:
                raise MasherError, "Can not get quantum random data"
            print c
    def randint(self, _min, _max):
        import quantumrandom
        return self.cmd(quantumrandom.randint, (), {"min":_min, "max":_max})
    def block(self, size):
        import quantumrandom
        return self.cmd(quantumrandom.binary, (), {"array_length":1, "block_size":size})

class RANDOM:
    def __init__(self, is_internal=False):
        if not is_internal:
            try:
                import quantumrandom
                self.r = QUANTUM_RANDOM()
            except ImportError:
                self.r = SYSTEM_RANDOM()
        else:
            self.r = SYSTEM_RANDOM()
    def randint(self, _min, _max):
        return self.r.randint(_min, _max)
    def block(self, size):
        return self.r.block(size)

class PSK:
    def __init__(self, is_internal=False):
        self.rnd = RANDOM(is_internal)
    def generate(self, size=6):
        out = []
        for i in range(size):
            out.append(self.rnd.randint(1,99))
        return out

def array2str(l):
    out = ""
    for c in l:
        out += chr(c)
    return out
class MASHER_BLOCK:
    def __init__(self, size, is_internal=False):
        self.size = size
        self.rnd = RANDOM(is_internal)
    def xor_data(self, buf, key, fun):
        out = []
        ix = 0
        for c in map(str, buf):
            if ix >= len(key):
                ix=0
            out.append(int(fun(c))^int(key[ix]))
            ix+=1
        return out
    def make_block(self, b):
        import struct
        if len(b)+8 > self.size:
            raise ValueError, "Size of the buffer is larger than the size of the block"
        nb = struct.pack("l", len(b))+b

        _tail = self.rnd.block(self.size-len(nb))
        nb = nb+_tail
        return nb

    def crypt(self, buf, psk):
        cb = self.xor_data(buf, psk, ord)
        cb = array2str(cb)
        pb = map(str, self.make_block(cb))
        mixer = map(str, self.rnd.block(self.size))
        nb = ""
        for i in pb:
            nb += i + mixer[0]
            mixer = mixer[1:]
        ## Now the mashing
        sb = bitstring.BitArray(bytes=nb)
        for k in psk:
            if k % 2 == 0:
                sb.rol(k)
            else:
                sb.ror(k)
        return sb.bytes
    def decrypt(self, data, psk):
        import struct
        sb = bitstring.BitArray(bytes=data)
        for k in psk:
            if k % 2 == 0:
                sb.ror(k)
            else:
                sb.rol(k)
        nb = sb.bytes
        nb = [nb[i:i+2] for i in range(0, len(nb), 2)]
        pb = ""
        for c in nb:
            pb += c[0]
        size = struct.unpack("l", pb[:8])[0]
        eb = pb[8:(size+8)]
        return array2str(self.xor_data(eb, psk, ord))
    def pretty_out(self, buf):
        p = [buf[i:i+5] for i in range(0, len(buf), 5)]
        for i in p:
            for j in i:
                print "%03d"%ord(j),
            print
        print



if __name__ == '__main__':
    psk = PSK(True)
    key = psk.generate(64)
    bad_key = psk.generate()
    print "PSK:",key
    msg = "Hello world!"
    print repr(msg)
    b = MASHER_BLOCK(20, True)
    out = b.crypt(msg,key)
    b.pretty_out(out)
    f = open("/tmp/crypto.txt", "w")
    f.write(out)
    f.close()
    print "Trying with bad key"
    try:
        out_bad = b.decrypt(out, bad_key)
        print repr(out_bad)
        assert (msg == out_bad),"Decryption failed"
    except AssertionError, _msg:
        print _msg
    print "Trying with good key"
    out = b.decrypt(out, key)
    print repr(out),repr(msg)
    assert (msg == out), "Decryption failed"




