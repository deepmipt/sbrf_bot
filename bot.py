import threading
import requests
from queue import Queue
from threading import Thread
from requests.exceptions import HTTPError

from deeppavlov.core.common.log import get_logger
from conversation import Conversation
from agent import init_agent

log = get_logger(__name__)


class Bot(Thread):
    def __init__(self, config: dict, input_queue: Queue):
        super(Bot, self).__init__()
        self.config = config
        self.model = self._init_model()
        self.conversations = {}
        self.access_info = {}
        self.http_sessions = {}
        self.input_queue = input_queue

        self._request_access_info()
        polling_interval = self.config['ms_bot_framework_defaults']['auth_polling_interval']
        timer = threading.Timer(polling_interval, self._update_access_info)
        timer.start()

    def run(self):
        while True:
            activity = self.input_queue.get()
            self._handle_activity(activity)

    def _init_model(self):
        model = init_agent()
        return model

    def _update_access_info(self):
        polling_interval = self.config['ms_bot_framework_defaults']['auth_polling_interval']
        timer = threading.Timer(polling_interval, self._update_access_info)
        timer.start()
        self._request_access_info()

    def _request_access_info(self):
        headers = {'Host': self.config['ms_bot_framework_defaults']['auth_host'],
                   'Content-Type': self.config['ms_bot_framework_defaults']['auth_content_type']}

        payload = {'grant_type': self.config['ms_bot_framework_defaults']['auth_grant_type'],
                   'scope': self.config['ms_bot_framework_defaults']['auth_scope'],
                   'client_id': self.config['ms_bot_framework_defaults']['auth_app_id'],
                   'client_secret': self.config['ms_bot_framework_defaults']['auth_app_secret']}

        result = requests.post(url=self.config['ms_bot_framework_defaults']['auth_url'],
                               headers=headers,
                               data=payload)

        # TODO: insert json content to the error message
        status_code = result.status_code
        if status_code != 200:
            raise HTTPError(f'Authentication token request returned wrong HTTP status code: {status_code}')

        self.access_info = result.json()
        log.info(f'Obtained authentication information from Microsoft Bot Framework: {str(self.access_info)}')

    def _handle_activity(self, activity: dict):
        conversation_key = f"{activity['channelId']}||{activity['conversation']['id']}"

        if conversation_key not in self.conversations.keys():
            self.conversations[conversation_key] = Conversation(self, activity)
            log.info(f'Created new conversation {conversation_key}')

        conversation = self.conversations[conversation_key]
        conversation.handle_activity(activity)
