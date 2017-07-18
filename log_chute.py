import re
import sys

    # import code; code.interact(local=dict(globals(), **locals()))

def parse(filename):
    'Return tuple of dictionaries containing file data.'
    log_re = re.compile(r"""
        \A
        (?P<ip>[.:0-9a-fA-F]{7,45})
        \s
        (?P<identd>-|.+?)
        \s
        (?P<userid>-|.+?)
        \s
        \[(?P<timestamp>.+?)\]
        \s
        "(?P<uri>[A-Z]+?\ /.*?\ HTTP/1.\d)"
        \s
        (?P<status_code>\d+?)
        \s
        (?P<size>\d+?)
        \s
        "(?P<referer>.*?)"
        \s
        "(?P<user_agent>.*?)"
        \s
        (?P<duration_microseconds>\d+?)
        \Z
    """, re.VERBOSE)

    line = '134.178.48.89 - - [21/Apr/2013:03:16:31 -0500] "DELETE /kms/alert/form/ HTTP/1.0" 200 5110 "https://example.com/kms/ledes/import/" "Mozilla/5.0 (Windows NT 4.0; en-US; rv:1.9.1.20) Gecko/2015-07-27 10:27:01 Firefox/5.0" 2247'
    matches = re.match(log_re, line)
    # import code; code.interact(local=dict(globals(), **locals()))
    print matches.group(match_group)

def main():
    if len(sys.argv) < 2:
        print "You didn't pass a filename to parse!"
        sys.exit(1)
    filename = sys.argv[1]
    print parse(filename)

if __name__ == '__main__':
    main()
