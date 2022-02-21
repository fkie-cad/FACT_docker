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


def build(args):
    cmd = f"docker build --rm -t {args.tag} ."

    subprocess.run(cmd.split())


def pytest(args):
    # We use the default docker-mount-base-dir because the user has no chance to change it when running the tests
    create_docker_mount_base_dir_with_correct_permissions("/tmp/fact-docker-mount-base-dir/")
    cmd = f"""docker run \
    {pass_docker_socket_args(args)} \
    {mount_relevant_dirs_for_docker_args("/tmp/fact-docker-mount-base-dir/")} \
    -it \
    --rm \
    {args.image}
    pytest {" ".join(args.pass_to_pytest)}
    """

    subprocess.run(cmd.split())


def pull(args):
    cmd = f"""docker run \
    {pass_docker_socket_args(args)} \
    -it \
    --rm \
    {args.image} pull-containers
    """

    subprocess.run(cmd.split())


def remove(args):
    cmd = f"docker rm {args.name}"

    subprocess.run(cmd.split())


def run(args):
    mongodb_path_gid = os.stat(args.wt_mongodb_path).st_gid
    fw_data_path_gid = os.stat(args.fw_data_path).st_gid

    # Always initialize the db on the first run
    pathlib.Path(f"{args.wt_mongodb_path}/REINITIALIZE_DB").touch()

    create_docker_mount_base_dir_with_correct_permissions(args.docker_mount_base_dir)

    # TODO the config in the container might mismatch with what we have configured here
    config_cmd = f"--mount type=bind,source={args.config_path},destination=/opt/FACT_core/src/config,ro=true"
    if args.config_path is None:
        config_cmd = ""

    start_cmd = "start"
    if args.branch is not None:
        start_cmd = f"start-branch {args.branch}"

    cmd = f"""docker run \
    {pass_docker_socket_args(args)} \
    {mount_relevant_dirs_for_docker_args(args.docker_mount_base_dir)} \
    -it \
    --name {args.name} \
    --hostname {args.name} \
    --group-add {mongodb_path_gid} \
    --mount type=bind,source={args.wt_mongodb_path},destination=/media/data/fact_wt_mongodb \
    --group-add {fw_data_path_gid} \
    --mount type=bind,source={args.fw_data_path},destination=/media/data/fact_fw_data \
    -p {args.port}:5000 \
    {config_cmd} \
    {args.image} {start_cmd}
    """

    subprocess.run(cmd.split())


def start(args):
    cmd = f"docker start -ai {args.name}"

    subprocess.run(cmd.split())


def stop(args):
    cmd = f"docker stop {args.name}"

    subprocess.run(cmd.split())


def main():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=lambda _: parser.print_usage())
    subparsers = parser.add_subparsers()

    build_p = subparsers.add_parser("build", help="Build the FACT image.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    build_p.set_defaults(func=build)
    build_p.add_argument("--tag", default="fkiecad/fact", help="The tag that the built image should have.")

    pull_p = subparsers.add_parser("pull", help="Pull or build all neccessary docker containers required to run FACT.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    pull_p.set_defaults(func=pull)
    pull_p.add_argument("--image", default="fkiecad/fact", help="The FACT image name.")

    remove_p = subparsers.add_parser("remove", help="Remove the container.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    remove_p.set_defaults(func=remove)
    remove_p.add_argument("--name", default="fact", help="The FACT container name.")

    run_p = subparsers.add_parser("run", help="Create and run a FACT container.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    run_p.set_defaults(func=run)
    run_p.add_argument("--name", default="fact", help="The FACT container name.")
    run_p.add_argument("--image", default="fkiecad/fact", help="The FACT image name.")
    run_p.add_argument("--port", default=5000, help="The port that the webserver is listening on.")
    # We default to the path that is set in the default config
    run_p.add_argument("--docker-mount-base-dir", default="/tmp/fact-docker-mount-base-dir", help="Has to match docker-mount-base-dir in main.cfg")
    # We cant reasonably choose a default path for the following arguments
    run_p.add_argument("--wt-mongodb-path", required=True, help="The path to the fact_wt_mongodb directory on the host. The group must have rwx permissions.")
    run_p.add_argument("--fw-data-path", required=True, help="Path to fact_fw_data directory on the host. The group must have rwx permissions.")
    run_p.add_argument("--config-path", help="The directory that contains the FACT configuration. If ommited use the config in the container.")
    run_p.add_argument("--branch", help="The branch of FACT to start")

    start_p = subparsers.add_parser("start", help="Start container", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    start_p.set_defaults(func=start)
    start_p.add_argument("--name", default="fact", help="The FACT container name")

    stop_p = subparsers.add_parser("stop", help="Stop a running container", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    stop_p.set_defaults(func=stop)
    stop_p.add_argument("--name", default="fact", help="The FACT container name")

    pytest_p = subparsers.add_parser("pytest", help="Run pytest on FACT in the container. Additional arguments will be passed to pytest.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    pytest_p.set_defaults(func=pytest)
    pytest_p.add_argument("--image", default="fkiecad/fact", help="The FACT image name.")
    pytest_p.add_argument("pass_to_pytest", nargs=argparse.REMAINDER, help=argparse.SUPPRESS)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
