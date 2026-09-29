import logging

from dataclasses import dataclass, asdict


@dataclass
class FunctionStackUsageAndAllocation:
    """ Class that represents stack allocation data variables within a map file """
    function: str
    memory_usage: int = 0
    container: str = None
    container_allocated_stack_size: int = 0


def consolidate(functions_su_info: list,
                function_container_mapping: list,
                stack_alloc_info: list) -> list:
    logger = logging.getLogger(__name__)
    mem_map_list = []

    for su_info in functions_su_info:
        short_function_name = su_info.function_name.removeprefix("Run_").replace("_Step", "Step")

        # Find if the function name is in rte mapping list
        match = next((rte_event for rte_event in function_container_mapping
                      if short_function_name in rte_event.event), None)

        if not match:
            logger.warning(f"Function has no container info from Rte.arxml: {su_info.function_name}")
            continue

        # Find if the container name is in stack_alloc_info
        stack_info = next((stack for stack in stack_alloc_info.list if match.container in stack.name), None)

        if not stack_info:
            logger.warning(f"No stack container found for {su_info.function_name}")
            stack_info["allocated_size"] = "missing info"

        mem_map_list.append(
            FunctionStackUsageAndAllocation(su_info.function_name,
                                            su_info.stack_usage,
                                            match.container,
                                            stack_info.stack_allocation))

    return mem_map_list


def group_by_containers(functions_obj_list: list):
    containers = list(set(map(lambda p: p.container, functions_obj_list)))

    container_and_members = []
    [container_and_members.append(list(filter(lambda p: p.container == c,
                                              functions_obj_list))) for c in containers]

    return container_and_members


def build_final_dict(stack_map_info):
    grouped_functions = group_by_containers(stack_map_info)
    final_dict = []

    for c in grouped_functions:
        functions_as_dict = sorted([asdict(function) for function in c],
                                   key=lambda x: x['memory_usage'] * -1)

        final_dict.append({"container": c[0].container,
                           "stack_size": c[0].container_allocated_stack_size,
                           "unit": "bytes",
                           "functions": functions_as_dict})

    return final_dict
