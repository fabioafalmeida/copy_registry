# -*- coding: utf-8 -*-

import docker
import json
import logging


def main():
    logger = logging.getLogger('copy_registry')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    settings = json.load(open("settings.json"))
    client = docker.from_env()

    projects = settings["projects"]
    for project in projects:
        logger.info("Logging into " + settings["origin"])
        client.login(registry=settings["origin"], username=settings["originUser"], password=settings["originPass"])
        repo_origin = settings["origin"]+"/"+project

        logger.info("Pulling all images from " + repo_origin)
        client.images.pull(repository=repo_origin, all_tags=True)

        logger.info("Logging into " + settings["destination"])
        client.login(registry=settings["destination"], username=settings["destinationUser"], password=settings["destinationPass"])

        for image in client.images.list(filters={"reference": repo_origin}):
            for tag in image.tags:
                if repo_origin in tag:
                    break
            split = tag.split(":")
            num_tag = split[len(split)-1]
            main_project = settings["destinationMainProject"]
            if main_project:
                main_project = main_project + "/"
            repo_dest = settings["destination"]+"/"+main_project+project
            logger.info("Creating Tag " + repo_dest + ":" + num_tag)
            image.tag(repo_dest, num_tag)

        logger.info("Pushing all images to " + repo_dest)
        client.images.push(repo_dest)


if __name__ == "__main__":
    main()
