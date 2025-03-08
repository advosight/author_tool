
import os
import json
import yaml
import importlib
from typing import List
from utils.logging import getLogger

logger = getLogger('Plugin Framework', 'DEBUG')

def get_plugin_definitions(type: str) -> List[dict]:
    """ Returns a list of plugin definitions for the given type 
    
    Args:
        type (str): The type of plugin to load
    
    Returns: An array of plugin registrations
    """

    # Check if the plugins directory exists
    if not os.path.exists(f"plugins/{type}"):
        return []
    # Read plugin registration files from the directory plugins, with the type being the subfolder
    # and the file being the plugin name
    plugins = []
    
    for plugin in os.listdir(f"plugins/{type}/registry"):
        if plugin.endswith(".yml"):
            # Open yml file and retrieve yml data
            with open(f"plugins/{type}/registry/{plugin}") as f:
                plugin_details = f.read().strip()
                data = yaml.safe_load(plugin_details)
                plugins.append(data)

    return plugins

def load_plugin_class(plugin_registration: dict) -> any:
    """ Loads a plugin class from the given plugin registration

    Args:
        plugin_registration (dict): The plugin registration to load

    Returns: The plugin class
    """
    # Load the plugin class
    logger.info(f"Loading plugin {plugin_registration['class']} from {plugin_registration['module']}")
    module = importlib.import_module(plugin_registration['module'])
    logger.info("Module loaded")
    plugin_class = getattr(module, plugin_registration['class'])

    return plugin_class