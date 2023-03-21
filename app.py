# -----------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
# -----------------------------------------------------------------------------------------

from typing import List
from flask import Flask, jsonify, request
from flask_cors import CORS
from model import KeyContainer, Status, KeyManagementEntity
from errors import KeySizeError, ExtensionMandatoryUnsupportedError
from flask import send_from_directory



app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {
    "origins": ["http://localhost:*", "http://127.0.0.1:*", "http://178.254.28.176:*"]
}})

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stdout',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

import logging
#logging.basicConfig(filename='logs/keys.log', encoding='utf-8', level=logging.DEBUG)

_KeyManager = KeyManagementEntity(
    id="kme_ID_1",
    key_size=352,
    max_key_count=1024,
    max_key_per_request=128,
    min_key_size=8,
    max_key_size=1024,
    max_SAE_ID_count=0,
)

@app.route('/<path:path>')
def send_report(path):
    return send_from_directory('static', path)


@app.route("/api/v1/keys/<string:slave_SAE_ID>/enc_key", methods=["GET", "POST"])
def get_key(slave_SAE_ID):
    extension_mandatory: List[str] = []
    extension_optional: List[str] = []
    additional_slave_SAE_IDs: List[str] = []
    amount_of_keys: int = 0

    if request.method == "POST":
        post_data = request.get_json()

        amount_of_keys = int(post_data.get("number", 1))
        key_size = int(post_data.get("size", _KeyManager.key_size))
        extension_mandatory = post_data.get("extension_mandatory", [])
        additional_slave_SAE_IDs = post_data.get("additional_slave_SAE_IDs", [])
        extension_optional = post_data.get("extension_optional", [])
    else:
        amount_of_keys = request.args.get("number", default = 1, type = int)
        key_size = request.args.get("size", default = _KeyManager.key_size, type = int)

    if key_size % 8 != 0:
        error = KeySizeError()
        return error.to_JSON(), error.status_code

    if extension_mandatory and not _KeyManager.does_support_mandatory(
        extensions_mandatory=extension_mandatory
    ):
        error = ExtensionMandatoryUnsupportedError()
        return error.to_JSON(), error.status_code
    
    key_container = _KeyManager.get_keys(slave_SAE_ID, key_size, amount_of_keys)
    
    logging.info(
        f"get_key()\n" +
        f"    slave_SAE_ID: {slave_SAE_ID}\n" +
        f"    size: {key_size}\n" +
        f"    number: {amount_of_keys}\n" +
        f"Result:\n" +
        f"    {key_container.__str__()}"
    )

    return key_container.to_JSON(), 200


@app.route("/api/v1/keys/<string:master_SAE_ID>/dec_key", methods=["GET", "POST"])
def get_keys_by_id(master_SAE_ID):
    slave_SAE_ID: str = request.headers.get('Host')
    key_container: KeyContainer = None
    key_ids: List[str] = []

    if request.method == "POST":
        data: object = request.get_json()
        key_ids = data.get("key_ids", [])
    else:
        key_id: str = request.args.get("key_id", default = "", type = str)
        key_ids.append(key_id) 

    key_container = _KeyManager.get_keys_with_ids(slave_SAE_ID, key_ids)
    logging.info(
        f"get_keys_by_id()\n" +
        f"    master_SAE_ID: {master_SAE_ID}\n" +
        f"    key_ids: \n" +
        f"      {key_ids}\n" +
        f"Result:\n" +
        f"    {key_container.__str__()}"
    )

    if key_container: 
        return key_container.to_JSON(), 200
    else:
        return jsonify({}), 400


@app.route("/api/v1/keys/<string:slave_ID>/status", methods=["GET"])
def get_status(slave_ID: str):
    return Status(
        source_KME_ID="AAAABBBBCCCCDDDD",
        target_KME_ID="EEEEFFFFGGGGHHHH",
        master_SAE_ID="master_SAE_ID_1",
        slave_SAE_ID="slave_SAE_ID_1",
        key_size=_KeyManager.key_size,
        stored_key_count=1000,#_KeyManager.stored_key_count(),
        max_key_count=_KeyManager.max_key_count,
        max_key_per_request=_KeyManager.max_key_per_request,
        min_key_size=_KeyManager.min_key_size,
        max_key_size=_KeyManager.max_key_size,
        max_SAE_ID_count=_KeyManager.max_SAE_ID_count,
        status_extension={},
    ).to_JSON()
