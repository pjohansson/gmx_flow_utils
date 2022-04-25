import os
from gmx_flow.utils.fileio import gen_file_range


#############
# Utilities #
#############

def get_base(tmp_path: str, base: str) -> str:
    return os.path.join(tmp_path, base)


def get_path(base: str, i: int, ext: str = 'dat') -> str:
    return f"{base}{i:05}.{ext}"


def create_file_range(base: str, num: int, begin: int = 1, ext='dat'):
    end = begin + num
    for i in range(begin, end):
        path = get_path(base, i, ext)

        fp = open(path, 'w')
        fp.close()


########################
# Simple range options #
########################

def test_iterate_over_range_yields_expected_items(tmp_path):
    base = get_base(tmp_path, 'test')
    num_files = 10
    create_file_range(base, num_files)

    fns = list(gen_file_range(base))

    assert len(fns) == num_files
    assert fns[0] == get_path(base, 1)
    assert fns[1] == get_path(base, 2)
    assert fns[-1] == get_path(base, num_files)



# def test_iterate_over_broken_range_stops_at_break(tmp_path):
#     base = get_base(tmp_path, 'test')
#     num_files = 10
#     create_file_range(base, num_files, begin=1)

#     begin_next_range = num_files + 2
#     create_file_range(base, num_files, begin=begin_next_range)

#     fns = list(get_files_from_range(base))

#     assert len(fns) == num_files
#     assert fns[0] == get_path(base, 1)
#     assert fns[1] == get_path(base, 2)
#     assert fns[-1] == get_path(base, num_files)


# def test_begin_and_end_of_range_options_work(tmp_path):
#     base = get_base(tmp_path, 'test')
#     num_files = 10
#     create_file_range(base, num_files)

#     begin = 4
#     end = 8
#     fns = list(get_files_from_range(base, begin=begin, end=end))

#     assert len(fns) == end - begin + 1
#     assert fns[0] == get_path(base, begin)
#     assert fns[1] == get_path(base, begin + 1)
#     assert fns[-1] == get_path(base, end)
