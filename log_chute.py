import re
import sys

    # import code; code.interact(local=dict(globals(), **locals()))

def parse(filename):
    'Return tuple of dictionaries containing file data.'
    log_re = re.compile(r"""
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
    """, re.VERBOSE)

    # Scan through a string, looking for any location where this RE matches.
    match = re.compile(log_re).match
    # Bets on if we'll have memory issues?
    matches = (match(line) for line in file(filename).readlines())
    matched_tuples = (match.groupdict() for match in matches if match)

    total = 0
    bad_matches = 0
    for matched in matched_tuples:
        # print matched
        if None in matched.values():
            bad_matches = bad_matches + 1
            print "Bad match: ", matched
        total = total + 1

    print "Found matching lines: ", total
    print "Found bad matches: ", bad_matches
    return matched_tuples

def main():
    if len(sys.argv) < 2:
        print "You didn't pass a filename to parse!"
        sys.exit(1)
    filename = sys.argv[1]
    parse(filename)

if __name__ == '__main__':
    main()
