import xml.etree.ElementTree as ET
import os
import pandas as pd

def get_all_xml_files(directory):
    """
    Get all XML files in a directory.
    
    Args:
        directory (str): Directory path.
    
    Returns:
        list: List of XML file paths.
    """
    xml_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    return xml_files

def get_namespace(element):
    """
    Extracts the namespace from an XML element tag.
    
    Args:
        element (xml.etree.ElementTree.Element): The root XML element.
    
    Returns:
        str: The namespace URI, or an empty string if no namespace is present.
    """
    # The element tag might look like '{namespace}tagname', so we split it
    if '}' in element.tag:
        return element.tag.split('}')[0].strip('{')
    return ''

def load_xml_file(file_path):
    """
    Loads and parses an XML file.
    
    Args:
        file_path (str): Path to the XML file.
    
    Returns:
        xml.etree.ElementTree.Element: Root of the parsed XML tree.
    """
    try:
        tree = ET.parse(file_path)
        return tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None

def extract_text_equivs(root, namespace):
    """
    Extracts the text equivalents from a parsed XML root.
    
    Args:
        root (xml.etree.ElementTree.Element): Root of the parsed XML tree.
        namespace (str): Namespace URI to use in the XPath queries.
    
    Returns:
        str: Extracted text joined into a sentence.
    """
    if root is None or not namespace:
        return ""
    
    ns = {'ns': namespace}  # Namespace dict for searching
    text_equivs = []
    for word in root.findall('.//ns:Word', ns):
        unicode_elem = word.find('.//ns:Unicode', ns)
        if unicode_elem is not None:
            text_equivs.append(unicode_elem.text)
    
    return ' '.join(text_equivs)

def main(xml_directory):
    xml_directory = "pagexmls\page_export_job_9770194"
    df = pd.DataFrame(columns=['file_path', 'filename', 'text'])
    
    xml_files = get_all_xml_files(xml_directory)
    data = []
    files_to_remove = ["mets.xml", "metadata.xml"]
    for file_path in xml_files:
        if os.path.basename(file_path) in files_to_remove:
            continue
        # Load the XML
        root = load_xml_file(file_path)

        # Get the namespace
        namespace = get_namespace(root)

        # Extract the text
        extracted_text = extract_text_equivs(root, namespace)
        
        # append to list
        data.append({'file_path': file_path, 'filename': os.path.basename(file_path), 'text': extracted_text})
    
    # convert list to dataframe
    df = pd.DataFrame(data)

    return df

if __name__ == "__main__":
    # Example usage:
    xml_parent_directory = r"C:\Users\B294422\Desktop\hackathon2024\pagexmls\page_export_job_9770194"
    
    df = main(xml_parent_directory)

    df.to_csv('./data/text_extraction_pagexmls.csv', index=False)


        