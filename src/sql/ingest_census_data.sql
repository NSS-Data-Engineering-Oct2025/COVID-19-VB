MERGE INTO {FINAL_TABLE} AS target
USING {STAGE_TABLE} AS source
ON target.name = source.name
   AND target.state = source.state

WHEN MATCHED THEN UPDATE SET
name = source.name,
state = source.state,
B01003_001E = source.B01003_001E

WHEN NOT MATCHED THEN INSERT (
    name,
    state, 
    B01003_001E

) VALUES (
 source.name,
 source.state,
    source.B01003_001E
);