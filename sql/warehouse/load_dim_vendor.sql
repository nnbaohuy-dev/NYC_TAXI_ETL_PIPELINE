INSERT INTO warehouse.dim_vendor
(
    vendor_id,
    vendor_name
)

VALUES
    (1, 'Creative Mobile Technologies, LLC'),
    (2, 'Curb Mobility, LLC'),
    (6, 'Myle Technologies Inc'),
    (7, 'Helix')

ON CONFLICT (vendor_id)
DO UPDATE SET
    vendor_name = EXCLUDED.vendor_name;
