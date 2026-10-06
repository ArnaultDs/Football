{{
    config(
        materialized='incremental', 
        incremental_strategy='merge', 
        unique_key=['fixture_id', 'team_id'],
        merge_exclude_columns='inserted_at'
    )
}}

with source as (
    select * 
    from {{ref("int_fixtures__latest")}}
    {% if is_incremental() %}
    where updated_at > (select coalesce(max(int_updated_at), '1900-01-01') from {{ this }})
    {% endif %}
), 

unpivot as (

    select 
        fixture_id, 
        league_id, 
        season_year, 
        round_label, 
        round_number, 
        home_team_id as team_id, 
        home_team_name as team_name, 
        is_home_winner as is_winner, 
        home_goals as scored, 
        away_goals as conceded, 
        home_score_halftime as scored_halftime,
        away_score_halftime as conceded_halftime, 
        home_score_extratime as scored_extratime, 
        away_score_extratime as conceded_extratime,
        home_score_penalty as scored_penalty, 
        away_score_penalty as conceded_penalty, 
        is_finished,
        'home' as side,
        source_file, 
        raw_loaded_at, 
        api_extracted_at, 
        updated_at as int_updated_at
    from source 

    union all 

    select 
        fixture_id,
        league_id, 
        season_year, 
        round_label, 
        round_number, 
        away_team_id as team_id, 
        away_team_name as team_name, 
        is_away_winner as is_winner, 
        away_goals as scored, 
        home_goals as conceded, 
        away_score_halftime as scored_halftime,
        home_score_halftime as conceded_halftime, 
        away_score_extratime as scored_extratime, 
        home_score_extratime as conceded_extratime,
        away_score_penalty as scored_penalty, 
        home_score_penalty as conceded_penalty, 
        is_finished, 
        'away' as side, 
        source_file, 
        raw_loaded_at, 
        api_extracted_at, 
        updated_at as int_updated_at
    from source
)


select 
    *, 
    {{ current_timestamp() }} as inserted_at,
    {{ current_timestamp() }} as updated_at
from unpivot
where is_finished = 1
