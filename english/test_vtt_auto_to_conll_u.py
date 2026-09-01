# Self-check for add_10ms() in vtt_auto_to_conll-u.py.
# Run directly: python test_vtt_auto_to_conll_u.py
#
# vtt_auto_to_conll-u.py can't be imported here (its module-level code
# depends on `somajo`, which isn't installed outside the pipeline's HPC
# environment -- see README Prerequisites). add_10ms() has no such
# dependency, so it's copied verbatim rather than importing the whole file.

def add_10ms(timestamp):
    h, m, s_ms = timestamp.split(":")
    s, ms = s_ms.split(".")
    total_ms = ((int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)) + 10
    h, rem_ms = divmod(total_ms, 3600000)
    m, rem_ms = divmod(rem_ms, 60000)
    s, ms = divmod(rem_ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def test_add_10ms():
    assert add_10ms("00:00:01.500") == "00:00:01.510"
    assert add_10ms("00:00:59.995") == "00:01:00.005"
    # regression: hour>=24 crashed the old datetime(2000,1,1,hour,...) implementation
    assert add_10ms("23:59:59.995") == "24:00:00.005"
    assert add_10ms("25:10:00.000") == "25:10:00.010"
    print("all tests passed")


if __name__ == "__main__":
    test_add_10ms()
