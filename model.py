from flask import jsonify
from typing import List, Dict
import uuid
import secrets
import base64


class KeyContainer:
    def __init__(self, keys: List[Dict[str, str]] = []):
        """
        Initializes a new instance of the KeyContainer class.

        :param keys: A list of dictionaries containing (id, keys) pairs.
        """
        self.keys = keys

    def to_JSON(self):
        """
        Returns the keys as a JSON-serializable dictionary.
        """
        return jsonify({"keys": self.keys})

    @staticmethod
    def _format_key_for_ui(key: str) -> str:
        """
        Formats the key for display in the UI.

        :param key: The key to format.
        :return: The formatted key.
        """
        if len(key) > 24:
            key = key[0:12] + "[...]" + key[-12:]
        return key

    def __str__(self) -> str:
        keys_str = "\n".join(
            [
                f"\t{key_id} - {self._format_key_for_ui(key)}"
                for key_id, key in self.keys.items()
            ]
        )
        return f"KeyContainer\n{keys_str}"


class Status:
    def __init__(
        self: str,
        source_KME_ID: str,
        target_KME_ID: str,
        master_SAE_ID: str,
        slave_SAE_ID: str,
        key_size: int,
        stored_key_count: int,
        max_key_count: int,
        max_key_per_request: int,
        max_key_size: int,
        min_key_size: int,
        max_SAE_ID_count: int,
        status_extension: object = None,
    ):
        self.source_KME_ID = source_KME_ID
        self.target_KME_ID = target_KME_ID
        self.master_SAE_ID = master_SAE_ID
        self.slave_SAE_ID = slave_SAE_ID
        self.key_size = key_size
        self.stored_key_count = stored_key_count
        self.max_key_count = max_key_count
        self.max_key_per_request = max_key_per_request
        self.min_key_size = min_key_size
        self.max_key_size = max_key_size
        self.max_SAE_ID_count = max_SAE_ID_count
        self.status_extension = status_extension if status_extension else {}

    def to_JSON(self):
        return jsonify(self.__dict__)


class KeyManagementEntity:
    def __init__(
        self,
        id: str,
        key_size: int,
        max_key_count: int,
        max_key_per_request: int,
        min_key_size: int,
        max_key_size: int,
        max_SAE_ID_count: int,
    ):
        self.id = id
        self.key_size = key_size
        self.max_key_count = max_key_count
        self.max_key_per_request = max_key_per_request
        self.min_key_size = min_key_size
        self.max_key_size = max_key_size
        self.max_SAE_ID_count = max_SAE_ID_count
        self.keys: Dict[str, Dict[str, str]] = {}

    def get_keys(
        self,
        slave_SAE_ID: str,
        key_size: int,
        amount_of_keys: int,
        additional_slave_SAE_IDs: List[str] = [],
        ext_mandatory: List[Dict[str, str]] = [],
        ext_optional: List[Dict[str, str]] = [],
    ) -> KeyContainer:
        generated_keys_container = self.generate_keys(
            slave_SAE_ID, key_size, amount_of_keys
        )
        return generated_keys_container

    def get_keys_with_ids(
        self,
        slave_SAE_ID: str,
        key_ids: List[str],
    ) -> KeyContainer:
        keys = {}
        for key_id in key_ids:
            keys[key_id] = base64.b64encode(
                self.keys[slave_SAE_ID][key_id]
            ).decode("utf-8")

        return KeyContainer(keys)

    def does_support_mandatory(
        self, extensions_mandatory: List[Dict[str, str]]
    ):
        return len(extensions_mandatory) == 0

    def generate_keys(
        self,
        slave_SAE_ID,
        size: int,
        amount: int,
        additional_slave_SAE_IDs: List[str] = [],
    ) -> KeyContainer:
        keys = {}

        additional_slave_SAE_IDs.append(slave_SAE_ID)

        for i in range(amount):
            key_uuid = str(uuid.uuid4())
            key = secrets.token_bytes(size)
            for slave_ID in additional_slave_SAE_IDs:
                if not slave_ID in self.keys:
                    self.keys[slave_ID] = {}
                self.keys[slave_ID][key_uuid] = key
            keys[key_uuid] = base64.b64encode(key).decode("utf-8")

        return KeyContainer(keys)
