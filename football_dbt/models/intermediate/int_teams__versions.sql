{{ config(materialized='view') }}

with source as (
    select * from {{ ref("stg_api_football__teams") }}
),

hash_keys as (

    select
        *,
        {{ dbt_utils.generate_surrogate_key(['team_name', 'team_code', 'team_logo_url', 'venue_name', 'venue_city', 'venue_address', 'venue_surface', 'venue_capacity']) }} as row_hash 
    from source
),

with_previous as (

    select 
        *, 
        lag(row_hash) over (partition by team_id order by api_extracted_at, loaded_at) previous_hash
    from hash_keys  
),

with_changes as (
    select *
    from with_previous
    where previous_hash is null or previous_hash <> row_hash
),

versions as (
    select
        *,
        api_extracted_at                                   as valid_from,
        lead(api_extracted_at) over (
            partition by team_id
            order by api_extracted_at, loaded_at
        )                                                  as valid_to
    from with_changes
)

select 
    team_id, 
    team_name, 
    team_code, 
    team_country, 
    founded_year, 
    is_national, 
    team_logo_url, 
    venue_id, 
    venue_name, 
    venue_city, 
    venue_address, 
    venue_surface, 
    venue_capacity, 
    source_file,
    loaded_at as raw_loaded_at, 
    api_extracted_at, 
    valid_from,
    valid_to,
    valid_to is null  as is_current
from versions
