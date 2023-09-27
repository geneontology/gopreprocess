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

# run diff code to compare with an existing file
```bash
poetry run compare -file1 file_path -file2 file_path -o file_output_prefix
```
By default, this will compare subject_id (gene or gene product id), object_id (go term id), and evidence_code between the two files 
reporting the matching associations, the associations unique to file1 and those unique to file2.
