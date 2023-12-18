from ..utils.logging import logger
from ..utils.config import Config
from ..utils.context import Context
import sys
import re
import json
from ..utils.common import create_change_set, remove_change_set, format_diff, get_yes_or_no, deploy_stack, create_stack,package


def deploy(config_path, root_path):
    config = Config.parse(config_path)
    config.setup_env(Context.get_args().env)
    services = config.stacks
    logger.warning(f"Checking difference for stacks from file {config_path}")
    
    logger.info(f"* Found {len(services)} services checking differences...")

    for service in services:
        if not re.search(Context.get_args().service, service.name):
            continue

        change_set = create_change_set(service, config)
        if change_set:
            diffs = [format_diff(change)for change in change_set["Changes"]]

            if len(diffs):
                logger.warning(f"Found {len(diffs)} differences for the stack {service.name}")
                for diff in diffs:
                    logger.warning(f"> {diff}")
                
                should_continue = get_yes_or_no(f"Do you wish to continue to update serivce: {service.name}")

                if not should_continue:
                    remove_change_set(service.name, change_set["ChangeSetName"])
                else:
                    logger.info("Deploying service...")
                    deploy_stack(service.name, change_set["ChangeSetName"])
            else:
                logger.info(f"Found no differences for the stack {service.name}")
        else:
            yml = package(service, config)
            logger.warn(f"{service.name} new stack ⭐")
            logger.warn(yml)
            should_continue = get_yes_or_no(f"Do you wish to continue to update serivce: {service.name}")

            if should_continue:
                create_stack(service, yml)

        
