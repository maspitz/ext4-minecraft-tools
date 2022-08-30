from _ext2_cffi import ffi, lib
"""Example usage and exploration area for ext2 CFFI."""

lib.initialize_ext2_error_table()

filsys_ptr = ffi.new('ext2_filsys *')
filename = "anvils.img"

## ext2fs_open(name, flags, superblock, block_size, manager, ret_fs)
errval = lib.ext2fs_open(filename.encode('ascii'), 0, 0, 0, lib.unix_io_manager, filsys_ptr)

if errval != 0:
    raise ValueError(ffi.string(lib.error_message(errval)).decode())
else:
    print(f"Opened file: {filename}")

filsys = filsys_ptr[0]
    
errval = lib.ext2fs_read_block_bitmap(filsys)

if errval != 0:
    raise ValueError(ffi.string(lib.error_message(errval)).decode())
else:
    print(f"Block bitmap read.")

# block bitmap
bm = filsys.block_map


# superblock
sb = filsys.super

print(f"inode count: {sb.s_inodes_count}")
print(f"block count: {sb.s_blocks_count}")
print(f"first inode: {sb.s_first_ino}")
print(f"{sb.s_free_blocks_count=}")
print(f"{sb.s_free_blocks_hi=}")
print(f"{lib.ext2fs_free_blocks_count(sb)=}")

used_cnt = 0
unused_cnt = 0
for blknum in range(sb.s_first_data_block, sb.s_first_data_block + sb.s_blocks_count - 1):
    blk_status = lib.ext2fs_test_block_bitmap(bm, blknum)
    if blk_status == 0:
        unused_cnt += 1
    else:
        used_cnt += 1

print(f"\t{used_cnt=}\t{unused_cnt=}")


# classifier code: line 253 of ext2hello.c
# what is sent to buf[] ..?  3rd arg of my_classifier
# which comes from io_channel_read_blk64(fs->io, blk64_t blk, 1, buf)
# where buf is allocated as: unsigned char buf[EXT2_MAX_BLOCK_SIZE].

buf = ffi.new("unsigned char[]", lib.CFFI_ext2_max_block_size)

def hexprint_blk64(buf: bytes, print_address_offset=0):
    MAXLEN = 1 << 14
    if len(buf) > MAXLEN:
        print(f"Warning: truncating hex {len(buf)} byte output to {MAXLEN} bytes.")
        buf = buf[0:MAXLEN]
    for idx in range(0, len(buf), 16):
        s1 = buf[idx:idx+8].hex(' ')
        s2 = buf[idx+8:idx+16].hex(' ')
        txt = "".join([chr(x) if 32 <= x <= 127 else "." for x in buf[idx:idx+16]])
        print(f"0x{print_address_offset+idx:06x}  {s1}  {s2}  {txt}")

