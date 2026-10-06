with source as (

    select *
    from {{ source('raw', 'leagues') }}
), 

flattened as (

    select 
        s.source_file, 
        s.loaded_at,
        s.api_extracted_at, 
        (s.payload -> 'parameters' ->> 'league') as extract_param_league,
        (s.payload -> 'parameters' ->> 'season') as extract_param_season, 
        l.league_block,
        se.season_block
    from source as s
    cross join lateral jsonb_array_elements(s.payload -> 'response') as l(league_block)
    cross join lateral jsonb_array_elements(l.league_block -> 'seasons') as se(season_block)
)


select 
    -- league
    (league_block -> 'league' ->> 'id')::bigint                 as league_id, 
    nullif(trim((league_block -> 'league' ->> 'name')), '')     as league_name, 
    league_block -> 'league' ->> 'type'                         as league_type, 
    league_block -> 'league' ->> 'logo'                         as league_logo_url, 


    -- country
    nullif(trim((league_block -> 'country' ->> 'name')), '')    as country_name, 
    league_block -> 'country' ->> 'code'                        as country_code, 
    league_block -> 'country' ->> 'flag'                        as country_flag, 

    -- season
    (season_block ->> 'year')::smallint                         as  season_year,
    (season_block ->> 'start')::date                            as  season_start, 
    (season_block ->> 'end')::date                              as  season_end, 
    (season_block ->> 'current')::boolean                       as  is_current, 

    -- context
    extract_param_league, 
    extract_param_season,

    -- lineage
    source_file, 
    loaded_at,
    api_extracted_at
from flattened as f
