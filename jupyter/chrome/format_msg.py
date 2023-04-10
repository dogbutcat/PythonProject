import re

def decode_msg(data):
    split_arr = [d for d in data.split("/") if d]
    is_arr = "@=" not in data and data.endswith("/")
    is_obj = "@=" in data and data.endswith("/")
    if not is_arr and not is_obj:
        return data
    result = [] if is_arr else {}
    for i, d in enumerate(split_arr):
        if not is_arr:
            k, v = d.split("@=")
            v = format_msg(v)
            k = format_msg(k)
            result[k] = decode_msg(v)
        else:
            v = format_msg(d)
            result.append(decode_msg(v))
    return result


def format_msg(msg):
    return re.sub(r'@(A|S)', lambda v: '@' if v.group(0) == '@A' else '/', msg)