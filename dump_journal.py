import struct
from dataclasses import dataclass
from collections import namedtuple

filename = "journal-anvils.img"

with open(filename, mode='rb') as file:
    data = file.read()

JBD2_HEADER = b'\xc0;9\x98\x00\x00\x00\x04\x00\x00\x00\x00'
s_header = data[0:12]

if s_header != JBD2_HEADER:
    raise ValueError("JBD2 header not found.  (Is this really a journal file?)")

def jbd2_superblock_v1(data):
    JBD2_SB_V1 = namedtuple("JBD2_SB_V1",
                            "header,blocksize,maxlen,first,sequence,start,errno")
    return JBD2_SB_V1(
        *struct.unpack(">12sIIIIII",data[:0x24]))

@dataclass
class J_Superblock:
    header: bytes
    blocksize: int
    maxlen: int
    first: int
    sequence: int
    start: int
    errno: int
    feature_compat: int
    feature_incompat: int
    feature_ro_compat: int
    uuid: tuple
    nr_users: int
    dynsuper: int
    max_transaction: int
    max_trans_data: int
    checksum_type: int
    padding2: tuple
    padding: tuple
    checksum: int
    users: tuple

def get_j_superblock(data: bytes):
    SUPERBLOCK_FORMAT = (
        ">" # big-endian
        "12s" # jbd2 12-byte header
        "I" # blocksize
        "I" # maxlen
        "I" # first
        "I" # sequence
        "I" # start
        "I" # errno
        "I" # feature_compat
        "I" # feature_incompat
        "I" # feature_ro_compat
        "16s" # uuid
        "I" # nr_users
        "I" # dynsuper
        "I" # max_transaction
        "I" # max_trans_data
        "B" # checksum_type
        "3s" # padding2
        "42s" # padding
        "I" # checksum
        "768s" # users
    )
    return J_Superblock(*struct.unpack(SUPERBLOCK_FORMAT,data[:898]))
