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


def test_yield_output_files_can_have_different_extension(tmpdir):
    base = "flow_"
    output_base = "output_"
    ext = 'dat'
    output_ext = 'xyz'

    base_path, _ = create_files_in_dir(tmpdir, base, num=10)

    generated_files = get_files_from_range(base_path, ext=ext,
            output_base=output_base, output_ext=output_ext)

    fn, fnout = next(generated_files)
    assert fn == "{}{:05d}.{}".format(base_path, 1, ext)
    assert fnout == "{}{:05d}.{}".format(output_base, 1, output_ext)


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


def test_yield_for_multiple_input_bases_yields_correctly(tmpdir):
    base1 = "one_"
    base2 = "two_"
    base3 = "three_"
    base_path1, _ = create_files_in_dir(tmpdir, base1, 10)
    base_path2, _ = create_files_in_dir(tmpdir, base2, 10)
    base_path3, _ = create_files_in_dir(tmpdir, base3, 10)

    generated_files = list(
        get_files_from_range(base_path1, base_path2, base_path3))

    assert len(generated_files) == 10

    fn1, fn2, fn3 = generated_files[0]
    assert fn1  == "{}{:05d}.dat".format(base_path1, 1)
    assert fn2  == "{}{:05d}.dat".format(base_path2, 1)
    assert fn3  == "{}{:05d}.dat".format(base_path3, 1)

    fn1, fn2, fn3 = generated_files[1]
    assert fn1  == "{}{:05d}.dat".format(base_path1, 2)
    assert fn2  == "{}{:05d}.dat".format(base_path2, 2)
    assert fn3  == "{}{:05d}.dat".format(base_path3, 2)

    fn1, fn2, fn3 = generated_files[2]
    assert fn1  == "{}{:05d}.dat".format(base_path1, 3)
    assert fn2  == "{}{:05d}.dat".format(base_path2, 3)
    assert fn3  == "{}{:05d}.dat".format(base_path3, 3)

    fn1, fn2, fn3 = generated_files[-1]
    assert fn1  == "{}{:05d}.dat".format(base_path1, 10)
    assert fn2  == "{}{:05d}.dat".format(base_path2, 10)
    assert fn3  == "{}{:05d}.dat".format(base_path3, 10)


def test_yield_for_multiple_bases_stops_at_first_missing_file(tmpdir):
    base_with_ten_files, _ = create_files_in_dir(tmpdir, 'ten', 10)
    base_with_five_files, _ = create_files_in_dir(tmpdir, 'five', 5)
    base_with_three_files, _ = create_files_in_dir(tmpdir, 'three', 3)

    generated_files = list(
        get_files_from_range(base_with_ten_files, base_with_five_files))
    assert len(generated_files) == 5

    generated_files = list(
        get_files_from_range(base_with_three_files, base_with_ten_files))
    assert len(generated_files) == 3


def test_yield_for_multiple_bases_with_output_works(tmpdir):
    base1 = "one_"
    base2 = "two_"
    output_base = "out"
    base_path1, _ = create_files_in_dir(tmpdir, base1, 10)
    base_path2, _ = create_files_in_dir(tmpdir, base2, 10)

    generated_files = list(
        get_files_from_range(base_path1, base_path2, output_base=output_base))

    [fn1, fn2], fnout = generated_files[0]
    assert fn1  == "{}{:05d}.dat".format(base_path1, 1)
    assert fn2  == "{}{:05d}.dat".format(base_path2, 1)
    assert fnout == "{}{:05d}.dat".format(output_base, 1)

    [fn1, fn2], fnout = generated_files[-1]
    assert fn1  == "{}{:05d}.dat".format(base_path1, 10)
    assert fn2  == "{}{:05d}.dat".format(base_path2, 10)
    assert fnout == "{}{:05d}.dat".format(output_base, 10)


def test_yield_for_multiple_bases_in_groups(tmpdir):
    base1 = "one_"
    base2 = "two_"
    output_base = "out"
    base_path1, _ = create_files_in_dir(tmpdir, base1, 10)
    base_path2, _ = create_files_in_dir(tmpdir, base2, 10)

    generated_files = list(
        get_files_from_range(base_path1, base_path2, output_base=output_base, num_per_output=2))

    assert len(generated_files) == 5

    [fns1, fns2], fnout = generated_files[0]
    assert fns1  == ["{}{:05d}.dat".format(base_path1, i) for i in [1, 2]]
    assert fns2  == ["{}{:05d}.dat".format(base_path2, i) for i in [1, 2]]
    assert fnout == "{}{:05d}.dat".format(output_base, 1)

    [fns1, fns2], fnout = generated_files[4]
    assert fns1  == ["{}{:05d}.dat".format(base_path1, i) for i in [9, 10]]
    assert fns2  == ["{}{:05d}.dat".format(base_path2, i) for i in [9, 10]]
    assert fnout == "{}{:05d}.dat".format(output_base, 5)


def test_yield_filenames_without_checking_for_file_existance(tmpdir):
    base = 'flow_'
    base_path, _ = create_files_in_dir(tmpdir, base, 0)

    generator = get_files_from_range(base_path, no_check=True)

    assert next(generator) == "{}{:05d}.dat".format(base_path, 1)
    assert next(generator) == "{}{:05d}.dat".format(base_path, 2)
    assert next(generator) == "{}{:05d}.dat".format(base_path, 3)

