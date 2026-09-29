import logging

import stack_usage_check.aggregator as aggregator
from stack_usage_check.map_file import StackArrayMapParser
from stack_usage_check.report import StackUsageReport
from stack_usage_check.rte_file import RunTimeEnvFile
from stack_usage_check.stack_usage_file import StackUsageFile


class StackUsageProcessor:
    """Process GCC stack usage, stack-array allocations, and RTE mappings."""

    def __init__(self, parameters):
        if "output" not in parameters.keys():
            parameters["output"] = "stack_report.json"

        self.parameters = parameters
        self.logger = logging.getLogger(__name__)

        if parameters["map_file"] is None:
            raise ValueError("Please provide the path to the map file. "
                             "Use -m or --map-file option.")

        if parameters["rte_arxml"] is None:
            raise ValueError("Please provide the path to the RTE arxml file. "
                             "Use -r or --rte-arxml option.")

        if parameters["obj_dir"] is None:
            raise ValueError("Please provide the path to the generated .su objs "
                             "directory. Use -t or --obj-dir option.")

        self.su_folder = parameters["obj_dir"]
        self.map_file = parameters["map_file"]
        self.rte_arxml = parameters["rte_arxml"]
        self.output_file = parameters["output"]

    def analyze_and_generate_report(self, stack_info: list):
        report = StackUsageReport(self.parameters)
        report.generate_report(stack_info)

        self.logger.info("Checking the limits...")
        report.analyze_stack_usage()

    def process_stack_usage_info(self):
        # Parse the map file and build a list of task stack allocations
        self.logger.info(f"Parsing {self.map_file}. Getting all task stack allocation data")
        stack_allocations = StackArrayMapParser().get_stack_allocation_list(self.map_file)

        # Parse the .su objects and get the stack usage per target function
        self.logger.info("Parsing .su objects. Getting the stack usage per runnable")
        runnables_stack_usages = StackUsageFile.StackUsageFileType("gcc").get_all_runnables(self.su_folder)

        # Parse the RTE-arxml to build a list of function to container mappings
        runnable_to_task_mappings_from_rte = RunTimeEnvFile.get_step_timing_event_ref_list(self.rte_arxml)

        self.logger.info("Generating stack usage report")
        consolidated_stack_usage_info = aggregator.consolidate(
            runnables_stack_usages,
            runnable_to_task_mappings_from_rte,
            stack_allocations)

        self.analyze_and_generate_report(consolidated_stack_usage_info)
