{{
    config(
        materialized='incremental', 
        incremental_strategy='merge', 
        unique_key='fixture_id',
        merge_exclude_columns='inserted_at'
    )
}}

with source as (
    select * 
    from {{ref("int_fixtures__latest")}}
    {% if is_incremental() %}
    where updated_at > (select coalesce(max(int_loaded_at), '1900-01-01') from {{this}})
    {% endif %}
)

select 
    {{ dbt_utils.generate_surrogate_key(['league_id', 'season_year']) }} as league_season_hash,
    fixture_id,
    kickoff_at,
    first_half_started_at,
    second_half_started_at,
    referee,
    status_code,
    status_label,
    elapsed_time_min,
    extra_time_min,
    venue_id,
    venue_name,
    league_id,
    league_name,
    season_year,
    round_label,
    round_number,
    home_team_id,
    home_team_name,
    is_home_winner,
    away_team_id,
    away_team_name,
    is_away_winner,
    home_goals,
    away_goals,
    home_score_halftime,
    away_score_halftime,
    home_score_fulltime,
    away_score_fulltime,
    home_score_extratime,
    away_score_extratime,
    home_score_penalty,
    away_score_penalty,
    extract_param_league,
    extract_param_season,
    source_file,
    updated_at as int_loaded_at,
    api_extracted_at,
    {{ current_timestamp() }} as inserted_at,
    {{ current_timestamp() }} as updated_at
from source as b



