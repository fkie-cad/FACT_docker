#!/usr/bin/env python3

import argparse
import grp
import os
import pathlib
import subprocess


def create_docker_mount_base_dir_with_correct_permissions(docker_mount_base_dir):
    docker_gid = grp.getgrnam("docker").gr_gid
    pathlib.Path(docker_mount_base_dir).mkdir(mode=0o770, parents=True, exist_ok=True)
    os.chown(docker_mount_base_dir, -1, docker_gid)


def pass_docker_socket_args(args):
    docker_gid = grp.getgrnam("docker").gr_gid
    docker_socket = os.getenv("DOCKER_HOST", default="/var/run/docker.sock")

    return f"""\
    --group-add {docker_gid} \
    --mount type=bind,source={docker_socket},destination=/var/run/docker.sock \
    """


def mount_relevant_dirs_for_docker_args(docker_mount_base_dir):
    return f"""\
    --mount type=bind,source={docker_mount_base_dir},destination={docker_mount_base_dir} \
    """


def pull(args):
    cmd = f"""docker run \
    {pass_docker_socket_args(args)} \
    -it \
    --rm \
    fkie-cad/fact-core-scripts:4.0 pull-containers
    """

    subprocess.run(cmd.split())


def initialize_db(args):
    cmd = f"""docker run \
    -it \
    --mount type=bind,source={args.main_cfg_path},destination=/opt/FACT_core/src/config/main.cfg,ro=true \
    --rm \
    --network {args.network} \
    fkie-cad/fact-core-scripts:4.0 \
    initialize-db
    """

    subprocess.run(cmd.split())


def compose_env(args):
    docker_gid = grp.getgrnam("docker").gr_gid
    fw_data_dir_gid = os.stat(args.firmware_file_storage_dir).st_gid
    create_docker_mount_base_dir_with_correct_permissions(args.docker_mount_base_dir)
    print(f"""\
export FACT_DOCKER_MAIN_CFG_PATH={args.main_cfg_path}
export FACT_DOCKER_UWSGI_CONFIG_INI_PATH={args.uwsgi_config_ini_path}
export FACT_DOCKER_DOCKER_GID={docker_gid}
export FACT_DOCKER_DOCKER_MOUNT_BASE_DIR={args.docker_mount_base_dir}
export FACT_DOCKER_FIRMWARE_FILE_STORAGE_DIR={args.firmware_file_storage_dir}
export FACT_DOCKER_FIRMWARE_FILE_STORAGE_DIR_GID={fw_data_dir_gid}
export FACT_DOCKER_FRONTEND_PORT={args.port}
export FACT_DOCKER_POSTGRES_PASSWORD=example""")


def main():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=lambda _: parser.print_usage())
    subparsers = parser.add_subparsers()

    pull_p = subparsers.add_parser(
        "pull",
        help="Pull or build all neccessary docker containers required to run FACT.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    pull_p.set_defaults(func=pull)

    initialize_db_p = subparsers.add_parser(
        "initialize-db",
        help="Initialize the postgres database",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    initialize_db_p.set_defaults(func=initialize_db)
    initialize_db_p.add_argument(
        "--main-cfg-path",
        default=f"{os.getcwd()}/main.cfg",
        help="Path to main.cfg",
        required=False,
    )
    initialize_db_p.add_argument(
        "--network",
        help="The docker network that the postgres container runs in",
        required=True,
    )

    compose_env_p = subparsers.add_parser(
        "compose-env",
        help="Print out sane defaults for FACT_DOCKER_* variables",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    compose_env_p.set_defaults(func=compose_env)
    compose_env_p.add_argument(
        "--main-cfg-path",
        default="$(pwd)/main.cfg",
        help="Path to main.cfg",
        required=False,
    )
    compose_env_p.add_argument(
        "--uwsgi-config-ini-path",
        default="$(pwd)/uwsgi_config.ini",
        help="Path to uwsgi_config.ini",
        required=False,
    )
    compose_env_p.add_argument(
        "--firmware-file-storage-dir",
        help="Path to 'firmware-file-storage-directory'",
        required=True,
    )
    compose_env_p.add_argument(
        "--port",
        default=5000,
        help="The FACT frontend webserver port",
        required=False,
    )
    compose_env_p.add_argument(
        "--docker-mount-base-dir",
        default="/tmp/fact-docker-mount-base-dir",
        help="Has to match docker-mount-base-dir in main.cfg",
    )

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
