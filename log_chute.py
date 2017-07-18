import re
import sys
from datetime import datetime

def parse(filename, processors):
    'Process a given log file with provided processors'

    log_re = re.compile(r"""
        # LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\" %D"

        (?P<ip>[.:0-9a-fA-F]{7,45})    # %h - client IP
        \s
        (?P<identd>-|.+?)              # %l - identity of the client from `identd`
        \s
        (?P<userid>-|.+?)              # %u - userid of client for password protected documents
        \s
        \[(?P<timestamp>.+?)\]         # %t - timestamp
        \s
        "(?P<request_line>[A-Z]+?\ /.*?\ HTTP/1\.\d)" # "%r" - request line from client
        \s
        (?P<status_code>\d+?)          # %>s - status code of request
        \s
        (?P<size_bytes>\d+?)           # %b - size of object returned to client, in bytes
        \s
        "(?P<referer>.*?)"             # "%{Referer}i" - Referer HTTP request header
        \s
        "(?P<user_agent>.*?)"          # "%{User-agent}i" - User-Agent HTTP request header
        \s
        (?P<duration_microseconds>\d+) # %D - time taken to serve request, in microseconds
    """, re.VERBOSE)

    match = re.compile(log_re).match
    matches = (match(line) for line in open(filename, 'r'))

    matched_tuples = (match.groupdict() for match in matches if match)

    for matched in matched_tuples:
        for processor in processors:
            processor.process(matched)

class LineCount(object):
    'Processor to count the total number of lines in a log file'

    def __init__(self):
        self.lines = 0

    def process(self, _matches):
        'Increase the line count by 1 for each match set that is received'

        self.lines += 1

    def print_result(self):
        print "Number of lines parsed:", self.lines

class LogDuration(object):
    'Processor to determine the duration a log file spans based on timestamps'

    def __init__(self):
        self.earliest_timestamp = None
        self.latest_timestamp = None

    def process(self, matches):
        'Capture the earliest and latest timestamps, zero assumptions on ordering'

        timestamp_string = matches['timestamp'][0:-6] # Strip the trailing timezone
        timestamp = datetime.strptime(timestamp_string, '%d/%b/%Y:%H:%M:%S')
        if self.earliest_timestamp is None or timestamp < self.earliest_timestamp:
            self.earliest_timestamp = timestamp

        if self.latest_timestamp is None or timestamp > self.latest_timestamp:
            self.latest_timestamp = timestamp

    def print_result(self):
        duration = self.latest_timestamp - self.earliest_timestamp
        print "Duration of log file", duration

class MostRequestedPage(object):
    'Processor to find the most requested page from a log file'

    def __init__(self):
        self.requested_pages = {}
        self.most_requested_page = None

    def process(self, matches):
        'Track each page request by incrementing a count in a dict keyed by request'

        requested_page = matches['request_line']

        # Initialize key/value if we haven't seen page before
        if requested_page not in self.requested_pages:
            self.requested_pages[requested_page] = 0

        self.requested_pages[requested_page] += 1

        # Keep running track of most requested page to avoid future comparisons
        if self.most_requested_page is None \
                or (self.requested_pages[self.most_requested_page]
                        < self.requested_pages[requested_page]):
            self.most_requested_page = requested_page

    def print_result(self):
        print "Most requested page:", self.most_requested_page

class MostFrequentVisitor(object):
    'Processor to find the most frequent visitor based on IP address from a log file'

    def __init__(self):
        self.visitors = {}
        self.most_frequent_visitor = None

    def process(self, matches):
        'Track each visitor by incrementing a count in a dict keyed by IP'

        visitor = matches['ip']

        # Initialize key/value if we haven't seen this visitor before
        if visitor not in self.visitors:
            self.visitors[visitor] = 0

        self.visitors[visitor] += 1

        # Keep running track of the most frequent visitor to avoid future comparisons
        if self.most_frequent_visitor is None \
                or (self.visitors[self.most_frequent_visitor]
                        < self.visitors[visitor]):
            self.most_frequent_visitor = visitor

    def print_result(self):
        print "Most frequent visitor:", self.most_frequent_visitor

class MinPageLoadTime(object):
    'Processor to determine the minimum page load time from a log file'

    def __init__(self):
        self.min_page_load_time = None

    def process(self, matches):
        'Find the minimum load time by comparing each match to current minimum'

        duration_microseconds = int(matches['duration_microseconds'])
        if self.min_page_load_time is None \
                or duration_microseconds < self.min_page_load_time:
            self.min_page_load_time = duration_microseconds

    def print_result(self):
        print "Min page load time:", self.min_page_load_time

class AveragePageLoadTime(object):
    'Processor to determine the average page load time from a log file'

    def __init__(self):
        self.total_page_load_time = 0
        self.total_pages_loaded = 0

    def process(self, matches):
        'Total the page load time and pages load to create an average'

        self.total_page_load_time += int(matches['duration_microseconds'])
        self.total_pages_loaded += 1

    def print_result(self):
        average_load_time = float(self.total_page_load_time) / self.total_pages_loaded

        print "Average page load time:", average_load_time

class MaxPageLoadTime(object):
    'Processor to determine the maximum page load time from a log file'

    def __init__(self):
        self.max_page_load_time = None

    def process(self, matches):
        'Find the maximum load time by comparing each match to current maximum'

        duration_microseconds = int(matches['duration_microseconds'])
        if self.max_page_load_time is None \
                or duration_microseconds > self.max_page_load_time:
            self.max_page_load_time = duration_microseconds

    def print_result(self):
        print "Max page load time:", self.max_page_load_time

class NumberOfErrors(object):
    'Processor to count the number of errors recorded in a log file'

    def __init__(self):
        self.total_errors = 0

    def process(self, matches):
        'Increment total error count If the matched line has a status of 4xx or 5xx'

        status_code = int(matches['status_code'])
        if status_code >= 400:
            self.total_errors += 1

    def print_result(self):
        print "Number of errors:", self.total_errors

class TotalDataTransfered(object):
    'Processor to sum the total data transfered, in bytes, from a log file'

    def __init__(self):
        # Don't worry about maximum int size, overflow is prevented automagically
        self.total_data = 0

    def process(self, matches):
        'Add the size of data transferred from a match to the running total'

        self.total_data += int(matches['size_bytes'])

    def print_result(self):
        print "Total data transferred:", self.total_data

def main():
    'Entry function for the log_chute script'

    # Validate that we received a filename and then extract it
    if len(sys.argv) < 2:
        print "You didn't pass a filename to parse!"
        sys.exit(1)
    filename = sys.argv[1]

    # Build the processor objects and then parse the log file
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

    # Print the results from all of the processors
    for processor in processors:
        processor.print_result()

if __name__ == '__main__':
    main()
