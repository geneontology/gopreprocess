from src.processors.orthoprocessor import OrthoProcessor
from src.processors.gafprocessor import GafProcessor
from src.processors.gpiprocessor import GpiProcessor
from src.utils.download import download_files

namespaces = ["RGD", "UniProtKB"]
mouse_taxon = "NCBITaxon:10090"
rat_taxon = "NCBITaxon:10116"
human_taxon = "NCBITaxon:9606"


def preprocess():
    ortho_path, rgd_gaf_path, mgi_gpi_path = download_files()
    mouse_genes = GpiProcessor(mgi_gpi_path).genes
    rat_genes = OrthoProcessor(mouse_genes, ortho_path, mouse_taxon, rat_taxon).genes
    for k, v in rat_genes.items():  # exclude any rat genes whose orthologs are not in the mouse GPI file.
        if v not in mouse_genes:
            del rat_genes[k]
    rgd_annotations = GafProcessor(rat_genes, rgd_gaf_path, namespaces=namespaces).convertable_annotations
    rat_gene_set = set(rat_genes.keys())
    print(list(rat_gene_set)[0])
    print(list(rat_gene_set)[1])
    for annotation in rgd_annotations:
        print(annotation.subject.id)
        if annotation.subject.id in rat_gene_set:
            print("True")


if __name__ == '__main__':
    preprocess()
