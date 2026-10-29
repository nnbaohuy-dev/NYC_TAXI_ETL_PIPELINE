INSERT INTO warehouse.dim_rate_code
(
    ratecode_id,
    ratecode_name
)

VALUES
    (1, 'Standard rate'),
    (2, 'JFK'),
    (3, 'Newark'),
    (4, 'Nassau or Westchester'),
    (5, 'Negotiated fare'),
    (6, 'Group ride'),  
    (99, 'Null/unknow')

ON CONFLICT (ratecode_id)
DO UPDATE SET
    ratecode_name = EXCLUDED.ratecode_name;