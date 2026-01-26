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
    Load base config + machine-specific stage configs
    (vision, language, decision, action).

    Args:
        machine (str): machine name ('fish' or 'fly')
        config_dir (Path): root config directory

    Returns:
        ConfigBox: merged configuration object
    """   

    #logger.info("load_machine_config(): START")
    #logger.info(f"Loading configurations for machine: {machine}")

    project_root = find_project_root()
    #logger.info(f"Project root resolve to : {project_root}")

    #----------------LOAD BASE CONFIG-----------------
    configs_dir = project_root / "configs"
    config = read_yaml(configs_dir/"base.yaml")


    #----------LOAD STAGE-SPECIFIC CONFIG-------------
    stages = ["vision", "language","decision","action"]

    for stage in stages:
        stage_config_path = configs_dir/machine/f"{stage}.yaml"

        if not stage_config_path.exists():
            raise FileNotFoundError(f"load_machine_config(): Missing config file: {stage_config_path}")

        config[stage] = read_yaml(stage_config_path)
        #logger.info(f"{stage.capitalize()} config loaded for {machine}")

    
    #logger.info(f"All configurations loaded successfully for machine: {machine}, \n{config}",)
    #logger.info("load_machine_config(): END")

    return config