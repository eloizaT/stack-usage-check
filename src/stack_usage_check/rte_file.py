import re

from dataclasses import dataclass
from pathlib import Path

# TODO: Consider using arxml-library instead
import xml.etree.ElementTree as ET


@dataclass
class RteEvent:
    """ Class that represents stack allocation data variables within a map file """
    event: str
    container: str = None


class RunTimeEnvFile:
    @staticmethod
    def get_step_timing_event_ref_list(rte_arxml_file: Path):
        """ Parse timing-event mappings from an RTE ARXML file.

        The Rte.arxml file is an AUTOSAR file that contains the RTE configuration.
        For this tool, we are only interested in the timing events and their
        respective containers.

        Args:
            rte_arxml_file (str): The path to the Rte.arxml file.

        Returns:
            list: A list of RteEvent objects.

        Todo:
            * Will be refactored to use autosar_library for parsing the arxml file.
        """
        xml_content = rte_arxml_file.read_text()

        pattern = r".*<REFERENCE-VALUES>(?s:.*?)</REFERENCE-VALUES>"
        matches = re.findall(pattern, xml_content)
        result = []

        for m in matches:
            if "Step" in m:
                container = None
                root = ET.fromstring(m)
                for valref in root.iter('VALUE-REF'):
                    if valref.attrib["DEST"] == "TIMING-EVENT":
                        event = valref.text.split("/")[-1]
                    elif valref.attrib["DEST"] == "ECUC-CONTAINER-VALUE":
                        container = valref.text.split("/")[-1]
                    else:
                        continue
                if container is not None:
                    result.append(RteEvent(event, container))
        return result
