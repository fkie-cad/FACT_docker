#!/usr/bin/env python3

import argparse
import sys
import os
import subprocess
import grp
import pathlib

def build(args):
    cmd = f"docker build --rm -t {args.tag} ."

    subprocess.run(cmd.split())

def pull(args):
    docker_gid = grp.getgrnam("docker").gr_gid
    docker_socket = os.getenv("DOCKER_HOST", default="/var/run/docker.sock")

    cmd = f"""docker run \
    -it \
    --rm \
    --group-add {docker_gid} \
    -v {docker_socket}:/var/run/docker.sock \
    {args.image} pull-containers
    """

    subprocess.run(cmd.split())

def remove(args):
    cmd = f"docker rm {args.name}"

    subprocess.run(cmd.split())

def run(args):
    # Always initialize the db on the first run
    pathlib.Path(f"{args.wt_mongodb_path}/REINITIALIZE_DB").touch()

    docker_gid = grp.getgrnam("docker").gr_gid
    docker_socket = os.getenv("DOCKER_HOST", default="/var/run/docker.sock")
    mongodb_path_gid = os.stat(args.wt_mongodb_path).st_gid
    fw_data_path_gid = os.stat(args.fw_data_path).st_gid
    # TODO the config in the container might mismatch with what we have configured here
    config_cmd = f"--mount type=bind,source={args.config_path},destination=/opt/FACT_core/src/config"
    if args.config_path is None:
        config_cmd = ""

    start_cmd = "start"
    if args.branch is not None:
        start_cmd = f"start-branch {args.branch}"


    cmd = f"""docker run -it \
    --name {args.name} \
    --hostname {args.name} \
    --group-add {docker_gid} \
    -v {docker_socket}:/var/run/docker.sock \
    --group-add {mongodb_path_gid} \
    -v {args.wt_mongodb_path}:/media/data/fact_wt_mongodb \
    --group-add {fw_data_path_gid} \
    -v {args.fw_data_path}:/media/data/fact_fw_data \
    -v {args.docker_dir}:{args.docker_dir} \
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
    build_p.add_argument("--tag", default="fkiecad/fact", help="The tag that the build image should have.")

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
    # We default to the path that is set in the default container config
    run_p.add_argument("--docker-dir", default="/tmp/fact-docker-tmp", help="The path on the host that the container should instruct docker to output files generated by running other docker images.")
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

    args = parser.parse_args()
    args.func(args)


main()