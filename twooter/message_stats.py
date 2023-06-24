"""Function for querying message stats

This requires grouping on the "year" part of the message timestamp, which isn't
super clean to achieve in Tortoise. To prevent excessive low-level imports in
the db module, this function got its own module.
"""


from collections import defaultdict

from pypika import CustomFunction
from tortoise.functions import Count, Function

import twooter.db


class ExtractYear(Function):
    """Custom Tortoise function for extracting a subfield from a value

    This is required to achieve grouping by the "year" subfield of a datetime value.

    Lifted from this comment on GitHub:

        https://github.com/tortoise/tortoise-orm/issues/608#issuecomment-758358476
    """

    database_func = CustomFunction("YEAR", ["name"])


MessageStats = dict[str, dict[str, int]]  # year -> tag -> twoot count


async def query_stats(start_year: int, end_year: int) -> MessageStats:
    """Returns message statistics grouped by year and tag

    start_year and end_year are both inclusive.
    """

    assert end_year >= start_year, "end year must be higher than or equal to start year"

    raw_stats = (
        await twooter.db.Message.annotate(
            year=ExtractYear("timestamp"),
            count=Count("id"),
        )
        .group_by("year", "tag")
        .filter(year__gte=start_year, year__lte=end_year)
        .values("year", "tag", "count")
    )

    # Formatting the result as a nested dict makes it much, much more readable
    stats = defaultdict(dict)

    for row in raw_stats:
        stats[str(row["year"])][row["tag"]] = row["count"]

    return dict(stats)
