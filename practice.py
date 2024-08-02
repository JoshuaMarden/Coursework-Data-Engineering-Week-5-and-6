import os
import xml.etree.ElementTree as ET
import config as c
import cProfile
import pstats

DATA_DIR =  c.DATA_DIR
PUBMED_FILE = c.PUBMED_FILE
SCRIPT_NAME = os.path.basename(__file__)


def open_file(file_path: str) -> str:
    """Opens a file, returns it as a string"""
    with open (file_path, "r",encoding="UTF-8") as file:
        return file.read()
    
def convert_string_to_element_tree(xml_str: str) -> ET:
    """Converts xml string an element tree"""
    return ET.fromstring(xml_str)

def get_info(root: ET.Element):
    """Extracts and prints the required information from the XML."""
    for article in root.findall("PubmedArticle"):
        title = article.findtext(".//ArticleTitle")
        year = article.findtext(".//PubDate/Year")
        pmid = article.findtext(".//PMID")
      
        # Extracting Keywords
        keywords = [kw.text for kw in article.findall(".//Keyword")]

        # Extracting MESH descriptor identifiers
        mesh_descriptors = [descriptor.attrib['UI'] for descriptor in article.findall(".//MeshHeading/DescriptorName") if descriptor.attrib['UI'].startswith('D')]

        # Print the extracted information
        print(f"Title: {title}")
        print(f"Year: {year}")
        print(f"PMID: {pmid}")
        print(f"Keywords: {keywords}")
        print(f"MESH Descriptors: {mesh_descriptors}")
        print("-" * 40)

def main(file_path):

    performance_logger = c.setup_logging(f"{DATA_DIR}/{SCRIPT_NAME}_performance")
    profiler = c.start_monitor()

    xml_content = open_file(file_path)
    root = convert_string_to_element_tree(xml_content)
    get_info(root)

    c.stop_monitor(SCRIPT_NAME, profiler, performance_logger)


if __name__ == "__main__":
    
    file_path = f"{DATA_DIR}/{PUBMED_FILE}"
    main(file_path)
    
