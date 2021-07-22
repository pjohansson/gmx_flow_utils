import numpy as np
import os 
import sys

from gmx_flow.utils import get_files_from_range

def create_files_in_dir(dir, base, num, ext='dat', begin=1):
    base_path = os.path.join(dir, base)

    paths = [
        "{}{:05}.{}".format(base, i + begin, ext) 
        for i in range(num)]

    for path in paths:
        dir.join(path).write("")

    return base_path, paths


def test_get_existing_files_from_range(tmpdir):
    base = "flow_"
    base_path, _ = create_files_in_dir(tmpdir, base, 10)

    generated_files = list(
        get_files_from_range(base_path))

    assert len(generated_files) == 10
    assert generated_files[0]  == "{}{:05d}.dat".format(base_path, 1)
    assert generated_files[1]  == "{}{:05d}.dat".format(base_path, 2)
    assert generated_files[2]  == "{}{:05d}.dat".format(base_path, 3)
    assert generated_files[-1] == "{}{:05d}.dat".format(base_path, 10)


def test_get_existing_files_from_range_with_begin_and_end(tmpdir):
    base = "flow_"

    begin = 5
    num = 4
    end = begin + num - 1

    base_path, _ = create_files_in_dir(tmpdir, base, num=10)

    generated_files = list(
        get_files_from_range(base_path, begin=begin, end=end))

    assert len(generated_files) == 4
    assert generated_files[0] == "{}{:05d}.dat".format(base_path, 5)
    assert generated_files[1] == "{}{:05d}.dat".format(base_path, 6)
    assert generated_files[2] == "{}{:05d}.dat".format(base_path, 7)
    assert generated_files[3] == "{}{:05d}.dat".format(base_path, 8)


def test_get_range_with_end_smaller_than_begin_yields_no_files(tmpdir):
    base = "flow_"
    base_path, _ = create_files_in_dir(tmpdir, base, num=10)

    generated_files = list(
        get_files_from_range(base_path, begin=5, end=4))
    
    assert len(generated_files) == 0




def test_get_existing_files_with_non_default_extension(tmpdir):
    base = "flow_"
    ext = 'png'

    base_path, _ = create_files_in_dir(tmpdir, base, num=10, ext=ext)

    generated_files = list(
        get_files_from_range(base_path, ext=ext))

    assert len(generated_files) == 10
    assert generated_files[0]  == "{}{:05d}.{}".format(base_path, 1, ext)
    assert generated_files[1]  == "{}{:05d}.{}".format(base_path, 2, ext)
    assert generated_files[2]  == "{}{:05d}.{}".format(base_path, 3, ext)
    assert generated_files[-1] == "{}{:05d}.{}".format(base_path, 10, ext)


def test_yield_existing_files_along_with_paths_for_output(tmpdir):
    base = "flow_"
    output_base = "output_"

    base_path, _ = create_files_in_dir(tmpdir, base, num=10)

    generated_files = get_files_from_range(base_path, output_base=output_base)

    fn, fnout = next(generated_files)
    assert fn == "{}{:05d}.dat".format(base_path, 1)
    assert fnout == "{}{:05d}.dat".format(output_base, 1)

    fn, fnout = next(generated_files)
    assert fn == "{}{:05d}.dat".format(base_path, 2)
    assert fnout == "{}{:05d}.dat".format(output_base, 2)


def test_yield_existing_files_in_groups_along_with_paths_for_output(tmpdir):
    base = "flow_"
    output_base = "output_"
    num_group = 4

    base_path, _ = create_files_in_dir(tmpdir, base, num=2 * num_group)

    generated_files = get_files_from_range(
        base_path, output_base=output_base, num_per_output=num_group)

    fns, fnout = next(generated_files)
    assert len(fns) == num_group
    assert fns[0] == "{}{:05d}.dat".format(base_path, 1)
    assert fns[1] == "{}{:05d}.dat".format(base_path, 2)
    assert fns[2] == "{}{:05d}.dat".format(base_path, 3)
    assert fns[3] == "{}{:05d}.dat".format(base_path, 4)
    assert fnout == "{}{:05d}.dat".format(output_base, 1)

    fns, fnout = next(generated_files)
    assert len(fns) == num_group
    assert fns[0] == "{}{:05d}.dat".format(base_path, 5)
    assert fns[1] == "{}{:05d}.dat".format(base_path, 6)
    assert fns[2] == "{}{:05d}.dat".format(base_path, 7)
    assert fns[3] == "{}{:05d}.dat".format(base_path, 8)
    assert fnout == "{}{:05d}.dat".format(output_base, 2)
