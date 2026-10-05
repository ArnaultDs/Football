with source as (

    select * 
    from {{ source('raw', 'fixtures_players') }}

),

flattened as (

    select
        s.source_file,
        s.loaded_at,
        s.api_extracted_at,
        (s.payload -> 'parameters' ->> 'fixture')::bigint  as fixture_id,
        t.team_block,
        p.player_block,
        st.stat
    from source s
    cross join lateral jsonb_array_elements(s.payload -> 'response')        as t(team_block)
    cross join lateral jsonb_array_elements(t.team_block -> 'players')      as p(player_block)
    left  join lateral jsonb_array_elements(p.player_block -> 'statistics') as st(stat) on true

)

select
    fixture_id,

    -- team
    (team_block -> 'team' ->> 'id')::bigint                  as team_id,
    nullif(trim(team_block -> 'team' ->> 'name'), '')        as team_name,

    -- player
    (player_block -> 'player' ->> 'id')::bigint              as player_id,
    nullif(trim(player_block -> 'player' ->> 'name'), '')    as player_name,
    player_block -> 'player' ->> 'photo'                     as player_photo_url,

    -- game
    (stat -> 'games' ->> 'minutes')::smallint                as minutes_played,
    (stat -> 'games' ->> 'number')::smallint                 as shirt_number,
    stat -> 'games' ->> 'position'                           as position_code,
    (stat -> 'games' ->> 'rating')::numeric(3,1)             as rating,
    (stat -> 'games' ->> 'captain')::boolean                 as is_captain,
    (stat -> 'games' ->> 'substitute')::boolean              as is_substitute,

    -- attack
    (stat ->> 'offsides')::smallint                          as offsides,
    (stat -> 'shots' ->> 'total')::smallint                  as shots_total,
    (stat -> 'shots' ->> 'on')::smallint                     as shots_on_target,
    (stat -> 'goals' ->> 'total')::smallint                  as goals,
    (stat -> 'goals' ->> 'assists')::smallint                as assists,

    -- goalkeeping
    (stat -> 'goals' ->> 'conceded')::smallint               as goals_conceded,
    (stat -> 'goals' ->> 'saves')::smallint                  as saves,

    -- passing
    (stat -> 'passes' ->> 'total')::smallint                 as passes_total,
    (stat -> 'passes' ->> 'key')::smallint                   as passes_key,
    (stat -> 'passes' ->> 'accuracy')::smallint              as passes_accurate,

    -- defending
    (stat -> 'tackles' ->> 'total')::smallint                as tackles_total,
    (stat -> 'tackles' ->> 'blocks')::smallint               as blocks,
    (stat -> 'tackles' ->> 'interceptions')::smallint        as interceptions,
    (stat -> 'duels' ->> 'total')::smallint                  as duels_total,
    (stat -> 'duels' ->> 'won')::smallint                    as duels_won,

    -- dribbles
    (stat -> 'dribbles' ->> 'attempts')::smallint            as dribbles_attempted,
    (stat -> 'dribbles' ->> 'success')::smallint             as dribbles_successful,
    (stat -> 'dribbles' ->> 'past')::smallint                as dribbled_past,

    -- discipline
    (stat -> 'fouls' ->> 'drawn')::smallint                  as fouls_drawn,
    (stat -> 'fouls' ->> 'committed')::smallint              as fouls_committed,
    (stat -> 'cards' ->> 'yellow')::smallint                 as yellow_cards,
    (stat -> 'cards' ->> 'red')::smallint                    as red_cards,

    -- penalties
    (stat -> 'penalty' ->> 'won')::smallint                  as penalties_won,
    (stat -> 'penalty' ->> 'commited')::smallint             as penalties_committed,
    (stat -> 'penalty' ->> 'scored')::smallint               as penalties_scored,
    (stat -> 'penalty' ->> 'missed')::smallint               as penalties_missed,
    (stat -> 'penalty' ->> 'saved')::smallint                as penalties_saved,

    -- lineage
    source_file,
    api_extracted_at,
    loaded_at

from flattened