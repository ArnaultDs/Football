{{
    config(
        materialized='incremental', 
        incremental_strategy='merge', 
        unique_key=['team_id'],
        merge_exclude_columns='inserted_at'
    )
}}

with source as (

    select * 
    from {{ref('int_teams__versions')}}
    {% if is_incremental() %}
    where raw_loaded_at > (select coalesce(max(raw_loaded_at), '1900-01-01') from {{ this }})
    {% endif %}
),

filter_version as (

    select *
    from source 
    where is_current = true
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
    raw_loaded_at,
    {{ current_timestamp() }} as inserted_at,
    {{ current_timestamp() }} as updated_at
from filter_version