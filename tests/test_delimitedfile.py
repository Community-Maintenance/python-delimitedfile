from delimitedfile import delimitedfile

import os
import pytest

@pytest.fixture
def new_file(tmpdir):
    return delimitedfile(tmpdir / 'delimitedfile.test')

def readfile(delimited):
    with open(delimited.path) as file:
        return file.read()

def test_new_len(new_file):
    file = new_file
    assert len(file) == 0

def test_new_exceptions(new_file):
    file = new_file
    with pytest.raises(IndexError):
        file[0]
    with pytest.raises(IndexError):
        file[1]
    with pytest.raises(IndexError):
        file[-1]
    with pytest.raises(IndexError):
        file[0] = 'test'
    with pytest.raises(IndexError):
        file[1] = 'test'
    with pytest.raises(IndexError):
        file[-1] = 'test'

def test_new_append(new_file):
    file = new_file
    file.append('hello')
    assert len(file) == 1
    assert f'hello{os.linesep}' == readfile(file)
    assert file[0] == 'hello'
    assert file[-1] == 'hello'

    file.insert(0, 'pre-hello')
    assert f'pre-hello{os.linesep}hello{os.linesep}' == readfile(file)
    assert file[0] == 'pre-hello'
    assert file[1] == 'hello'
    assert file[-1] == 'hello'
    assert len(file) == 2

    with pytest.raises(IndexError):
        file[2]

    with pytest.raises(IndexError):
        file[2] = 'test'

