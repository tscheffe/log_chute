Take a 10MB Apache log file.  It's lines are formatted according to the standard
"Combined" log format, with one addition: %D added as the last field in the format string.

Write a Python program that takes a filename as its only argument, and outputs
the following data:

    Number of lines parsed:
    Duration of log file:

    Most requested page:
    Most frequent visitor:

    Min page load time:
    Average page load time:
    Max page load time:

    Number of errors:
    Total data transferred:

NOTE: I should add p95 and total 400 vs 500 errors. But do it in an '--improved'
mode so that if they have automated tests to verify things then it won't break them.

# Notes:
Combined Log Format:
```
LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\"" combined

134.178.48.89 - - [21/Apr/2017:03:16:31 -0500] "DELETE /kms/alert/form/ HTTP/1.0" 200 5110 "https://example.com/kms/ledes/import/" "Mozilla/5.0 (Windows NT 4.0; en-US; rv:1.9.1.20) Gecko/2015-07-27 10:27:01 Firefox/5.0" 2247
```
- %h is the IP address of the client
- %l is the RFC 1413 identity of the cilent, determined by `identd`, highly
unreliable, hyphen means it could not be determined
- %u is the userid of the person requesting the document, if it's not password
protected then this will be a hyphen
- %t is the time, [day/month/year:hour:minute:second zone]
- \"%r\" is the request line from client in double quotes
- %>s is the status code
- %b is the size of the object returned to the client, not including response
headers, if hyphen then zero
- %{Referer}i is the Referer HTTP request header
- %{User-agent}i is the User-Agent HTTP request header

%D was added to the traditional "Combined" format string, which is the time
taken to serve the request in microseconds

Thoughts before starting:
- Make sure to stream the file, not slurp it, so we don't run into memory problems.
- I don't know if we'll run into tricky encoding problems or not, best to not worry about it
until something happens.

Steps:
- First I looked up documentation for the Apache Combined Log Format
- Googled Python apache log parser
- Found some github projects, seemed complex
- Found [this stack overflow](https://stackoverflow.com/questions/12544510/parsing-apache-log-files)
- Debated about splitting into tokens based on whitespaces or a regex.
- I like the idea of getting a dictionary back from the named groups and regex
solves the problem completely, with no "special casing" token munging for the
quoted segments, which seems more pythonic.
  - Turns out that `MatchGroup.groupdict()` is exactly what I want!
- Next step is to find a regex to use, or come up with one.
- [This github project](https://github.com/lethain/apache-log-parser) actually
uses a regex, I'll base mine off of that.
- Looked up python Regexes and found a description of `re.VERBOSE` which seems
perfect
- You can go _crazy_ with IP validation regexes but I elected to keep it as simple as possible
- `\s` looked better than a `\ ` to me, and it won't get mauled by text editors
that remove trailing whitespace
- Decided to just get the regexes working without further iteration, I can come
back to optimze if needed
- Discovering how to do all the ruby tricks I'm used to like `binding.pry` and
`obj.public_methods` is interesting
- Generators and, what I believe are, "list comprehensions" are pretty slick
- I was worried that I'd run into issues where every line in the file is slurped
and I'd run into performance or memory constraints, but I believe that the matches
generator expression will only pull lines as needed which is awesome. I do immediately
make a match object for each line, but I'll fix that later
- I get the same number of matched lines as `wc -l log_file`, and it's quick, but
I should verify that each match group is present in each line too. It works!
- Tested the parser on a 1.3 gigabyte file, 128 times larger than the provided
log file, and it works just takes awhile. Might try bigger later, but the iteration
time slows down.
- Tried to use `valgrind` to get the maximum memory used, just for fun, but can't
be used without a "valgrind friendly" compiled Python that has debug enabled. But
GNU `time`, and ZSH `time`, work as well, I'll be able to reduce memory footprint
if needed.
- Time to build out functionality and actually do something based on the matches
- Middleware was a good idea, and it'd be interesting to implement with the first
class functions in Python, but it's likely too complex. I bet I can do it simpler,
because we don't have a "request" piece, only response.
- Implemented a simple class that responds to `process(matches)` and `print_result()`,
basically the Visitor pattern. This worked perfectly for counting lines, now let's
expand it.
- Timestamps in 2.7 are not easy, fortunately we can just strip the timezone when
we're only looking for duration, we'll assume all of the logs have the same timezone
when doing the processing
