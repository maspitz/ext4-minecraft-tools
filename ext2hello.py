from _ext2_cffi import ffi, lib

lib.initialize_ext2_error_table()

filsys = ffi.new('ext2_filsys *')
filename = "anvils.img"

## ext2fs_open(name, flags, superblock, block_size, manager, ret_fs)
errval = lib.ext2fs_open(filename.encode('ascii'), 0, 0, 0, lib.unix_io_manager, filsys)

if errval != 0:
    raise ValueError(ffi.string(lib.error_message(errval)).decode())
else:
    print(f"Opened file: {filename}")
    
