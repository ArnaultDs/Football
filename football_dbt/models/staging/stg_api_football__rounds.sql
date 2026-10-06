with source as (

    select *
    from {{ source('raw', 'fixtures_rounds') }}
), 

flattened as (

    select 
        s.source_file, 
        s.loaded_at,
        s.api_extracted_at, 
        (s.payload -> 'parameters' ->> 'league') as extract_param_league,
        (s.payload -> 'parameters' ->> 'season') as extract_param_season, 
        r.item
    from source as s
    cross join lateral jsonb_array_elements_text(s.payload -> 'response') as r(item)

)

select * from flattened
