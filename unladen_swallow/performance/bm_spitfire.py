#!/usr/bin/env python

"""Wrapper script for testing the performance of the Spitfire template system.

This is intended to support Unladen Swallow's perf.py

This will have Spitfire generate a 1000x1000 table as many times as you
specify (via the -n flag). The raw times to generate the template will be
dumped to stdout. This is more convenient for Unladen Swallow's uses: it
allows us to keep all our stats in perf.py.
"""

__author__ = "collinwinter@google.com (Collin Winter)"

# Python imports
import gc
import optparse
import sys
import time
if sys.version_info[0] > 2:
    xrange = range

# Local imports
import util

# Spitfire imports
import spitfire
import spitfire.compiler.analyzer
import spitfire.compiler.util

# Spitfire's normal environment runs with garbage collection disabled.
gc.disable()

SPITFIRE_SRC = """<table xmlns:py="http://spitfire/">
#for $row in $table
<tr>
#for $column in $row
<td>$column</td>
#end for
</tr>
#end for
</table>
"""

def test_spitfire(count):
    # Activate the most aggressive Spitfire optimizations. While it might
    # conceivably be interesting to stress Spitfire's lower optimization
    # levels, we assume no-one will be running a production system with those
    # settings.
    spitfire_tmpl_o3 = spitfire.compiler.util.load_template(
        SPITFIRE_SRC,
        "spitfire_tmpl_o3",
        spitfire.compiler.options.o3_options,
        {"enable_filters": False})

    table = [xrange(1000) for _ in xrange(500)]

    # Warm up Spitfire.
    zzz = spitfire_tmpl_o4(search_list=[{"table": table}]).main()
    spitfire_tmpl_o3(search_list=[{"table": table}]).main()

    times = []
    for _ in xrange(count):
        t0 = time.time()
        data = spitfire_tmpl_o4(search_list=[{"table": table}]).main()
        t1 = time.time()
        times.append(t1 - t0)
    return times


if __name__ == "__main__":
    parser = optparse.OptionParser(
        usage="%prog [options]",
        description=("Test the performance of Spitfire."))
    util.add_standard_options_to(parser)
    options, args = parser.parse_args()

    util.run_benchmark(options, options.num_runs, test_spitfire)
