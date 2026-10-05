
with source as (

    select *
    from {{ source('raw', 'fixtures') }}
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

    -- fixtures
    (item -> 'fixture' ->> 'id')::bigint                                      as fixture_id, 
    (item -> 'fixture' ->> 'date')::timestamptz                               as kickoff_at,
    to_timestamp((item -> 'fixture' -> 'periods' ->> 'first')::bigint)        as first_half_started_at,
    to_timestamp((item -> 'fixture' -> 'periods' ->> 'second')::bigint)       as second_half_started_at,
    nullif(trim((item -> 'fixture' ->> 'referee')), '')                       as referee,
    item -> 'fixture' -> 'status' ->> 'short'                                 as status_code,
    item -> 'fixture' -> 'status' ->> 'long'                                  as status_label,
    (item -> 'fixture' -> 'status' ->> 'elapsed')::int                        as elapsed_time_min,
    (item -> 'fixture' -> 'status' ->> 'extra')::int                          as extra_time_min,

    -- venue
    (item -> 'fixture' -> 'venue' ->> 'id'):: bigint                          as venue_id, 
    nullif(trim((item -> 'fixture' -> 'venue' ->> 'name')), '')               as venue_name, 

     -- league
    (item -> 'league' ->> 'id')::bigint                                       as league_id, 
    nullif(trim((item -> 'league' ->> 'name')), '')                           as league_name, 
    (item -> 'league' ->> 'season')::smallint                                 as season_year, 
    trim(item -> 'league' ->> 'round')                                        as round_label, 
    substring(item -> 'league' ->> 'round' from '- (\d+)$')::smallint         as round_number,

    -- teams
    (item -> 'teams' -> 'home' ->> 'id')::bigint                              as home_team_id, 
    nullif(trim((item -> 'teams' -> 'home' ->> 'name')), '')                  as home_team_name, 
    (item -> 'teams' -> 'home' ->> 'winner')::boolean                         as is_home_winner,
    (item -> 'teams' -> 'away' ->> 'id')::bigint                              as away_team_id, 
    nullif(trim((item -> 'teams' -> 'away' ->> 'name')), '')                  as away_team_name, 
    (item -> 'teams' -> 'away' ->> 'winner')::boolean                         as is_away_winner, 

    -- goals
    (item -> 'goals' ->> 'home')::smallint                                    as home_goals,
    (item -> 'goals' ->> 'away')::smallint                                    as away_goals,
    (item -> 'score' -> 'halftime' ->> 'home')::smallint                      as home_score_halftime, 
    (item -> 'score' -> 'halftime' ->> 'away')::smallint                      as away_score_halftime, 
    (item -> 'score' -> 'fulltime' ->> 'home')::smallint                      as home_score_fulltime, 
    (item -> 'score' -> 'fulltime' ->> 'away')::smallint                      as away_score_fulltime, 
    (item -> 'score' -> 'extratime' ->> 'home')::smallint                     as home_score_extratime, 
    (item -> 'score' -> 'extratime' ->> 'away')::smallint                     as away_score_extratime, 
    (item -> 'score' -> 'penalty' ->> 'home')::smallint                       as home_score_penalty, 
    (item -> 'score' -> 'penalty' ->> 'away')::smallint                       as away_score_penalty,
   
    -- context
    extract_param_league,
    extract_param_season,

    -- lineage
    source_file, 
    loaded_at,
    api_extracted_at
from flattened as f


