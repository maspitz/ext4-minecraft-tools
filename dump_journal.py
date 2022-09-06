import struct
from dataclasses import dataclass
from collections import namedtuple

from enum import IntFlag


# constants from <linux/jbd2.h>
JBD2_MAGIC_NUMBER = 0xc03b3998

JBD2_DESCRIPTOR_BLOCK	= 1
JBD2_COMMIT_BLOCK	= 2
JBD2_SUPERBLOCK_V1	= 3
JBD2_SUPERBLOCK_V2	= 4
JBD2_REVOKE_BLOCK	= 5

JBD2_CRC32_CHKSUM   = 1
JBD2_MD5_CHKSUM     = 2
JBD2_SHA1_CHKSUM    = 3
JBD2_CRC32C_CHKSUM  = 4

JBD2_FEATURE_COMPAT_CHECKSUM		= 0x00000001

class FeatureIncompat(IntFlag):
    REVOKE = 0x01         # has block revocation records
    _64BIT = 0x02         # can have 64-bit block numbers
    ASYNC_COMMIT = 0x04   # asynchronous commits of journal
    CSUM_V2 = 0x08        # v2 of checksum format
    CSUM_V3 = 0x10        # v3 of checksum format (fixed journal block tag size)
    FAST_COMMIT = 0x20

JBD2_KNOWN_INCOMPAT_FEATURES	= sum(FeatureIncompat.__members__.values())
JBD2_KNOWN_COMPAT_FEATURES = JBD2_FEATURE_COMPAT_CHECKSUM

SUPERBLOCK_FORMAT = (
    ">" # big-endian
    "I" # JBD2 magic number
    "I" # blocktype
    "I" # header_padding
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

Superblock = namedtuple("Superblock",
                        "magic_number,blocktype,header_padding,"
                        "blocksize,maxlen,first,sequence,start,errno,"
                        "feature_compat,feature_incompat,feature_ro_compat,uuid,"
                        "nr_users,dynsuper,max_transaction,max_trans_data,checksum_type,"
                        "padding2,padding,checksum,users")

HEADER_FORMAT = (
    ">" # big-endian
    "I" # JBD2 magic number
    "I" # blocktype
    "I" # sequence
)

Header = namedtuple("Header", "magic_number,blocktype,sequence")

DataBlock = namedtuple("DataBlock", "data")
DescriptorBlock = namedtuple("DescriptorBlock", "sequence,data")
CommitBlock = namedtuple("CommitBlock", "sequence,data")
RevokeBlock = namedtuple("RevokeBlock", "sequence,data")

class JBD2:
    """Class to read jbd2 journal transactions"""
    def __init__(self, filename: str):
        """Open and read the journal file."""
        with open(filename, mode='rb') as file:
            self.data = file.read()
        self.superblock = Superblock(*struct.unpack(SUPERBLOCK_FORMAT,self.data[:898]))
        if self.superblock.magic_number != JBD2_MAGIC_NUMBER:
            raise ValueError("Magic number not found.  Is this really JBD2 data?")
        if self.superblock.blocktype == 3:
            raise Warning("Superblock v1 detected.  May not work with this application.")
        elif self.superblock.blocktype != 4:
            raise ValueError("Superblock unknown version or absent.")
        if self.superblock.feature_incompat & ~JBD2_KNOWN_INCOMPAT_FEATURES:
            raise ValueError("Unrecognized incompat. features on journal.")
        if ~(self.superblock.feature_incompat & FeatureIncompat.CSUM_V3):
            raise ValueError("Unsupported journal because checksum v3 not present.")

    def get_block(self, block_num):
        """Read and return the specified block."""
        if block_num < 0 or block_num >= self.superblock.maxlen:
            raise IndexError(f"Block {block_num} out of range.")
        start_byte = self.superblock.blocksize * block_num
        stop_byte = start_byte + self.superblock.blocksize
        data = self.data[start_byte:stop_byte]
        hdr = Header(*struct.unpack(HEADER_FORMAT, data[:12]))
        if hdr.magic_number != JBD2_MAGIC_NUMBER:
            return DataBlock(data)
        if (hdr.blocktype == JBD2_SUPERBLOCK_V1 or
            hdr.blocktype == JBD2_SUPERBLOCK_V2):
            return Superblock(*struct.unpack(SUPERBLOCK_FORMAT, data[:898]))
        if hdr.blocktype == JBD2_DESCRIPTOR_BLOCK:
            return DescriptorBlock(hdr.sequence, data)
        if hdr.blocktype == JBD2_COMMIT_BLOCK:
            return CommitBlock(hdr.sequence, data)
        if hdr.blocktype == JBD2_REVOKE_BLOCK:
            return RevokeBlock(hdr.sequence, data)

        return hdr

BLOCKTAG3_FORMAT = (
    ">" # big-endian
    "I" # blocknr
    "I" # flags
    "I" # blocknr_high
    "I" # checksum
    
)

JBD2_FLAG_ESCAPE = 1    # the first 4 bytes of the data block should really be the JBD2 magic number
JBD2_FLAG_SAME_UUID = 2 # block has same uuid as previous block
JBD2_FLAG_DELETED = 4   # block is deleted by this transaction (?)
JBD2_FLAG_LAST_TAG = 8  # marks the last tag in the descriptor block

BlockTag3 = namedtuple("BlockTag3", "blocknr, flags, blocknr_high, checksum")




def print_descriptor_block(d: DescriptorBlock):
    """Print info about descriptor block."""
    print(f"Descriptor Block: Sequence {d.sequence}")
    idx = 12
    while idx < 1024:
        bt = BlockTag3(*struct.unpack(BLOCKTAG3_FORMAT, d.data[idx:idx+16]))
        print(bt)
        # FIXME - also handle 128 bit uuid (16 bytes)
        if bt.flags & JBD2_FLAG_LAST_TAG:
            break
        idx += 16
    


def print_descs(j):
    for i in range(j.superblock.maxlen):
        x = j.get_block(i)
        if type(x) == DescriptorBlock:
            print(f"Block {i}:")
            print_descriptor_block(x)
    
        

    
TEST_FILENAME = "journal-anvils-del.img"

j = JBD2(TEST_FILENAME)

incompat_feature_str = str(FeatureIncompat(j.superblock.feature_incompat))

print(f"Got incompat feature list: {incompat_feature_str}")

"""
If using csum3, then simply journal_block_tag3_t
