# -*- coding: utf-8 -*-

import docker
import json


def main():
    settings = json.load(open("settings.json"))
    client = docker.from_env()

    projects = settings["projects"]
    for project in projects:
        client.login(registry=settings["origin"], username=settings["originUser"], password=settings["originPass"])
        repo_origin = settings["origin"]+"/"+project
        client.images.pull(repository=repo_origin, all_tags=True)

        client.login(registry=settings["destination"], username=settings["destinationUser"], password=settings["destinationPass"])

        for image in client.images.list(filters={"reference": repo_origin}):
            for tag in image.tags:
                if repo_origin in tag:
                    break
            split = tag.split(":")
            num_tag = split[len(split)-1]
            print(num_tag)
            main_project = settings["destinationMainProject"]
            if main_project:
                main_project = main_project + "/"
            repo_dest = settings["destination"]+"/"+main_project+project
            image.tag(repo_dest, num_tag)

        client.images.push(repo_dest)


if __name__ == "__main__":
    main()
