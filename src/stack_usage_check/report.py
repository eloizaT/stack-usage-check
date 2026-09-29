import json
import logging

import stack_usage_check.aggregator as aggregator
from stack_usage_check.utils.logger import Config


class StackUsageReport():
    def __init__(self, parameters: dict):
        self.output_file = parameters["output"]

        self.logger = logging.getLogger(__name__)

        # TODO: Consider using namespaces instead
        if "memory_threshold_limit" in parameters.keys():
            self.failing_limit = parameters["memory_threshold_limit"]
        else:
            self.failing_limit = Config().get_config()["failing_limit"]

        self.warning_limit = Config().get_config()["warning_limit"]

    def generate_report(self, stack_map_info: list):
        final_format = aggregator.build_final_dict(stack_map_info)

        with open(self.output_file, 'w') as f:
            json.dump(final_format, f, indent=4)

    def analyze_stack_usage(self):
        """
        This method will verify if the stack usages in the report
        file are within the limits. See documentation for the
        required json format.

        Issues a warning:
        Warning is prompted when memory usage is between the warning limit
        and failing limit (threshold). Warning limit is configured
        in config.json and is set to 75% (.75)

        Raises:
            ValueError: When a memory usage exceeds the set threshold
            limit for the allocated stack size. The default failing
            limit is defined in config.json and set to 85% (.85) initially.
        """
        with open(self.output_file, 'r') as f:
            dict_list = json.load(f)

        print(json.dumps(dict_list, indent=4, sort_keys=True))

        for task_data in dict_list:
            # Get the runnable with highest memory usage
            runnable_with_highest_mem_usage = max(task_data['functions'],
                                                  key=lambda x:
                                                  int(x['memory_usage']))

            mem_usage = int(runnable_with_highest_mem_usage['memory_usage'])
            runnable_name = runnable_with_highest_mem_usage['function']
            allocated = int(task_data['stack_size'])

            exceeding_list = []
            warning_list = []
            if mem_usage > self.failing_limit * allocated:
                exceeding_list.append(f"{runnable_name}: {mem_usage}")

            elif mem_usage > self.warning_limit * allocated:
                warning_list.append(f"{runnable_name}: {mem_usage}")

            if exceeding_list:
                raise ValueError(f"Memory usage exceeds {self.failing_limit: .0%} "
                                 f"of allocated stack size: {exceeding_list}")

            if warning_list:
                self.logger.warning(f"Memory usage exceeds {self.warning_limit: .0%} "
                                    f"of allocated stack size: {warning_list}")
