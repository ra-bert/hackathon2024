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

def extract_text_equivs(root, namespace, include_break_line=False):
    """
    Extracts the text equivalents from a parsed XML root.
    
    Args:
        root (xml.etree.ElementTree.Element): Root of the parsed XML tree.
        namespace (str): Namespace URI to use in the XPath queries.
    
    Returns:
        str: Extracted text joined into a sentence.
    """
    count_lines = 0
    if root is None or not namespace:
        return ""
    
    ns = {'ns': namespace}  # Namespace dict for searching
  
    text_lines = []
    for text_line in root.findall('.//ns:TextLine', ns):
        # Find the direct child TextEquiv of the TextLine (ignore Word elements)
        text_equiv = text_line.find('./ns:TextEquiv/ns:Unicode', ns)
        if text_equiv is not None and text_equiv.text is not None:
            text_lines.append(text_equiv.text)

    # join text line and add \n for each line
    if text_lines and len(text_lines) > 1:
            if include_break_line:
                text_lines = '\n'.join(text_lines)
            else:
                # concatenate all text lines
                text_lines = ' '.join(text_lines)
    if not text_lines:
        return ""

    return text_lines

def extract_metadata_status(root, namespace):
    """
    Extracts the metadata status from a parsed XML root.
    
    Args:
        root (xml.etree.ElementTree.Element): Root of the parsed XML tree.
        namespace (str): Namespace URI to use in the XPath queries.
    
    Returns:
        str: Extracted metadata status.
    """
    if root is None or not namespace:
        return ""
    
    ns = {'ns': namespace}  # Namespace dict for searching

    metadata = root.find('.//ns:TranskribusMetadata', ns)
    status = metadata.get('status')
    if status is not None:
        return status
        
    return ' '.join(status)

def extract_info(xml_directory):
    # Create an empty DataFrame
    df = pd.DataFrame(columns=['file_path', 'filename', 'text'])
    
    # Get all XML files in the directory
    xml_files = get_all_xml_files(xml_directory)

    # Extract the text and status from each XML file
    data = []
    files_to_remove = ["mets.xml", "metadata.xml"]
    for file_path in xml_files:
        #print(os.path.basename(file_path))
        if os.path.basename(file_path) in files_to_remove:
            continue
        # Load the XML
        root = load_xml_file(file_path)

        # Get the namespace
        namespace = get_namespace(root)

        # Extract the text
        extracted_text = extract_text_equivs(root, namespace, include_break_line=True)

        # Extract the metadata status
        metadata_status = extract_metadata_status(root, namespace)
        
        # append to list
        data.append({'file_path': file_path, 'filename': os.path.basename(file_path), 'status':metadata_status, 'text': extracted_text})
    
    # convert list to dataframe
    df = pd.DataFrame(data)

    return df

# text into minimum of 50 words and include until next line break \n
# insert it in a new row in the dataframe

def split_into_chunks(df, word_len=100):
    df_new = pd.DataFrame(columns=['file_path', 'filename', 'row_idx', 'status', 'text'])
    chunks = []
    for idx, row in df.iterrows():
        text = row['text']
        if len(text) > word_len:
            text = text.split()
            row_idx = 0
            for i in range(0, len(text), word_len):
                chunks.append({'file_path': row['file_path'], 'filename': row['filename'], 'row_idx': row_idx, 'status': row['status'], 'text': ' '.join(text[i:i+word_len])})
                row_idx += 1
        else:
            chunks.append({'file_path': row['file_path'], 'filename': row['filename'], 'row_idx': 0, 'status': row['status'], 'text': text})
    df_new = pd.DataFrame(chunks)
    return df_new

if __name__ == "__main__":
    # Rein deer dataset
    xml_parent_directory = "pagexmls\page_export_job_9770194"

    df = extract_info(xml_parent_directory)
    df_chunk = split_into_chunks(df)
    df.to_csv('./data/text_extraction_pagexmls.csv', index=False)
    df_chunk.to_csv('./data/text_extraction_pagexmls_chunk.csv', index=False, encoding='utf-8')

    # Swedish dataset
    xml_parent_directory = "pagexmls\export_job_12164122"

    df = extract_info(xml_parent_directory)
    df_chunk = split_into_chunks(df)
    
    df.to_csv('./data/text_extraction_pagexmls_swedish.csv', index=False)
    df_chunk.to_csv('./data/text_extraction_pagexmls_swedish_chunk.csv', index=False)
