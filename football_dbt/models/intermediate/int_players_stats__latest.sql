{{
    config(
        materialized='incremental', 
        incremental_strategy='merge', 
        unique_key=['fixture_id', 'player_id'],
        merge_exclude_columns='inserted_at'


    )
}}

with source as (
    select *
    from {{ ref('stg_api_football__players_stats') }}
    {% if is_incremental() %}
    where loaded_at > (select coalesce(max(raw_loaded_at), '1900-01-01') from {{ this }})
    {% endif %}
),

dedup as (

    select *, row_number() over(partition by fixture_id, player_id order by api_extracted_at desc, loaded_at desc) rn
    from source
),

latest_in_batch as (

    select * from dedup where rn = 1
)

select 
    fixture_id,
    team_id,
    team_name,
    player_id,
    player_name,
    player_photo_url,
    minutes_played,
    shirt_number,
    position_code,
    rating,
    is_captain,
    is_substitute,
    offsides,
    shots_total,
    shots_on_target,
    goals,
    assists,
    goals_conceded,
    saves,
    passes_total,
    passes_key,
    passes_accurate,
    tackles_total,
    blocks,
    interceptions,
    duels_total,
    duels_won,
    dribbles_attempted,
    dribbles_successful,
    dribbled_past,
    fouls_drawn,
    fouls_committed,
    yellow_cards,
    red_cards,
    penalties_won,
    penalties_committed,
    penalties_scored,
    penalties_missed,
    penalties_saved,
    source_file,
    loaded_at as raw_loaded_at,
    api_extracted_at,
    {{ current_timestamp() }} as inserted_at,
    {{ current_timestamp() }} as updated_at
from latest_in_batch as b
{% if is_incremental() %}
where exists(
    select 1
    from {{ this }} as t
    where t.fixture_id = b.fixture_id
        and t.player_id = b.player_id
        and t.api_extracted_at > b.api_extracted_at
)
{% endif %}
