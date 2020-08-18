from collections.abc import MutableSequence
from mmap import mmap
import os

# right now this counts all lines from the start
# if delimitedfile.linemap had negative offset in it, it could quickly skip to the end
# maybe easier if two linemaps were held

# TODO: including trailing items not followed by delimiter (usually unwanted with line delimiting on linux)

class delimitedfile(MutableSequence):
    def __init__(self, path = None, delimiter = os.linesep, encoding = 'utf-8'):
        self.path = None
        self.file = None
        self.open(path, delimiter, encoding)

    def open(self, path = None, delimiter = os.linesep, encoding = 'utf-8'):
        self.close()
        if None != path:
            self.path = path

        self.delimiter = delimiter.encode(encoding)
        self.encoding = encoding

        if None == self.path:
            return

        self.linemap = [0]
        self.length = None

        try:
            self.openandmmap()
        except FileNotFoundError:
            self.close()
        except ValueError:
            # mmap failed, file has zero length
            self.close()

    def close(self):
        if None != self.file:
            os.close(self.file)
            self.file = None
        self.linemap = [0]
        self.map = None
        self.length = 0

    # operators

    def __len__(self):
        if None is self.map: # file is empty or missing
            return 0
        if None is self.length: 
            self.getalloffsets()
        return self.length

    def __getitem__(self, linenumber):
        nextoffset = self.getoffset(linenumber + 1) - len(self.delimiter)
        offset = self.getoffset(linenumber)
        return self.map[offset:nextoffset].decode(self.encoding)

    def __setitem__(self, linenumber, value):
        value = value.encode(self.encoding) + self.delimiter
        offset = self.getoffset(linenumber)
        nextoffset = offset + len(value)
        self.setoffset(linenumber + 1, nextoffset)
        self.map[offset:nextoffset] = value

    def __delitem__(self, linenumber):
        self.setoffset(linenumber + 1, self.getoffset(linenumber))
        self.deloffset(linenumber)

    def insert(self, linenumber, value):
        value = value.encode(self.encoding) + self.delimiter
        offset = self.getoffset(linenumber)
        nextoffset = offset + len(value)
        self.setoffset(linenumber, offset + len(value))
        self.insertoffset(linenumber, offset)
        self.map[offset:nextoffset] = value

    # context management
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        self.close()
    def __del__(self):
        self.close()

    # utilities
    def getoffset(self, linenumber):
        if slice is type(linenumber):
            raise IndexError('slicing unimplemented')

        if linenumber < 0:
            linenumber += len(self)

        if linenumber < 0:
            raise IndexError('line number out of range')

        if linenumber < len(self.linemap):
            return self.linemap[linenumber]

        if None is self.map: # file is empty or missing
            raise IndexError('line number out of range')

        offset = self.linemap[-1]
        while len(self.linemap) <= linenumber:
            offset = self.map.find(self.delimiter, offset)
            if -1 == offset:
                self.length = len(self.linemap) - 1
                raise IndexError('line number out of range')
            offset += len(self.delimiter)
            self.linemap.append(offset)
        return self.linemap[-1]
    def getalloffsets(self):
        offset = self.linemap[-1]
        while True:
            offset = self.map.find(self.delimiter, offset)
            if -1 == offset:
                break
            offset += len(self.delimiter)
            self.linemap.append(offset)
        self.length = len(self.linemap) - 1
    def setoffset(self, linenumber, offset):
        if slice is type(linenumber):
            raise IndexError('slicing unimplemented')
        prevoffset = self.getoffset(max(0,linenumber-1))
        oldoffset = self.getoffset(linenumber)
        if oldoffset < prevoffset:
            raise IndexError('line number out of range')
        difference = offset - oldoffset
        if None is self.map: # file empty or missing
            oldtail = 0
            assert oldoffset == 0
            self.openandmmap(difference)
        else:
            oldtail = len(self.map)
        tail = oldtail + difference
        if difference > 0:
            # grow the file
            self.map.resize(tail)
        self.map[offset:tail] = self.map[oldoffset:oldtail]
        self.linemap[linenumber:] = (offset + difference for offset in self.linemap[linenumber:])
        if difference < 0:
            # shrink the file
            self.map.resize(tail)
    def deloffset(self, linenumber):
        del self.linemap[linenumber]
        if None is not self.length: 
            self.length = self.length - 1

    def insertoffset(self, linenumber, offset):
        self.linemap.insert(linenumber, offset)
        if None is not self.length: 
            self.length = self.length + 1

    def openandmmap(self, clobber_to_size = 0):
        flags = os.O_RDWR
        if clobber_to_size > 0:
            self.file = os.open(self.path, os.O_RDWR | os.O_CREAT)
            os.ftruncate(self.file, clobber_to_size)
        else:
            self.file = os.open(self.path, os.O_RDWR)
        self.map = mmap(self.file, 0)
