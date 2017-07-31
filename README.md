# Usage
```shell
python log_chute.py path/to/log_file
```

Tested with Python 2.7.13 and Python 3.6.1.


# Installation
```shell
git clone git@github.com:tscheffe/log_chute.git
```

No additional dependencies.

# Requirements
Given an Apache log file, lines formatted according to the standard "Combined" log format plus %D at the end.

Deliver a python script that takes a filename and outputs some data:

# Discussion Points
## Assumptions
I made assumptions in three places: how to interpret ambiguous requirements, that
the quality of the input log file is high, and that the constraint is on memory
not time.

There weren't many ambiguous requirements, they were appropriately specific for the
most part. I had to define what a "requested page" was and guess what the "duration"
meant. I elected to go with the most simplistic interpretation each time, leaving
room for further business logic in the future if needed.

At the start I was worried about encodings, line endings, malformed logs, that sort
of thing. As implementation proceeded I found that the provided log file was uniform
and easily parsed. The code isn't "hardened", if a malformed log was input then it
would certainly break. I'm not familiar with the Apache logging and can't predict
what sorts of issues I should validate to avoid, so I assumed that the quality
would be consistent. If there is a problem in the future it should be easy to address
and add a validation for protection.

If you hadn't mentioned "will be tested with a substantially larger one" then I
don't think I would have gone to the lengths I did to ensure memory safety. I've
over-optimized for that in the past and wasted time when I didn't need to, now I'm
wary about investing time there. Previous experience did help me get it right without
much of a struggle, or maybe Python just gets it right by default.

## Verification
I elected to verify by hand rather than with unit tests. Everything is imperative,
if anything breaks then everything will. It's like singing the ABCs, you don't need
to practice A -> B independent of C -> D. For implementing, I had a REPL open and
would try something in there to verify and then codify it before running the script
again to determine that the feature I had just implemented worked as part of the whole.

For the individual output values, I compared them to numbers derived from shell tools
like `wc -l log_File`, `ag --count '192.168.1.1' log_file`, and
`awk '{sum+=$NF} END {print sum}'`.

## Limitations
I didn't run into too many limitations with the actual problem, only with how my
experiences relate to it. I'm not as familiar with Python so there was a lot of
"python #{problem I want to solve but don't know how}" googling. I even proc'd the
Google "you're speaking our language" test for Python which was interesting. For
the most part, I had a good idea for what I wanted to do and was limited by how
to actually implement it but that's a part of learning and continued to be interesting.

## PEP8/Style
Ran `pylint` with the default configuration and got a good score, remaining
violations are `superfluous-parens` for `print` which I'm ignoring to maintain
Python 3.6 compatability and a few `missing-docstring` for the `__init__` and
`print_result` methods which I felt were superfluous and would only add additional
noise.

I also reread the PEP8 style guide and feel that I'm in line with it.

## Git Commits and Commit Messages
If this were proper _Github Flow_ I would clean up my commits by squashing them
down into a nice clean history. For now I've elected to leave them as-is and
maintain an unfiltered history. Of course, they're all "high quality", tpope approved,
messages as qualified by [this blog post](https://chris.beams.io/posts/git-commit/).

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

# Development Steps/Process:
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
- Duration worked out well with the processor model, time to go ham and implement
a bunch
- I could combine min, max, and average page load times but that breaks consistency
which dilutes the simplicity of the pattern. Sometimes to be understandable than DRY,
and there really isn't much duplication. Better separation of concerns too.
- Compared the `time` reported sizes for 11M file vs 1.3G file and it went from
5456MB -> 5644MB which is O(1), awesome. Time went from 1.63s to 208s which is
~127.7x slower, on a 128x larger file; O(n) based on file size!
- "Most requested page" is ambiguous, should 'PUT /xyz' and 'GET /xyz' count as
the same page? Or different? In this case, it actually ends up being the same page
but the difference could matter in the future. I'll commit both interpretations,
though the "final version" will be the simplistic one where each different request
line is treated as a unique key; no extracting of the "page".
