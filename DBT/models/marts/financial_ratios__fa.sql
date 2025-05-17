select
    symbol,
    year,
    pe,
    eps
from {{ source('raw_layer', 'ratios') }}