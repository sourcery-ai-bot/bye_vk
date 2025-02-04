#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time

from actions.common import are_you_sure, print_owner_info, pluralize
from core.auth import get_session

try:
    import simplejson as json
except ImportError:
    import json

import vk_api


def delete_albums():
    """Удалить альбомы"""

    vk_session = get_session()

    try:
        vk_session.method("users.get")
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    vk_tools = vk_api.VkTools(vk_session)

    owner = vk_session.method("users.get")[0]
    print_owner_info(owner)

    albums = vk_tools.get_all("photos.getAlbums", 1000)

    if albums["count"] == 0:
        print("Нет альбомов")
    else:
        n = albums["count"]
        print(f"Всего {n:d} {pluralize(n, 'альбом', 'альбома', 'альбомов')}")
        sure = are_you_sure()
        if not sure:
            return

        for album in albums["items"]:
            print("Удаляем " + album["title"])
            vk_session.method("photos.deleteAlbum", values={"album_id": album["id"]})
            time.sleep(1)

    print("Теперь удалим сохранённые, фото со стены, фото профиля")
    sure = are_you_sure()
    if not sure:
        return

    for special_id in ["saved", "wall", "profile"]:
        album_photos = vk_tools.get_all("photos.get", 1000, values={
            "album_id": special_id
        })
        time.sleep(1)

        for photo in album_photos["items"]:
            print(f"Deleting {str(special_id)}_" + str(photo["id"]))
            vk_session.method("photos.delete", values={"photo_id": photo["id"]})
            time.sleep(1)
