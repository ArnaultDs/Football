{{
    config(
        materialized='incremental', 
        incremental_strategy='merge', 
        unique_key=['fixture_id', 'team_id'],
        merge_exclude_columns='inserted_at',
    )
}}


with source as (
    select * 
    from {{ ref("int_team_matches__unpivoted") }}
    {% if is_incremental() %}
    where updated_at > (select coalesce(max(int_updated_at), '1900-01-01') from {{ this }})
    {% endif %}

)


select 
    {{ dbt_utils.generate_surrogate_key(['league_id', 'season_year']) }} as league_season_hash,
    league_id, 
    season_year, 
    fixture_id,
    round_number,
    team_id, 
    team_name,
    is_winner,
    scored,
    conceded,
    case 
        when scored > conceded then 'W'
        when scored = conceded then 'D'
        else 'L'
    end as result,
    case
        when scored > conceded then 3
        when scored = conceded then 1
        else 0
    end as points,
    case 
        when scored > conceded then 
            case 
                when side = 'home' then 'home_victory'
                when side = 'away' then 'away_victory'
            end
        when scored = conceded then 'draw'
        else NULL
    end as match_outcomes,
    is_finished, 
    side, 
    updated_at as int_updated_at, 
    {{ current_timestamp() }} as inserted_at,
    {{ current_timestamp() }} as updated_at
from source
