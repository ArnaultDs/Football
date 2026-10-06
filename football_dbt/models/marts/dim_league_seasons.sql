with source as (
    select * from {{ ref("int_leagues__latest")}}
)


select 
    {{ dbt_utils.generate_surrogate_key(['league_id', 'season_year']) }} as league_season_hash, 
    league_id, 
    season_year as season_id,
    season_start, 
    season_end,
    is_current,
    {{ current_timestamp() }} as inserted_at,
    {{ current_timestamp() }} as updated_at
from source
