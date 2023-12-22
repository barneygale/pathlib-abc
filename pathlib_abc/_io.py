import sys


def text_encoding(encoding):
    if encoding is not None:
        return encoding
    elif sys.flags.utf8_mode:
        return "utf-8"
    else:
        return "locale"
