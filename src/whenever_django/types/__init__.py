from typing import TypeAlias

import whenever

WheneverType: TypeAlias = (
    whenever.Instant
    | whenever.PlainDateTime
    | whenever.Date
    | whenever.Time
    | whenever.ZonedDateTime
    | whenever.OffsetDateTime
    | whenever.YearMonth
    | whenever.MonthDay
    | whenever.TimeDelta
    | whenever.ItemizedDelta
    | whenever.ItemizedDateDelta
)

NullableWheneverType: TypeAlias = WheneverType | None

WheneverTypeClass: TypeAlias = (
    type[whenever.Instant]
    | type[whenever.PlainDateTime]
    | type[whenever.Date]
    | type[whenever.Time]
    | type[whenever.ZonedDateTime]
    | type[whenever.OffsetDateTime]
    | type[whenever.YearMonth]
    | type[whenever.MonthDay]
    | type[whenever.TimeDelta]
    | type[whenever.ItemizedDelta]
    | type[whenever.ItemizedDateDelta]
)
