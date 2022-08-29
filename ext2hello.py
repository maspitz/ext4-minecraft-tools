from _ext2_cffi import ffi, lib
"""Example usage and exploration area for ext2 CFFI."""

lib.initialize_ext2_error_table()

filsys = ffi.new('ext2_filsys *')
filename = "anvils.img"

## ext2fs_open(name, flags, superblock, block_size, manager, ret_fs)
errval = lib.ext2fs_open(filename.encode('ascii'), 0, 0, 0, lib.unix_io_manager, filsys)

if errval != 0:
    raise ValueError(ffi.string(lib.error_message(errval)).decode())
else:
    print(f"Opened file: {filename}")

# superblock
sb = filsys[0].super

print(f"inode count: {sb.s_inodes_count}")
print(f"block count: {sb.s_blocks_count}")
print(f"first inode: {sb.s_first_ino}")
print(f"{sb.s_free_blocks_count=}")
print(f"{sb.s_free_blocks_hi=}")
print(f"{lib.ext2fs_free_blocks_count(sb)=}")
