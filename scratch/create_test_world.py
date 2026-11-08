import struct
import gzip
import os

TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11
TAG_LONG_ARRAY = 12

class NBTReader:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def read_byte(self):
        v = self.data[self.pos]
        self.pos += 1
        return v

    def read_short(self):
        v = struct.unpack_from('>h', self.data, self.pos)[0]
        self.pos += 2
        return v

    def read_int(self):
        v = struct.unpack_from('>i', self.data, self.pos)[0]
        self.pos += 4
        return v

    def read_long(self):
        v = struct.unpack_from('>q', self.data, self.pos)[0]
        self.pos += 8
        return v

    def read_float(self):
        v = struct.unpack_from('>f', self.data, self.pos)[0]
        self.pos += 4
        return v

    def read_double(self):
        v = struct.unpack_from('>d', self.data, self.pos)[0]
        self.pos += 8
        return v

    def read_string(self):
        length = self.read_short()
        s = self.data[self.pos:self.pos+length].decode('utf-8', errors='replace')
        self.pos += length
        return s

    def read_tag(self, tag_type):
        if tag_type == TAG_END:
            return None
        elif tag_type == TAG_BYTE:
            return self.read_byte()
        elif tag_type == TAG_SHORT:
            return self.read_short()
        elif tag_type == TAG_INT:
            return self.read_int()
        elif tag_type == TAG_LONG:
            return self.read_long()
        elif tag_type == TAG_FLOAT:
            return self.read_float()
        elif tag_type == TAG_DOUBLE:
            return self.read_double()
        elif tag_type == TAG_BYTE_ARRAY:
            length = self.read_int()
            v = self.data[self.pos:self.pos+length]
            self.pos += length
            return v
        elif tag_type == TAG_STRING:
            return self.read_string()
        elif tag_type == TAG_LIST:
            item_type = self.read_byte()
            length = self.read_int()
            return (item_type, [self.read_tag(item_type) for _ in range(length)])
        elif tag_type == TAG_COMPOUND:
            res = {}
            while True:
                t = self.read_byte()
                if t == TAG_END:
                    break
                name = self.read_string()
                res[name] = (t, self.read_tag(t))
            return res
        elif tag_type == TAG_INT_ARRAY:
            length = self.read_int()
            v = struct.unpack_from(f'>{length}i', self.data, self.pos)
            self.pos += length * 4
            return list(v)
        elif tag_type == TAG_LONG_ARRAY:
            length = self.read_int()
            v = struct.unpack_from(f'>{length}q', self.data, self.pos)
            self.pos += length * 8
            return list(v)
        raise ValueError(f"Unknown tag type {tag_type} at {self.pos}")

class NBTWriter:
    def __init__(self):
        self.buf = bytearray()

    def write_byte(self, v):
        self.buf.append(int(v) & 0xff)

    def write_short(self, v):
        self.buf.extend(struct.pack('>h', int(v)))

    def write_int(self, v):
        self.buf.extend(struct.pack('>i', int(v)))

    def write_long(self, v):
        self.buf.extend(struct.pack('>q', int(v)))

    def write_float(self, v):
        self.buf.extend(struct.pack('>f', float(v)))

    def write_double(self, v):
        self.buf.extend(struct.pack('>d', float(v)))

    def write_string(self, s):
        b = s.encode('utf-8')
        self.write_short(len(b))
        self.buf.extend(b)

    def write_tag(self, tag_type, val):
        if tag_type == TAG_END:
            return
        elif tag_type == TAG_BYTE:
            self.write_byte(val)
        elif tag_type == TAG_SHORT:
            self.write_short(val)
        elif tag_type == TAG_INT:
            self.write_int(val)
        elif tag_type == TAG_LONG:
            self.write_long(val)
        elif tag_type == TAG_FLOAT:
            self.write_float(val)
        elif tag_type == TAG_DOUBLE:
            self.write_double(val)
        elif tag_type == TAG_BYTE_ARRAY:
            self.write_int(len(val))
            self.buf.extend(val)
        elif tag_type == TAG_STRING:
            self.write_string(val)
        elif tag_type == TAG_LIST:
            item_type, items = val
            self.write_byte(item_type)
            self.write_int(len(items))
            for item in items:
                self.write_tag(item_type, item)
        elif tag_type == TAG_COMPOUND:
            for k, (t, v) in val.items():
                self.write_byte(t)
                self.write_string(k)
                self.write_tag(t, v)
            self.write_byte(TAG_END)
        elif tag_type == TAG_INT_ARRAY:
            self.write_int(len(val))
            for x in val:
                self.write_int(x)
        elif tag_type == TAG_LONG_ARRAY:
            self.write_int(len(val))
            for x in val:
                self.write_long(x)

def load_nbt(path):
    with gzip.open(path, 'rb') as f:
        raw = f.read()
    r = NBTReader(raw)
    root_type = r.read_byte()
    root_name = r.read_string()
    val = r.read_tag(root_type)
    return root_name, root_type, val

def save_nbt(path, root_name, root_type, val):
    w = NBTWriter()
    w.write_byte(root_type)
    w.write_string(root_name)
    w.write_tag(root_type, val)
    with gzip.open(path, 'wb') as f:
        f.write(w.buf)

print("NBT library ready.")
