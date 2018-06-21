# encoding=utf-8

import math
from hashlib import md5


class RedisBitMap(object):
    _block_size = 1 << 31

    def __init__(self, redis, capacity=256, key='BLOOM_FILTER'):
        self._server = redis
        self._map_size = capacity * 1024 * 1024 * 8
        self._key = key

    def get_size(self):
        return self._map_size

    def _locate(self, position):
        block = math.ceil(position / self._block_size)
        key = self._key + '_BLOCK_' + str(block)
        offset = position % self._block_size
        return key, offset

    def get_bit(self, position):
        key, offset = self._locate(position)
        return self._server.getbit(key, offset)

    def set_bit(self, position):
        key, offset = self._locate(position)
        self._server.setbit(key, offset, 1)


class MemoryBitMap(object):

    def __init__(self, capacity=256):
        self._map_size = capacity * 1024 * 1024
        max_index, _ = self._locate(self._map_size)
        max_index += 1
        self._buffer = [0 for _ in range(max_index)]

    def get_size(self):
        return self._map_size

    @classmethod
    def _locate(cls, position):
        index = int(position / 31)
        offset = position % 31
        return index, offset

    def set_bit(self, position):
        index, offset = self._locate(position)
        block = self._buffer[index]
        self._buffer[index] = block | (1 << offset)

    def get_bit(self, position):
        index, offset = self._locate(position)
        return self._buffer[index] & (1 << offset) != 0


class BloomFilter(object):
    _hash_funcs = []

    def __init__(self, bit_map):
        self._map_size = bit_map.get_size()
        self._bit_map = bit_map
        for seed in [5, 7, 11, 13, 31, 37, 61]:
            self._hash_funcs.append(self._hash_gen(seed))

    def _hash_gen(self, seed):
        def _hash(value):
            ret = 0
            for i in range(len(value)):
                ret += seed * ret + ord(value[i])
            return (self._map_size - 1) & ret

        return _hash

    def marked(self, hash_str):
        if not hash_str:
            return False

        m5 = md5()
        m5.update(hash_str.encode("utf-8"))
        hash_str = m5.hexdigest()

        ret = True
        for f in self._hash_funcs:
            position = f(hash_str)
            ret = ret & self._bit_map.get_bit(position)
        return ret

    def mark(self, hash_str):
        m5 = md5()
        m5.update(hash_str.encode("utf-8"))
        hash_str = m5.hexdigest()

        for f in self._hash_funcs:
            position = f(hash_str)
            self._bit_map.set_bit(position)
