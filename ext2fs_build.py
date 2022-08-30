from cffi import FFI
ffibuilder = FFI()

# WARNING: manipulation of filesystems may lead to loss of data, etc.
# Be sure you know what you are doing.

# Assuming libext2fs is installed (via compilation, or e2fsprogs-devel, etc...)

ffibuilder.set_source("_ext2_cffi",
                      """
                      #include <ext2fs/ext2fs.h>
                      #include <et/com_err.h>
                      int CFFI_ext2_max_block_size = EXT2_MAX_BLOCK_SIZE;
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
typedef int... __u64;
typedef int... __u32;
typedef int... __u16;
typedef int... __u8;
typedef int... __le32;
typedef int... __le16;
typedef int... __s16;

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



/*
 * Structure of the super block
 */
struct ext2_super_block {
/*000*/	__u32	s_inodes_count;		/* Inodes count */
	__u32	s_blocks_count;		/* Blocks count */
	__u32	s_r_blocks_count;	/* Reserved blocks count */
	__u32	s_free_blocks_count;	/* Free blocks count */
/*010*/	__u32	s_free_inodes_count;	/* Free inodes count */
	__u32	s_first_data_block;	/* First Data Block */
	__u32	s_log_block_size;	/* Block size */
	__u32	s_log_cluster_size;	/* Allocation cluster size */
/*020*/	__u32	s_blocks_per_group;	/* # Blocks per group */
	__u32	s_clusters_per_group;	/* # Fragments per group */
	__u32	s_inodes_per_group;	/* # Inodes per group */
	__u32	s_mtime;		/* Mount time */
/*030*/	__u32	s_wtime;		/* Write time */
	__u16	s_mnt_count;		/* Mount count */
	__s16	s_max_mnt_count;	/* Maximal mount count */
	__u16	s_magic;		/* Magic signature */
	__u16	s_state;		/* File system state */
	__u16	s_errors;		/* Behaviour when detecting errors */
	__u16	s_minor_rev_level;	/* minor revision level */
/*040*/	__u32	s_lastcheck;		/* time of last check */
	__u32	s_checkinterval;	/* max. time between checks */
	__u32	s_creator_os;		/* OS */
	__u32	s_rev_level;		/* Revision level */
/*050*/	__u16	s_def_resuid;		/* Default uid for reserved blocks */
	__u16	s_def_resgid;		/* Default gid for reserved blocks */
	/*
	 * These fields are for EXT2_DYNAMIC_REV superblocks only.
	 *
	 * Note: the difference between the compatible feature set and
	 * the incompatible feature set is that if there is a bit set
	 * in the incompatible feature set that the kernel doesn't
	 * know about, it should refuse to mount the filesystem.
	 *
	 * e2fsck's requirements are more strict; if it doesn't know
	 * about a feature in either the compatible or incompatible
	 * feature set, it must abort and not try to meddle with
	 * things it doesn't understand...
	 */
	__u32	s_first_ino;		/* First non-reserved inode */
	__u16   s_inode_size;		/* size of inode structure */
	__u16	s_block_group_nr;	/* block group # of this superblock */
	__u32	s_feature_compat;	/* compatible feature set */
/*060*/	__u32	s_feature_incompat;	/* incompatible feature set */
	__u32	s_feature_ro_compat;	/* readonly-compatible feature set */
/*068*/	__u8	s_uuid[16] ;		/* 128-bit uuid for volume */
/* assuming #define EXT2_LABEL_LEN 16 */
/*078*/	__u8	s_volume_name[16] ;	/* volume name, no NUL? */
/*088*/	__u8	s_last_mounted[64] ;	/* directory last mounted on, no NUL? */
/*0c8*/	__u32	s_algorithm_usage_bitmap; /* For compression */
	/*
	 * Performance hints.  Directory preallocation should only
	 * happen if the EXT2_FEATURE_COMPAT_DIR_PREALLOC flag is on.
	 */
	__u8	s_prealloc_blocks;	/* Nr of blocks to try to preallocate*/
	__u8	s_prealloc_dir_blocks;	/* Nr to preallocate for dirs */
	__u16	s_reserved_gdt_blocks;	/* Per group table for online growth */
	/*
	 * Journaling support valid if EXT2_FEATURE_COMPAT_HAS_JOURNAL set.
	 */
/*0d0*/	__u8	s_journal_uuid[16] ;	/* uuid of journal superblock */
/*0e0*/	__u32	s_journal_inum;		/* inode number of journal file */
	__u32	s_journal_dev;		/* device number of journal file */
	__u32	s_last_orphan;		/* start of list of inodes to delete */
/*0ec*/	__u32	s_hash_seed[4];		/* HTREE hash seed */
/*0fc*/	__u8	s_def_hash_version;	/* Default hash version to use */
	__u8	s_jnl_backup_type;	/* Default type of journal backup */
	__u16	s_desc_size;		/* Group desc. size: INCOMPAT_64BIT */
/*100*/	__u32	s_default_mount_opts;	/* default EXT2_MOUNT_* flags used */
	__u32	s_first_meta_bg;	/* First metablock group */
	__u32	s_mkfs_time;		/* When the filesystem was created */
/*10c*/	__u32	s_jnl_blocks[17];	/* Backup of the journal inode */
/*150*/	__u32	s_blocks_count_hi;	/* Blocks count high 32bits */
	__u32	s_r_blocks_count_hi;	/* Reserved blocks count high 32 bits*/
	__u32	s_free_blocks_hi;	/* Free blocks count */
	__u16	s_min_extra_isize;	/* All inodes have at least # bytes */
	__u16	s_want_extra_isize;	/* New inodes should reserve # bytes */
/*160*/	__u32	s_flags;		/* Miscellaneous flags */
	__u16	s_raid_stride;		/* RAID stride in blocks */
	__u16	s_mmp_update_interval;  /* # seconds to wait in MMP checking */
	__u64	s_mmp_block;		/* Block for multi-mount protection */
/*170*/	__u32	s_raid_stripe_width;	/* blocks on all data disks (N*stride)*/
	__u8	s_log_groups_per_flex;	/* FLEX_BG group size */
	__u8	s_checksum_type;	/* metadata checksum algorithm */
	__u8	s_encryption_level;	/* versioning level for encryption */
	__u8	s_reserved_pad;		/* Padding to next 32bits */
	__u64	s_kbytes_written;	/* nr of lifetime kilobytes written */
/*180*/	__u32	s_snapshot_inum;	/* Inode number of active snapshot */
	__u32	s_snapshot_id;		/* sequential ID of active snapshot */
	__u64	s_snapshot_r_blocks_count; /* active snapshot reserved blocks */
/*190*/	__u32	s_snapshot_list;	/* inode number of disk snapshot list */
/*#define EXT4_S_ERR_START ext4_offsetof(struct ext2_super_block, s_error_count)*/
	__u32	s_error_count;		/* number of fs errors */
	__u32	s_first_error_time;	/* first time an error happened */
	__u32	s_first_error_ino;	/* inode involved in first error */
/*1a0*/	__u64	s_first_error_block;	/* block involved in first error */
	__u8	s_first_error_func[32] ;	/* function where error hit, no NUL? */
/*1c8*/	__u32	s_first_error_line;	/* line number where error happened */
	__u32	s_last_error_time;	/* most recent time of an error */
/*1d0*/	__u32	s_last_error_ino;	/* inode involved in last error */
	__u32	s_last_error_line;	/* line number where error happened */
	__u64	s_last_error_block;	/* block involved of last error */
/*1e0*/	__u8	s_last_error_func[32] ;	/* function where error hit, no NUL? */
/*#define EXT4_S_ERR_END ext4_offsetof(struct ext2_super_block, s_mount_opts)*/
/*200*/	__u8	s_mount_opts[64] ;	/* default mount options, no NUL? */
/*240*/	__u32	s_usr_quota_inum;	/* inode number of user quota file */
	__u32	s_grp_quota_inum;	/* inode number of group quota file */
	__u32	s_overhead_clusters;	/* overhead blocks/clusters in fs */
/*24c*/	__u32	s_backup_bgs[2];	/* If sparse_super2 enabled */
/*254*/	__u8	s_encrypt_algos[4];	/* Encryption algorithms in use  */
/*258*/	__u8	s_encrypt_pw_salt[16];	/* Salt used for string2key algorithm */
/*268*/	__le32	s_lpf_ino;		/* Location of the lost+found inode */
	__le32  s_prj_quota_inum;	/* inode for tracking project quota */
/*270*/	__le32	s_checksum_seed;	/* crc32c(orig_uuid) if csum_seed set */
/*274*/	__u8	s_wtime_hi;
	__u8	s_mtime_hi;
	__u8	s_mkfs_time_hi;
	__u8	s_lastcheck_hi;
	__u8	s_first_error_time_hi;
	__u8	s_last_error_time_hi;
	__u8	s_first_error_errcode;
	__u8    s_last_error_errcode;
/*27c*/ __le16	s_encoding;		/* Filename charset encoding */
	__le16	s_encoding_flags;	/* Filename charset encoding flags */
	__le32	s_reserved[95];		/* Padding to the end of the block */
/*3fc*/	__u32	s_checksum;		/* crc32c(superblock) */
};




errcode_t ext2fs_open(const char *name, int flags, int superblock,
			     unsigned int block_size, io_manager manager,
			     ext2_filsys *ret_fs);

io_manager unix_io_manager;

char const *error_message(long);

blk64_t ext2fs_free_blocks_count(struct ext2_super_block *super);

errcode_t ext2fs_read_inode_bitmap(ext2_filsys fs);
errcode_t ext2fs_read_block_bitmap(ext2_filsys fs);

int ext2fs_test_block_bitmap(ext2fs_block_bitmap bitmap, blk_t block);
int ext2fs_test_inode_bitmap(ext2fs_inode_bitmap bitmap, ext2_ino_t inode);

/* the 'fast' variants have no bounds checking, etc. */
int ext2fs_fast_test_block_bitmap(ext2fs_block_bitmap bitmap, blk_t block);
int ext2fs_fast_test_inode_bitmap(ext2fs_inode_bitmap bitmap, ext2_ino_t inode);

errcode_t io_channel_read_blk64(io_channel channel,
				       unsigned long long block,
				       int count, void *data);

int CFFI_ext2_max_block_size;


""")


if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
    
