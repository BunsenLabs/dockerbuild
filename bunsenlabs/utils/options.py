from typing import Any
import argparse
import os
import yaml

def getopts(option_file: str, environment_namespace: str = "BL") -> argparse.Namespace:
    def yaml_env_constructor(loader, node) -> Any:
        def __env(opt: str, local_preference: Any) -> Any:
            key = "{}_{}".format(environment_namespace, opt)
            if key in os.environ:
                return os.environ[key]
            else:
                return local_preference
        seq = loader.construct_sequence(node)
        return __env(*seq)

    with open(option_file, "r") as FILE:
        yaml.add_constructor("!Env", yaml_env_constructor, Loader=yaml.FullLoader)
        options = yaml.load(FILE, Loader=yaml.FullLoader)

    parser = argparse.ArgumentParser(description=options.get("program_description"),
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    for opt in options.get("options"):
        parser.add_argument(*opt["names"], **{k:v for k,v in opt.items() if k != 'names'})
    
    return parser.parse_args()
