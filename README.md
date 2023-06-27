# gopreprocess

This repo holds parsing and GPAD generation code for generating automatic annotations based on orthology, or based on upstream products from GOA, etc.

# human example

```bash
 poetry run convert_annotations --namespaces 'HUMAN','UniProtKB' --target_taxon NCBITaxon:10090 --source_taxon NCBITaxon:9606 --ortho_reference GO_REF:0000096 
```

# rat example, uses cli defaults 
```bash 
poetry run convert_annotations
```