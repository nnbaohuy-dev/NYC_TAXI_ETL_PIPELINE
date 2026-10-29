INSERT INTO warehouse.dim_payment_type
(
    payment_type_id,
    payment_type_name
)

VALUES
    (0, 'Flex Fare trip'),
    (1, 'Credit card'),
    (2, 'Cash'),
    (3, 'No charge'),
    (4, 'Dispute'),
    (5, 'Unknown'),
    (6, 'Voided trip')

ON CONFLICT (payment_type_id)
DO UPDATE SET
    payment_type_name = EXCLUDED.payment_type_name;