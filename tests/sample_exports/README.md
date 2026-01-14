Paste real export strings into this folder for validation.

Guidelines:
- Use one file per export string.
- Use a `.txt` extension.
- Either:
  - Include a header line like `contract=MIN` or `contract=FULL` as the first non-empty line, or
  - Put `min` or `full` in the filename (case-insensitive).
- The export string should be the next non-empty, non-comment line after the optional header.

Example file:
```
contract=MIN
ver=OVC_MIN_V0_1|profile=MIN|schema_min=OVC_MIN_V0_1|...
```
