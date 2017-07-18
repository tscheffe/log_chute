import re
import sys
from datetime import datetime

# import code; code.interact(local=dict(globals(), **locals()))

def parse(filename, processors):
    'Process a given log file with provided processors'
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
        (?P<duration_microseconds>\d+)
    """, re.VERBOSE)

    # Scan through a string, looking for any location where this RE matches.
    match = re.compile(log_re).match
    matches = (match(line) for line in open(filename, 'r'))

    matched_tuples = (match.groupdict() for match in matches if match)

    for matched in matched_tuples:
        for processor in processors:
            processor.process(matched)

class LineCount(object):
    def __init__(self):
        self.lines = 0;

    def process(self, matches):
        self.lines = self.lines + 1

    def print_result(self):
        print "Number of lines parsed: ", self.lines

class LogDuration(object):
    def __init__(self):
        self.earliest_timestamp = None;
        self.latest_timestamp = None;

    def process(self, matches):
        timestamp_string = matches['timestamp'][0:-6] # Strip the trailing timezone
        timestamp = datetime.strptime(timestamp_string, '%d/%b/%Y:%H:%M:%S')
        # import code; code.interact(local=dict(globals(), **locals()))
        if self.earliest_timestamp == None or timestamp < self.earliest_timestamp:
            self.earliest_timestamp = timestamp

        if self.latest_timestamp == None or timestamp > self.latest_timestamp:
            self.latest_timestamp = timestamp

    def print_result(self):
        duration = self.latest_timestamp - self.earliest_timestamp
        print "Duration of log file", duration

def main():
    if len(sys.argv) < 2:
        print "You didn't pass a filename to parse!"
        sys.exit(1)
    filename = sys.argv[1]
    processors = [
            LineCount(),
            LogDuration()
            ]
    parse(filename, processors)
    for processor in processors:
        processor.print_result()

if __name__ == '__main__':
    main()
