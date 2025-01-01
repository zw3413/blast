import yaml
from easydict import EasyDict
import os.path as osp

class YamlParser(EasyDict):
    """
    YAML parser that inherits from EasyDict for dot notation access.
    Supports loading and merging of YAML configuration files.
    """
    
    def __init__(self, config_dict=None):
        """
        Initialize the YAML parser.
        
        Args:
            config_dict (dict, optional): Initial configuration dictionary.
        """
        super(YamlParser, self).__init__(config_dict or {})
    
    def merge_from_file(self, yaml_path):
        """
        Load and merge configuration from a YAML file.
        
        Args:
            yaml_path (str): Path to the YAML configuration file.
            
        Raises:
            FileNotFoundError: If the YAML file doesn't exist.
            yaml.YAMLError: If there's an error parsing the YAML file.
        """
        if not osp.exists(yaml_path):
            raise FileNotFoundError(f"Config file not found: {yaml_path}")
            
        with open(yaml_path, 'r') as f:
            try:
                new_config = yaml.safe_load(f)
                self._merge_config(self, new_config)
            except yaml.YAMLError as e:
                raise yaml.YAMLError(f"Error parsing YAML file: {e}")
    
    def _merge_config(self, current_dict, new_dict):
        """
        Recursively merge new configuration into the current configuration.
        
        Args:
            current_dict (dict): Current configuration dictionary.
            new_dict (dict): New configuration to merge.
        """
        for key, val in new_dict.items():
            if (key in current_dict and isinstance(current_dict[key], dict) 
                and isinstance(val, dict)):
                self._merge_config(current_dict[key], val)
            else:
                current_dict[key] = val
    
    def __str__(self):
        """
        String representation of the configuration.
        
        Returns:
            str: Pretty-formatted string of the configuration.
        """
        return yaml.dump(self)