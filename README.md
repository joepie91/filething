# filething

Filesystem operations are one of those things in the Python standard library that just kind of suck.

`filething` is a thin light-weight wrapper library, to make filesystem operations in Python suck less. It's primarily meant for read-only stuff, and doesn't do anything to set file attributes and so on.

## License

[WTFPL](http://wtfpl.net/) or [CC0](https://creativecommons.org/publicdomain/zero/1.0/), your choice.

## Platforms

Theoretically cross-platform. Then again, Windows will probably be Windows and thus it may break there. I have no idea, I don't use Windows. All code is pure Python, anyway.

## Installation

`pip install filething`

Done. You'll need `pip`, of course.

## Usage

First of all, import `filething`.

```python
import filething
```

Then there's a bunch of stuff you can do. To start working with a directory or file, create a `Directory` or `File` object respectively.

To create a new `Directory` object:

```python
some_dir = filething.Directory("/path/to/directory")
```

To create a new `File` object:

```python
some_file = filething.File("/path/to/file")
```

Entering a non-existent (or inaccessible) path will result in a `filething.FilesystemException` being raised.

### Directory and File objects

The `Directory` and `File` classes have some things in common.

#### Attributes

The following attributes are automatically set on both `Directory` and `File` objects:

* `path`: The path of the file or directory.
* `name`: The name of the file or directory. This is generally the part after the last slash.
* `is_symlink`: Boolean. Whether the file/directory is a symlink or not.

#### Directory/File information

To learn more about a directory or file, you can use the `stat` or `symlink_stat` methods.

`stat` will give you the metadata for a file or directory, resolving a symlink if necessary. `symlink_stat` only applies to symbolic links, and gives you metadata about the symlink itself.

Trying to use `symlink_stat` on something that isn't a symlink, will raise a `filething.FilesystemException`. The `symlink_stat` function returns data in the same format as `stat`. The below applies to both.

```python
metadata = some_file.stat()
```

By default, the `stat` data will be returned as a custom `Attributes` object, with more human-meaningful names than what Python provides. The below is a list of available attributes, with a description (and their original name in `os.stat` in parentheses). I'll assume that the metadata is stored in a `metadata` variable, as above.

As with Python's `os.stat`, the exact meaning and accuracy of `lastmodified`, `lastaccessed` and `ctime` differ across platforms and filesystems.

Cross-platform (more-or-less):

* **metadata.size** (*st_size*): size of file, in bytes
* **metadata.lastaccessed** (*st_atime*): time of most recent access
* **metadata.lastmodified** (*st_mtime*): time of most recent content modification
* **metadata.uid** (*st_uid*): user id of owner
* **metadata.gid** (*st_gid*): group id of owner

* **metadata.mode** (*st_mode*): protection bits
* **metadata.inode** (*st_ino*): inode number
* **metadata.device** (*st_dev*): device
* **metadata.links** (*st_nlink*): number of hard links
* **metadata.ctime** (*st_ctime*): platform dependent; time of most recent metadata change on Unix, or the time of creation on Windows

On some UNIX-like (eg. Linux):

* **metadata.blockcount** (*st_blocks*): number of 512-byte blocks allocated for file
* **metadata.blocksize** (*st_blksize*): filesystem blocksize for efficient file system I/O
* **metadata.devicetype** (*st_rdev*): type of device if an inode device
* **metadata.userflags** (*st_flags*): user defined flags for file

On some other UNIX-like (eg. FreeBSD):

* **metadata.filegen** (*st_gen*): file generation number
* **metadata.creation** (*st_birthtime*): time of file creation

On Mac OS:

* **metadata.rsize** (*st_rsize*): ?
* **metadata.creator** (*st_creator*): ?
* **metadata.type** (*st_type*): ?

On RISCOS:

* **metadata.filetype** (*st_ftype*): file type
* **metadata.attributes** (*st_attrs*): attributes
* **metadata.objecttype** (*st_objtype*): object type

You may access any of these attributes as either normal attributes, or as dictionary keys. The following are both valid:

```python
filesize = metadata.size
filesize = metadata['size']
```

Optionally, you may pass `True` as a parameter to either `stat` or `symlink_stat`, to return the original data returned by `os.stat`, without changing the attribute names. This does, however, mean that dictionary key access no longer works. Example:

```python
metadata = some_file.stat(True)
filesize = metadata.st_size     # Valid
filesize = metadata['st_size']  # Won't work!
```

### Directory objects

There are some methods that are specific to directories, and only available on `Directory` objects.

#### Retrieving a child file/directory

You can use `get` to retrieve a `File` or `Directory` object for a child node. The type of node will automatically be detected, and either a `File` or `Directory` object will be returned as appropriate. The child doesn't have to be a direct child; it will simply join together the paths, so you can even retrieve nodes outside the path of the current `Directory`. A `FilesystemException` will be raised if the path does not exist.

Examples:

```python
child_dir = some_dir.get("assets")
deeper_child_file = some_dir.get("public/static/logo.png")
outside_dir = some_dir.get("../configuration")
```

#### Listing all child nodes

You may retrieve a list of `File` and `Directory` objects representing child nodes of the directory, by using `get_children`.

```python
child_nodes = some_dir.get_children()
```

Alternatively, you may use `get_files` or `get_directories` to only retrieve child files and directories, respectively. All files and directories will be wrapped in `File` and `Directory` objects.

### File objects

You may use `File` objects as actual Python file objects. There are three ways to do this:

#### As a context manager in read-only mode

The easiest way. The file object will be opened in `rb` (binary reading) mode. It will be automatically closed.

```python
some_file = filething.File("/some/file/on/my/system")

with some_file as f:
	print f.read()
```

#### As a context manager in another mode

If you need to do more than just reading, you may define an explicit mode. The file will still be automatically closed.

```python
some_file = filething.File("/some/file/on/my/system")

with some_file("wb") as f:
	f.write("hi!")
```

#### As a normal function

If context managers are not an option for some reason, you may retrieve the corresponding Python file object through a regular method. If you don't specify a mode, it will default to `rb`.

Note that when using this method, you need to manually close the file!

```python
some_file = filething.File("/some/file/on/my/system")

f = some_file.get_file_object("wb")
f.write("hi!")
f.close()
```