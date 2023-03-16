from post_caldav_events.outputs import TelegramMarkdownv2Msg

sanatize = TelegramMarkdownv2Msg({}).sanatize

def test_none_input():
    assert sanatize(None) == ""

def test_escape_characters():
    assert sanatize("_*[]()~`>#+-={}|.!") == "\\_\\*\\[\\]\\(\\)\\~\\`\\>\\#\\+\\-\\=\\{\\}\\|\\.\\!"

def test_no_escape_characters():
    assert sanatize("<abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") == "<abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def test_mixed_characters():
    assert sanatize("abc_def*ghi[jkl]m<no(pqr)stu~vwx`yza]BCD>EFGH#IJKL+MNOPQR-STUV=WXYZ01|23456789") == "abc\\_def\\*ghi\\[jkl\\]m<no\\(pqr\\)stu\\~vwx\\`yza\\]BCD\\>EFGH\\#IJKL\\+MNOPQR\\-STUV\\=WXYZ01\\|23456789"
