#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time

from actions.common import are_you_sure, YES_NO_PROMPT, print_owner_info
from core.auth import get_session
from core.vk_wrapper import VkToolsWithRetry

try:
    import simplejson as json
except ImportError:
    import json

import vk_api


def delete_messages():
    """Удалить все диалоги"""

    vk_session = get_session()

    try:
        vk_session.method("users.get")
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    vk_tools = VkToolsWithRetry(vk_session)

    owner = vk_session.method("users.get")[0]
    print_owner_info(owner)

    first_time = True

    while True:
        print("Получаем диалоги...")
        conversations = vk_tools.get_all(
            "messages.getConversations",
            max_count=200,
            values={"preview_length": "0"}
        )
        print("Количество диалогов:", conversations["count"])

        if conversations["count"] == 0:
            print("Все диалоги уже удалены!")
            return

        if first_time:
            sure = are_you_sure()
            if not sure:
                return
            first_time = False

        for item in conversations["items"]:
            conversation = item["conversation"]

            peer_id = conversation["peer"]["id"]
            peer_type = conversation["peer"]["type"]

            values = {"count": "10000"}

            if peer_type in ["chat", "group", "email"]:
                values["peer_id"] = peer_id
            elif peer_type == "user":
                values["user_id"] = peer_id
            print(f"Удаляем {values}...")

            vk_session.method("messages.deleteConversation", values=values)
            time.sleep(1)

        again = input(
            "За один раз из каждого диалога можно удалить максимум 10000 "
            "сообщений.\n"
            "Попробовать удалить диалоги ещё раз?\n" + YES_NO_PROMPT)
        if again.lower() not in ["y", "д"]:
            return
