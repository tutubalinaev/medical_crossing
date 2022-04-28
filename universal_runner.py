# coding: utf-8
"""
    We work under assumption that all scripts of interest look like:
    `python xxx.py --argument argument_value --another-argument another_argument_value`
"""
import logging
import os

import hydra

log = logging.getLogger()


def run_command(command):
    log.info(f"Executing: {command}")
    log.info(f"Finished with return code: {os.system(command)}.")


def run_baseline(cfg, save_results_dir, base_dir):
    cuda_visible_devices = os.environ.get("CUDA_VISIBLE_DEVICES")
    cuda_visible_devices = ("CUDA_VISIBLE_DEVICES=" + cuda_visible_devices) if cuda_visible_devices else ""
    log.info("Evaluating baseline...")

    goto = cfg.model.path_to_script
    evaluation_script = cfg.model.script_name
    parameters_mapping = {k.split(".")[-1]: v for k, v in dict(cfg.parameters_mapping).items()}
    passable_params = []

    for key in cfg.model:
        if key in parameters_mapping:
            if str(cfg.model[key]).strip() == "True":
                passable_params.append(f"--{parameters_mapping[key]}")
            elif str(cfg.model[key]).strip() != "False":
                passable_params.append(f"--{parameters_mapping[key]}={cfg.model[key]}")

    interpreter = cfg.python.interpreter
    resulting_script = f"{cuda_visible_devices} cd {base_dir}/{goto} &&" \
                       f" {interpreter} {evaluation_script} {' '.join(passable_params)}" \
                       f" > {save_results_dir}/stdout.txt"
    print(resulting_script)
    log.info(resulting_script)
    run_command(resulting_script)
    log.info("Done with baseline evaluation.")


# @hydra.main(config_path=os.environ["HYDRA_CONFIG_PATH"])
@hydra.main(config_path="config", config_name="config")
def main(config):
    print(config)
    log.info(str(config))
    auto_generated_dir = os.getcwd()
    base_dir = hydra.utils.get_original_cwd()
    config.original_dir = base_dir
    config.run_dir = auto_generated_dir
    run_baseline(config, auto_generated_dir, base_dir)


if __name__ == "__main__":
    main()
