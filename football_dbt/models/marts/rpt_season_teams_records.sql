
with standing as (
    select 
        s.*
    from {{ref("rpt_standings_per_round")}} s
    left join {{ref("dim_league_seasons")}} as ls
        on s.league_season_hash = ls.league_season_hash
    where 1=1
    and is_last_round = 1
    and ls.is_current = true
), 

matches as (
    select 
        s.*
    from {{ref("fact_team_matches")}} s
    left join {{ref("dim_league_seasons")}} as ls
        on s.league_season_hash = ls.league_season_hash
    where 1=1
    and ls.is_current = true
),

home_stats as (

    select
        league_season_hash,
        team_id,
        count(*)                                  as home_played,
        count(*) filter (where result = 'W')      as home_won,
        sum(points)                               as home_points,
        sum(scored)                               as home_scored,
        sum(conceded)                             as home_conceded
    from matches
    where side = 'home'
    group by league_season_hash, team_id

),

away_stats as (
    select
        league_season_hash,
        team_id,
        count(*)                                  as away_played,
        count(*) filter (where result = 'W')      as away_won,
        sum(points)                               as away_points,
        sum(scored)                               as away_scored,
        sum(conceded)                             as away_conceded
    from matches
    where side = 'away'
    group by league_season_hash, team_id
),


candidates as (
    select 
        league_season_hash, 1 as record_order, 'Meilleure attaque' as record_label, 
        team_id, scored as record_value,
        rank() over(PARTITION by league_season_hash order by scored desc, diff desc) rnk
    from standing

    UNION ALL

    select 
        league_season_hash, 2 as record_order, 'Meilleure défense' as record_label, 
        team_id, conceded as record_value,
        rank() over(PARTITION by league_season_hash order by conceded asc, diff desc) rnk
    from standing

    UNION ALL

    select 
        league_season_hash, 3 as record_order, 'Plus de victoire à domicile' as record_label, 
        team_id, home_won as record_value,
        rank() over(
            partition by league_season_hash
            order by home_points::numeric / home_played desc,
                     home_scored - home_conceded desc,
                     home_scored desc
        )
    from home_stats

    UNION ALL

    select 
        league_season_hash, 4 as record_order, 'Plus de victoire à exterieur' as record_label, 
        team_id, away_won as record_value,
        rank() over(
            partition by league_season_hash
            order by away_points::numeric / away_played desc,
                     away_scored - away_conceded desc,
                     away_scored desc
        )
    from away_stats
)

select *
from candidates
where rnk = 1

