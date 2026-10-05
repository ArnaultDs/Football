
-- One row per team per payload (no dedups)


with source as (

    select *
    from {{ source('raw', 'teams') }}
), 

flattened as (

    select 
        s.source_file, 
        s.loaded_at,
        s.api_extracted_at, 
        (s.payload -> 'parameters' ->> 'league') as extract_param_league,
        (s.payload -> 'parameters' ->> 'season') as extract_param_season, 
        r.item
    from source as s
    cross join lateral jsonb_array_elements(s.payload -> 'response') as r(item)

)

select 

    -- teams
    (item -> 'team' ->> 'id')::bigint                           as team_id,
    nullif(trim((item -> 'team' ->> 'name')), '')               as team_name, 
    nullif(trim((item -> 'team' ->> 'code')), '')               as team_code, 
    nullif(trim((item -> 'team' ->> 'country')), '')            as team_country,
    (item -> 'team' ->> 'founded')::smallint                    as founded_year,
    (item -> 'team' ->> 'national')::boolean                    as is_national,
    item -> 'team' ->> 'logo'                                   as team_logo_url,

    -- venues
   (item -> 'venue' ->> 'id')::bigint                           as venue_id,
    nullif(trim(item -> 'venue' ->> 'name'), '')                as venue_name,
    nullif(trim(item -> 'venue' ->> 'city'), '')                as venue_city,
    nullif(trim(item -> 'venue' ->> 'address'), '')             as venue_address,
    nullif(trim(item -> 'venue' ->> 'surface'), '')             as venue_surface,
    (item -> 'venue' ->> 'capacity')::int                       as venue_capacity,

    -- context
    extract_param_league, 
    extract_param_season,

    -- lineage
    source_file, 
    loaded_at, 
    api_extracted_at
from flattened