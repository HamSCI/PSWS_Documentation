"""
what this does

Does not currently handle more than one error in file (nor errors
that would occur at the beginning or end of the file.)
"""

import csv
import io
import os
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from dateutil import parser

DEBUG = False


def _is_header(line):
    return (
        line[0] != "#"
        and line != "UTC,Freq,Freq Err,Vpk,dBV(Vpk)\n"
        and "\x00" not in line
    )


def _seek_to_start_of_data(f):
    f.seek(0)
    line = f.readline()

    while line != "":
        if line[:3] == "UTC":
            # next readline is the first row of data
            print("header line is", line)
            return

        line = f.readline()

    # file has no header
    print("file has no header")
    f.seek(0)
    return


# sign of the error: timestamp goes backwards
def _find_time_delta_backwards(f):
    """
    find the timestamp and seek position of any locations
    in the file where the time index goes backwards.

    f: a file-like object supporting seek
    """
    _seek_to_start_of_data(f)

    line = f.readline()
    results = {"has_error": False}

    reader = csv.reader([line])
    line_as_csv = next(reader)
    prev_dt = parser.isoparse(line_as_csv[0])
    while line != "":
        if _is_header(line):
            # print(line)
            reader = csv.reader([line])
            line_as_csv = next(reader)
            dt = parser.isoparse(line_as_csv[0])
            if dt < prev_dt:
                # this is the first datetime with an error
                print("found error at", dt)
                results["has_error"] = True
                results["error_position"] = start_of_line
                results["last_good_dt"] = prev_dt
            prev_dt = dt

        start_of_line = (
            f.tell()
        )  # do this before reading, so that we can get a position
        # for the start of the line
        line = f.readline()

    return results


def _find_time_return_to_previous(f, threshold):
    """
    Given a datetime and a file-like object, start at
    the current stream position and find the first
    datetime in the stream that is greater than the
    datetime

    f: file-like object
    """
    start_of_line = f.tell()
    line = f.readline()

    reader = csv.reader([line])
    line_as_csv = next(reader)
    prev_dt = parser.isoparse(line_as_csv[0])
    while line != "":
        if _is_header(line):
            # print(line)
            reader = csv.reader([line])
            line_as_csv = next(reader)
            dt = parser.isoparse(line_as_csv[0])

            if dt > threshold:
                # return start_of_line, dt
                return {
                    "last_row_with_errors": (prev_start_of_line, prev_dt),
                    "first_row_without_errors": (start_of_line, dt),
                }

            prev_dt = dt

        # do this before reading, so that we can get a position
        # for the start of the line
        prev_start_of_line = start_of_line
        start_of_line = f.tell()

        line = f.readline()

    # the timestamps do not return to threshold in this file
    raise Exception("Timestamps do not return to previous level in file")


def _increment_timestamp(line, timedelta):
    """
    Add the timedelta to the timestamp in a line and return
    the new line
    """
    reader = csv.reader([line])
    line_as_csv = next(reader)
    dt = parser.isoparse(line_as_csv[0])
    dt += timedelta
    line_as_csv[0] = dt.isoformat().replace("+00:00", "Z")

    with io.StringIO("") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(line_as_csv)
        out = stream.getvalue()

    if DEBUG:
        print(
            f"{bytes(line, encoding='utf-8')} -> {bytes(out, encoding='utf-8')}"
        )  # TODO drop newlines?
    return out


# read through lines
# if line is bad
# generate an adjusted line
# write the (possibly adjusted) line to outfile
def _fix_errors(infile, outfile, start_of_bad, start_of_good, adjust):
    infile.seek(0)
    line = infile.readline()

    start_of_this_line = 0

    while line != "":
        if (start_of_this_line >= start_of_bad) and (
            start_of_this_line < start_of_good
        ):
            line = _increment_timestamp(line, adjust)

        outfile.write(line)

        start_of_this_line = infile.tell()
        line = infile.readline()

    print("Done")


def main(infilepath, outfilepath):
    """All the things"""

    with open(infilepath, "r") as infile:
        results = _find_time_delta_backwards(infile)

        if not results["has_error"]:
            raise Exception("Timestamp errors were expected but none" " were found")

        error_position = results["error_position"]

        infile.seek(error_position)

        results = _find_time_return_to_previous(infile, results["last_good_dt"])

        first_dt_without_errors = results["first_row_without_errors"][1]
        last_dt_with_errors = results["last_row_with_errors"][1]

        adjust = first_dt_without_errors - last_dt_with_errors - timedelta(seconds=1)

        with open(outfilepath, "w") as outfile:
            return _fix_errors(
                infile,
                outfile,
                error_position,
                results["first_row_without_errors"][0],
                adjust,
            )


def fix_and_write_back(infilepath):
    """Same as main, but write back to infile once done."""
    f = tempfile.NamedTemporaryFile(delete=False)
    fp = f.name
    f.close()  # we won't write to this object now, but save its path

    main(infilepath, fp)
    shutil.copy(fp, infilepath)

    os.remove(fp)
