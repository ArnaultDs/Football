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
    from {{ ref("int_fixtures__latest") }}
    {% if is_incremental() %}
    where updated_at > (select coalesce(max(int_updated_at), '1900-01-01') from {{ this }})
    {% endif %}
), 

sides as (
    select 
        fixture_id,
        round_number,
        status_code,
        home_team_id as team_id, 
        home_team_name as team_name,
        is_home_winner as is_winner,
        home_goals as scored,
        away_goals as conceded,
        'home' as side,
        updated_at
    from source

    union all 
    select 
        fixture_id,
        round_number,
        status_code,
        away_team_id as team_id, 
        away_team_name as team_name,
        is_away_winner as is_winner,
        away_goals as scored,
        home_goals as conceded,
        'away' as side,
        updated_at
    from source
), 

finished as (

    select 
        *, 
        case 
            when status_code in ('FT', 'AET', 'PEN') THEN 1
            else 0 
        end as is_finished
    from sides
)


select 
    fixture_id,
    round_number,
    team_id, 
    team_name,
    is_winner,
    scored,
    conceded,
    case 
        when is_finished = 1 THEN 
            case 
                when scored > conceded then 'W'
                when scored = conceded then 'D'
                else 'L'
            end 
    end as result,
    case 
        when is_finished = 1 THEN
            case
                when scored > conceded then 3
                when scored = conceded then 1
                else 0
            end
        else null
    end as points,
    case 
        when is_finished=1 and scored > conceded then 
            case 
                when side = 'home' then 'home_victory'
                when side = 'away' then 'away_victory'
            end
        when is_finished=1 and scored = conceded then 'draw'
        else NULL
    end as match_outcomes,
    is_finished, 
    side, 
    updated_at as int_updated_at, 
    {{ current_timestamp() }} as inserted_at,
    {{ current_timestamp() }} as updated_at
from finished
