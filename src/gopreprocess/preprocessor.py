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
    rgd_annotations = GafProcessor(rat_genes, rgd_gaf_path, namespaces=namespaces).convertable_annotations
    rat_gene_set = set(rat_genes.keys())
    for annotation in rgd_annotations:
        print(annotation)
        if annotation.subject.id in rat_gene_set:
            print("True")


if __name__ == '__main__':
    preprocess()
