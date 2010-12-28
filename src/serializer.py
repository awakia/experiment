#! /usr/bin/env python
# -*- coding: utf-8 -*-

class Serializer:
    def __init__(self):
        self.enc = []
        self.dec = {}
    def decode(self, id, default=None):
        if id >= 0 and id < len(self.enc): return self.enc[id]
        else: return default
    def encode(self, item):
        if self.dec.has_key(item): return self.dec[item]
        else:
            id = len(self.enc)
            self.dec[item] = id
            self.enc.append(item)
            return id

if __name__ == '__main__':
    ser = Serializer()
    print ser.encode("abc")
    print ser.encode("ddd")
    print ser.encode("abc")
    print ser.encode("aabc")
    print ser.encode("ddd")
    print ser.decode(0)
    print ser.decode(1)
    print ser.decode(2)
    print ser.decode(3)
