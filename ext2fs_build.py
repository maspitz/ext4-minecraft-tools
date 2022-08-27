from cffi import FFI
ffibuilder = FFI()

# WARNING: manipulation of filesystems may lead to loss of data, etc.
# Be sure you know what you are doing.

# Assuming libext2fs is installed (via compilation, or e2fsprogs-devel, etc...)

ffibuilder.set_source("_ext2_cffi",
                      """
                      #include <ext2fs/ext2fs.h>
                      #include <et/com_err.h>
                      """,
                      libraries=['ext2fs'])

ffibuilder.cdef("""
void initialize_ext2_error_table(void);
typedef int... errcode_t;
typedef struct struct_io_manager *io_manager;
typedef struct struct_io_channel *io_channel;
typedef struct struct_io_stats *io_stats;
struct struct_io_channel {
	errcode_t	magic;
	io_manager	manager;
	char		*name;
	int		block_size;
	errcode_t	(*read_error)(io_channel channel,
				      unsigned long block,
				      int count,
				      void *data,
				      size_t size,
				      int actual_bytes_read,
				      errcode_t	error);
	errcode_t	(*write_error)(io_channel channel,
				       unsigned long block,
				       int count,
				       const void *data,
				       size_t size,
				       int actual_bytes_written,
				       errcode_t error);
	int		refcount;
	int		flags;
	long		reserved[14];
	void		*private_data;
	void		*app_data;
	int		align;
};

struct struct_io_stats {
	int			num_fields;
	int			reserved;
	unsigned long long	bytes_read;
	unsigned long long	bytes_written;
};
struct struct_io_manager {
	errcode_t magic;
	const char *name;
	errcode_t (*open)(const char *name, int flags, io_channel *channel);
	errcode_t (*close)(io_channel channel);
	errcode_t (*set_blksize)(io_channel channel, int blksize);
	errcode_t (*read_blk)(io_channel channel, unsigned long block,
			      int count, void *data);
	errcode_t (*write_blk)(io_channel channel, unsigned long block,
			       int count, const void *data);
	errcode_t (*flush)(io_channel channel);
	errcode_t (*write_byte)(io_channel channel, unsigned long offset,
				int count, const void *data);
	errcode_t (*set_option)(io_channel channel, const char *option,
				const char *arg);
	errcode_t (*get_stats)(io_channel channel, io_stats *io_stats);
	errcode_t (*read_blk64)(io_channel channel, unsigned long long block,
					int count, void *data);
	errcode_t (*write_blk64)(io_channel channel, unsigned long long block,
					int count, const void *data);
	errcode_t (*discard)(io_channel channel, unsigned long long block,
			     unsigned long long count);
	errcode_t (*cache_readahead)(io_channel channel,
				     unsigned long long block,
				     unsigned long long count);
	errcode_t (*zeroout)(io_channel channel, unsigned long long block,
			     unsigned long long count);
	long	reserved[14];
};


typedef int...		ext2_ino_t;
typedef int...		blk_t;
typedef int...		blk64_t;
typedef int...		dgrp_t;
typedef int...		ext2_off_t;
typedef int...		ext2_off64_t;
typedef int...		e2_blkcnt_t;
typedef int...		ext2_dirhash_t;
typedef int...          time_t;
typedef int...          __u32;
typedef int...          __u16;

typedef struct struct_ext2_filsys *ext2_filsys;

struct ext2fs_struct_generic_bitmap_base {
	errcode_t		magic;
	ext2_filsys 		fs;
};


typedef struct ext2fs_struct_generic_bitmap_base *ext2fs_generic_bitmap;
typedef struct ext2fs_struct_generic_bitmap_base *ext2fs_inode_bitmap;
typedef struct ext2fs_struct_generic_bitmap_base *ext2fs_block_bitmap;

typedef struct ext2_struct_u32_list *ext2_badblocks_list;

typedef struct ext2_struct_dblist *ext2_dblist;


struct struct_ext2_filsys {
	errcode_t			magic;
	io_channel			io;
	int				flags;
	char *				device_name;
	struct ext2_super_block	* 	super;
	unsigned int			blocksize;
	int				fragsize;
	dgrp_t				group_desc_count;
	unsigned long			desc_blocks;
	struct opaque_ext2_group_desc *	group_desc;
	unsigned int			inode_blocks_per_group;
	ext2fs_inode_bitmap		inode_map;
	ext2fs_block_bitmap		block_map;
	/* XXX FIXME-64: not 64-bit safe, but not used? */
	errcode_t (*get_blocks)(ext2_filsys fs, ext2_ino_t ino, blk_t *blocks);
	errcode_t (*check_directory)(ext2_filsys fs, ext2_ino_t ino);
	errcode_t (*write_bitmaps)(ext2_filsys fs);
	errcode_t (*read_inode)(ext2_filsys fs, ext2_ino_t ino,
				struct ext2_inode *inode);
	errcode_t (*write_inode)(ext2_filsys fs, ext2_ino_t ino,
				struct ext2_inode *inode);
	ext2_badblocks_list		badblocks;
	ext2_dblist			dblist;
	__u32				stride;	/* for mke2fs */
	struct ext2_super_block *	orig_super;
	struct ext2_image_hdr *		image_header;
	__u32				umask;
	time_t				now;
	int				cluster_ratio_bits;
	__u16				default_bitmap_type;
	__u16				pad;
	/*
	 * Reserved for future expansion
	 */
	__u32				reserved[5];

	/*
	 * Reserved for the use of the calling application.
	 */
	void *				priv_data;

	/*
	 * Inode cache
	 */
	struct ext2_inode_cache		*icache;
	io_channel			image_io;

	/*
	 * More callback functions
	 */
	errcode_t (*get_alloc_block)(ext2_filsys fs, blk64_t goal,
				     blk64_t *ret);
	errcode_t (*get_alloc_block2)(ext2_filsys fs, blk64_t goal,
				      blk64_t *ret, struct blk_alloc_ctx *ctx);
	void (*block_alloc_stats)(ext2_filsys fs, blk64_t blk, int inuse);

	/*
	 * Buffers for Multiple mount protection(MMP) block.
	 */
	void *mmp_buf;
	void *mmp_cmp;
	int mmp_fd;

	/*
	 * Time at which e2fsck last updated the MMP block.
	 */
	long mmp_last_written;

	/* progress operation functions */
	struct ext2fs_progress_ops *progress_ops;

	/* Precomputed FS UUID checksum for seeding other checksums */
	__u32 csum_seed;

	io_channel			journal_io;
	char				*journal_name;

	/* New block range allocation hooks */
	errcode_t (*new_range)(ext2_filsys fs, int flags, blk64_t goal,
			       blk64_t len, blk64_t *pblk, blk64_t *plen);
	void (*block_alloc_stats_range)(ext2_filsys fs, blk64_t blk, blk_t num,
					int inuse);

	/* hashmap for SHA of data blocks */
	struct ext2fs_hashmap* block_sha_map;

	const struct ext2fs_nls_table *encoding;
};


errcode_t ext2fs_open(const char *name, int flags, int superblock,
			     unsigned int block_size, io_manager manager,
			     ext2_filsys *ret_fs);
""")


if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
    
