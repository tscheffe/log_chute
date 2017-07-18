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
        (?P<size_bytes>\d+?)
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
        self.lines += 1

    def print_result(self):
        print "Number of lines parsed:", self.lines

class LogDuration(object):
    def __init__(self):
        self.earliest_timestamp = None;
        self.latest_timestamp = None;

    def process(self, matches):
        timestamp_string = matches['timestamp'][0:-6] # Strip the trailing timezone
        timestamp = datetime.strptime(timestamp_string, '%d/%b/%Y:%H:%M:%S')
        if self.earliest_timestamp == None or timestamp < self.earliest_timestamp:
            self.earliest_timestamp = timestamp

        if self.latest_timestamp == None or timestamp > self.latest_timestamp:
            self.latest_timestamp = timestamp

    def print_result(self):
        duration = self.latest_timestamp - self.earliest_timestamp
        print "Duration of log file", duration

class MostRequestedPage(object):
    def __init__(self): pass

    def process(self, matches): pass

    def print_result(self):
        print "Most requested page:"

class MostFrequentVisitor(object):
    def __init__(self): pass

    def process(self, matches): pass

    def print_result(self):
        print "Most frequent visitor:"

class MinPageLoadTime(object):
    def __init__(self):
        self.min_page_load_time = None

    def process(self, matches):
        duration_microseconds = int(matches['duration_microseconds'])
        if self.min_page_load_time == None \
                or duration_microseconds < self.min_page_load_time:
            self.min_page_load_time = duration_microseconds

    def print_result(self):
        print "Min page load time:", self.min_page_load_time

class AveragePageLoadTime(object):
    def __init__(self):
        self.total_page_load_time = 0
        self.total_pages_loaded = 0

    def process(self, matches):
        self.total_page_load_time += int(matches['duration_microseconds'])
        self.total_pages_loaded += 1

    def print_result(self):
        average_load_time = float(self.total_page_load_time) / self.total_pages_loaded

        print "Average page load time:", average_load_time

class MaxPageLoadTime(object):
    def __init__(self):
        self.max_page_load_time = None

    def process(self, matches):
        duration_microseconds = int(matches['duration_microseconds'])
        if self.max_page_load_time == None \
                or duration_microseconds > self.max_page_load_time:
            self.max_page_load_time = duration_microseconds

    def print_result(self):
        print "Max page load time:", self.max_page_load_time

class NumberOfErrors(object):
    def __init__(self):
        self.total_errors = 0

    def process(self, matches):
        status_code = int(matches['status_code'])
        if status_code >= 400:
            self.total_errors += 1;

    def print_result(self):
        print "Number of errors:", self.total_errors

class TotalDataTransfered(object):
    def __init__(self):
        self.total_data = 0

    def process(self, matches):
        self.total_data += int(matches['size_bytes'])

    def print_result(self):
        print "Total data transferred:", self.total_data

def main():
    if len(sys.argv) < 2:
        print "You didn't pass a filename to parse!"
        sys.exit(1)
    filename = sys.argv[1]
    processors = [
            LineCount(),
            LogDuration(),
            MostRequestedPage(),
            MostFrequentVisitor(),
            MinPageLoadTime(),
            AveragePageLoadTime(),
            MaxPageLoadTime(),
            NumberOfErrors(),
            TotalDataTransfered()
            ]
    parse(filename, processors)
    for processor in processors:
        processor.print_result()

if __name__ == '__main__':
    main()
