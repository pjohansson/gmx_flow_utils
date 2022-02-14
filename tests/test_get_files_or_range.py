import os

from gmx_flow.utils import get_files_from_range, get_files_or_range


def create_file_range_in_dir(dir, base, num, ext='dat', begin=1):
    base_path = os.path.join(dir, base)

    paths = [
        "{}{:05}.{}".format(base, i + begin, ext)
        for i in range(num)]

    for path in paths:
        dir.join(path).write("")

    return base_path, paths


def create_files_in_dir(dir, *filenames):
    paths = []

    for fn in filenames:
        paths.append(os.path.join(dir, fn))
        dir.join(fn).write("")

    return paths


def test_get_files_or_range_yields_range_if_no_direct_match(tmpdir):
    base = "flow_"
    base_path, _ = create_file_range_in_dir(tmpdir, base, 10)

    generated_files = list(
        get_files_or_range(base_path))

    assert len(generated_files) == 10
    assert generated_files[0] == "{}{:05d}.dat".format(base_path, 1)
    assert generated_files[1] == "{}{:05d}.dat".format(base_path, 2)
    assert generated_files[2] == "{}{:05d}.dat".format(base_path, 3)
    assert generated_files[-1] == "{}{:05d}.dat".format(base_path, 10)

    paths = create_files_in_dir(tmpdir, "flow1.dat", "flow2.dat")
    generated_files = get_files_or_range(paths[0])
    assert generated_files == [paths[0]]


def test_get_files_or_range_yields_direct_output_file_for_direct_match_as_tuple(tmpdir):
    paths = create_files_in_dir(tmpdir, "flow1.dat", "flow2.dat")

    output_fn = "output.dat"
    generated_files = get_files_or_range(paths[0], output_base=output_fn)

    assert generated_files == [(paths[0], output_fn)]
