from flask import jsonify
from typing import List, Dict
import uuid
import secrets
import base64


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
        ext_mandatory: List[Dict[str, str]] = None, 
        ext_optional: List[Dict[str, str]] = None
    ) -> Dict[str, str]:
        generated_keys = self.generate_keys(slave_SAE_ID ,key_size, amount_of_keys)
        return generated_keys

    def get_keys_with_ids(
        self, 
        key_ids: List[str], 
    ) -> Dict[str, str]:
        keys = {}
        for key_id in key_ids:
            keys[key_id] = base64.b64encode(self.keys[key_id]).decode('utf-8')
        
        return keys

    def does_support_mandatory(self, extensions_mandatory: List[Dict[str, str]]):
        return False

    def generate_keys(self, slave_SAE_ID, size: int, amount: int ) -> Dict[str, str]:
        keys = {}

        if not slave_SAE_ID in self.keys:
            self.keys[slave_SAE_ID] = {}

        for i in range(amount):
            key_uuid = str(uuid.uuid4())
            key = secrets.token_bytes(size)
            self.keys[slave_SAE_ID][key_uuid] = key
            keys[key_uuid] = base64.b64encode(key).decode('utf-8')
        
        return keys


class KeyContainer:
    def __init__(self, keys: List[Dict[str, str]] = None):
        self.keys = keys if keys else []

    def to_JSON(self):
        return jsonify({"keys": self.keys})
