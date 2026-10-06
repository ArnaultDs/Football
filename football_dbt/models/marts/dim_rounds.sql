
with source as (
    select * from {{ ref("int_rounds__latest")}}
)

select 
    {{ dbt_utils.generate_surrogate_key(['league_id', 'season_year']) }} as league_season_hash, 
    league_id, 
    season_year, 
    round_label,
    round_number,
    {{ current_timestamp() }} as inserted_at,
    {{ current_timestamp() }} as updated_at
from source
