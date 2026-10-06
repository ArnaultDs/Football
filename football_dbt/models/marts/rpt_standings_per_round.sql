with source as (

    select * from {{ ref('fact_team_matches')}}
),

grouped_teams as (

    select 
        s.league_season_hash,
        team_id,
        round_number,
        count(*) over w as played, 
        count(*) filter(where result = 'W') over w as won,
        count(*) filter(where result = 'D') over w as draw,
        count(*) filter(where result = 'L') over w as lost,
        string_agg(result, ' ') over w as form,
        sum(scored) over w as scored, 
        sum(conceded) over w as conceded,
        sum(scored - conceded) over w as diff,
        sum(points) over w as points
    from source as s
    left join {{ref("dim_league_seasons")}} as ls
        on s.league_season_hash = ls.league_season_hash
    where ls.is_current = true
    window w as (
        partition by s.league_season_hash, team_id 
        order by round_number
        rows between unbounded preceding and current row
    )
),

max_round as (
    select max(round_number) as max_round_number
    from source
)

select 
    league_season_hash,
    team_id, 
    round_number,
    played, 
    won, 
    draw, 
    lost, 
    scored, 
    conceded, 
    diff, 
    points,
    form,
    split_part(form, ' ', 1) as form1,
    split_part(form, ' ', 2) as form2,
    split_part(form, ' ', 3) as form3,
    split_part(form, ' ', 4) as form4,
    split_part(form, ' ', 5) as form5,
    case 
        when mr.max_round_number is not null then 1
        else 0 
    end is_last_round,
    rank() over(partition by league_season_hash, round_number order by points desc, diff desc) team_rank
from grouped_teams  gt
left join max_round mr
    on gt.round_number = mr.max_round_number