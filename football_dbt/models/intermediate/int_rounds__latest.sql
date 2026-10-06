{{
    config(
        incremental_strategy='merge', 
        unique_key='round_id',
        merge_exclude_columns='inserted_at'
    )
}}

with dedup as (

    select *, row_number() over(partition by item order by api_extracted_at desc, loaded_at desc) rn
    from {{ ref('stg_api_football__rounds') }}
)


select 
    extract_param_league as league_id,
    extract_param_season as season_year,
    cast(item as text) as round_label,
    substring(item from '- (\d+)$')::smallint as round_number,
    source_file,
    loaded_at as raw_loaded_at,
    api_extracted_at,
    {{ current_timestamp() }} as inserted_at,
    {{ current_timestamp() }} as updated_at
from dedup
where rn = 1
