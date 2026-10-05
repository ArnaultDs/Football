with sources as (

    select * from {{ ref('fact_team_matches')}} where is_finished = 1
),

grouped_teams as (

    select 
        team_id,
        count(*) as played, 
        sum(case when result = 'W' then 1 else 0 end) as won,
        sum(case when result = 'D' then 1 else 0 end) as drawn, 
        sum(case when result = 'L' then 1 else 0 end) as lost,
        string_agg(result, ' ' order by round_number desc) as form,
        sum(scored) as scored, 
        sum(conceded) as conceded,
        sum(scored - conceded) as diff,
        sum(points) as points
    from sources
    group by team_id
)

select 
    team_id, 
    played, 
    won, 
    drawn, 
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
    rank() over(order by points desc, diff desc) team_rank
from grouped_teams 