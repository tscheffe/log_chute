import re
import sys

# def parse(filename):
#     print filename
#     line = '172.16.0.3 - - [25/Sep/2002:14:04:19 +0200] "GET / HTTP/1.1" 401 - "" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.1) Gecko/20020827"'
#     regex = '([(\d\.)]+) - - \[(.*?)\] "(.*?)" (\d+) - "(.*?)" "(.*?)"'

#     print re.match(regex, line).groups()

def parse(filename):
    'Return tuple of dictionaries containing file data.'
    def make_entry(x):
        return {
            'server_ip':x.group('ip'),
            'uri':x.group('uri'),
            'time':x.group('time'),
            'status_code':x.group('status_code'),
            'referral':x.group('referral'),
            'agent':x.group('agent'),
            }
    log_re = re.compile(r"""
        (?P<ip>[.:0-9a-fA-F]{7,45})
        \s
        (?P<identd>.*)
        \s
        -
        \s
        \[(?P<time>.*?)\]
        \s
        "GET (?P<uri>.*?) HTTP/1.\d"
        \s
        (?P<status_code>\d+)
        \s
        \d+
        \s
        "(?P<referral>.*?)"
        \s
        "(?P<agent>.*?)"
        \s
        "(?P<response_time>\d+?)"
    """, re.VERBOSE)
    # Scan through a string, looking for any location where this RE matches.
    search = re.compile(log_re).search
    matches = (search(line) for line in file(filename))
    return (make_entry(x) for x in matches if x)

matchers = {
        'ip':'(?P<ip>[.:0-9a-fA-F]{7,45})'
        }

def run_matcher(matcher, group):
    line = '134.178.48.89 - - [21/Apr/2013:03:16:31 -0500] "DELETE /kms/alert/form/ HTTP/1.0" 200 5110 "https://example.com/kms/ledes/import/" "Mozilla/5.0 (Windows NT 4.0; en-US; rv:1.9.1.20) Gecko/2015-07-27 10:27:01 Firefox/5.0" 2247'
    print re.match(matcher, line).group(group)

def main():
    if len(sys.argv) < 2:
        print "You didn't pass a filename to parse!"
        sys.exit(1)
    filename = sys.argv[1]
    # parse(filename)

    run_matcher(matchers['ip'], 'ip')

if __name__ == '__main__':
    main()
