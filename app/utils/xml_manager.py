"""
File: app/utils/xml_manager.py
Description: Efficient XML processing for PLCopen projects.
Focuses on extracting relevant Code blocks (ST) and Variable declarations
to provide context for AI diagnostics.
"""

# Standard Library Imports
from typing import Optional

from loguru import logger

# Third-Party Imports
from lxml import etree


class XMLContextExtractor:
    """
    Handles granular extraction of PLC project components from XML.
    """

    def __init__(self, xml_content: str):
        """
        Parses the XML content into a searchable tree.
        """
        try:
            # PLCopen XMLs can have namespaces; we handle them to ensure XPath works
            self.tree = etree.fromstring(xml_content.encode("utf-8"))
            self.ns = {"ns": "http://www.plcopen.org/xml/tc6_0201"}
        except Exception as e:
            logger.error(f"Failed to parse PLC XML: {e}")
            raise ValueError("Invalid PLC XML project format.")

    def get_pou_context(self, pou_name: str = "program0") -> str:
        """
        Extracts the full definition of a POU (Program Organizational Unit).
        This includes both the variable interface and the logic body.
        """
        # XPath searches for the POU by name
        query = f"//ns:pou[@name='{pou_name}']"
        pou_element = self.tree.xpath(query, namespaces=self.ns)

        if pou_element:
            # We return the raw XML of just this POU to provide focused context
            context = etree.tostring(
                pou_element[0], pretty_print=True, encoding="unicode"
            )
            logger.info(f"Context extracted for POU: {pou_name}")
            return context

        return "Context not found for the specified POU."
