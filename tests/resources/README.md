To generate a subset of ontology terms to use in the tests:

```bash
robot extract --method BOT --input go.owl --term GO:0051179 --output localization.owl
```

```bash
robot convert --input localization.owl --output localization.json --format json
```

mv resulting localization.json to tests/resources/localization.json

```bash
mv localization.json ../resources/localization.json
```