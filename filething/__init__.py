import sys, os, collections, contextlib

def map_attributes(obj, attr_map):
	attrs = {}
	
	for original, mapped in attr_map.iteritems():
		try:
			attrs[mapped] = getattr(obj, original)
		except AttributeError, e:
			pass
		
	if len(attrs) == 0:
		raise FilesystemException("No stat data received! This is probably a bug, please report it.")
	
	return Attributes(attrs)
	
class FilesystemException(Exception):
	pass

class Attributes(object):
	def __init__(self, data = {}):
		self.data = data
		self.__setattr__ = self._setattr # To prevent the previous line from causing havoc
		
	def __getattr__(self, attr):
		try:
			return self.data[attr]
		except KeyError, e:
			raise AttributeError("No such attribute.")
			
	def _setattr(self, attr, value):
		self.data[attr] = value
		
	def __getitem__(self, attr):
		return self.data[attr]
	
	def __setitem__(self, attr, value):
		self.data[attr] = value

class FilesystemObject(object):
	def __init__(self, path):
		if not os.path.exists(path):
			raise FilesystemException("The specified path (%s) either does not exist, or you cannot access it." % path)
			
		self.path = path
		self.name = os.path.basename(path)
		self.is_symlink = os.path.islink(self.path)
		
	def _process_stat(self, data, original_names):
		attr_map = {
			"st_mode": "mode",
			"st_ino": "inode",
			"st_dev": "device",
			"st_nlink": "links",
			"st_uid": "uid",
			"st_gid": "gid",
			"st_size": "size",
			"st_atime": "lastaccessed",
			"st_mtime": "lastmodified",
			"st_ctime": "ctime",
			"st_blocks": "blockcount",
			"st_blksize": "blocksize",
			"st_rdev": "devicetype",
			"st_flags": "userflags",
			"st_gen": "filegen",
			"st_birthtime": "creation",
			"st_rsize": "rsize",
			"st_creator": "creator",
			"st_type": "type",
			"st_ftype": "filetype",
			"st_attrs": "attributes",
			"st_objtype": "objecttype"
		}
		
		if original_names:
			return data
		else:
			return map_attributes(data, attr_map)
	
	def stat(self, original_names = False):
		return self._process_stat(os.stat(self.path), original_names)
	
	def symlink_stat(self, original_names = False):
		if self.is_symlink:
			return self._process_stat(os.lstat(self.path), original_names)
		else:
			raise FilesystemException("The specified path is not a symlink.")

class Directory(FilesystemObject):
	def _get_items(self):
		return os.listdir(self.path)
	
	def _join(self, name):
		return os.path.join(self.path, name)
		
	def get(self, name):
		child = self._join(name)
		
		if os.path.isdir(child):
			return Directory(child)
		else:
			return File(child)
	
	def get_children(self):
		return [self.get(x) for x in self._get_items()]
	
	def get_directories(self):
		return [Directory(self._join(x)) for x in self._get_items() if os.path.isdir(self._join(x))]
	
	def get_files(self):
		return [File(self._join(x)) for x in self._get_items() if os.path.isfile(self._join(x))]
		
class File(FilesystemObject):
	def __enter__(self, mode = "rb"):
		self.fileobj = self.get_file_object(mode)
		return self.fileobj
	
	def __exit__(self, exc_type, exc_value, traceback):
		self.fileobj.close()
		
	@contextlib.contextmanager
	def __call__(self, mode = "rb"):
		obj = self.__enter__(mode)
		
		try:
			yield obj
		finally:
			self.fileobj.close() # Can't call __exit__ here because we don't have an exception...
		
	def get_file_object(self, mode = "rb"):
		return open(self.path, mode)