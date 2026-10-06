
with source as (
    select * from {{ ref("int_leagues__latest")}}
)

select 
    
    league_id, 
    league_name,
    league_type,
    league_logo_url, 
    country_name, 
    country_code, 
    country_flag, 
    {{ current_timestamp() }} as inserted_at,
    {{ current_timestamp() }} as updated_at
from source