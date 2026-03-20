import yaml
from pathlib import Path
from box import ConfigBox
from box.exceptions import BoxValueError
from ensure import ensure_annotations

from src.common.logging import logger



def find_project_root() -> Path:
    """
    Find project root by locating 'configs/base.yaml'
    """
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "configs" / "base.yaml").exists():
            return parent
        
    raise FileNotFoundError("find_project_root(): Error in finding `configs/base.yaml`. Please check project structure.")



@ensure_annotations
def read_yaml(path_to_yaml: Path) -> ConfigBox:
    """
    Read a YAML file and return its content as ConfigBox.

    Args:
        path_to_yaml (Path): Path to the YAML file

    Raises:
        ValueError: If YAML file is empty
        Exception: Any other exception

    Returns:
        ConfigBox: Parsed YAML content
    """
    try:
        with open(path_to_yaml, "r") as yaml_file:
            content = yaml.safe_load(yaml_file)

            if content is None:
                raise BoxValueError
            
            #logger.info(f"read_yaml(): YAML file is loaded sucessfully: {path_to_yaml}")
            return ConfigBox(content)

    except BoxValueError:
        raise ValueError(f"read_yaml(): YAML file is empty: {path_to_yaml}")
        
    except Exception as e:
        logger.error(f"read_yaml(): Error reading YAML file {path_to_yaml}: {e}")
        raise e



@ensure_annotations
def load_machine_config(machine: str) -> ConfigBox:
    """
    Load base config + machine specific configs.

    Args:
        machine: 'fish' or 'fly'

    Returns:
        ConfigBox: merged configuration
    """
    try:
        project_root = find_project_root()
        configs_dir = project_root / "configs"

        # ---------------- LOAD BASE CONFIG ----------------
        base_config = read_yaml(configs_dir / "base.yaml")

        config = ConfigBox(base_config)

        # --------------- LOAD MACHINE CONFIGS -------------
        machine_dir = configs_dir / machine

        if not machine_dir.exists():
            raise FileNotFoundError(f"Config directory not found: {machine_dir}")

        config[machine] = ConfigBox()

        # load all yaml files automatically
        for yaml_file in machine_dir.glob("*.yaml"):

            stage_name = yaml_file.stem
            config[machine][stage_name] = read_yaml(yaml_file)

        return config
    

    except Exception as e:
        logger.error(f"Error occurred in load_machine_config(), error: {e}")
        raise e