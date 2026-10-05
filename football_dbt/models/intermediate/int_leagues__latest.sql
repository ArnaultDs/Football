{{
    config(
        incremental_strategy='merge', 
        unique_key=['league_id', 'season_year'],
        merge_exclude_columns='inserted_at'
    )
}}

with dedup as (

    select *, row_number() over(partition by league_id, season_year order by api_extracted_at desc, loaded_at desc) rn
    from {{ ref('stg_api_football__leagues') }}
)

select 
    league_id,
    league_name,
    league_type,
    league_logo_url,
    country_name,
    country_code,
    country_flag,
    season_year,
    season_start,
    season_end,
    is_current,
    extract_param_league,
    extract_param_season,
    source_file,
    loaded_at as raw_loaded_at,
    api_extracted_at,
    {{ current_timestamp() }} as inserted_at,
    {{ current_timestamp() }} as updated_at
from dedup
where rn = 1
