# -----------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for license information.
# -----------------------------------------------------------------------------------------

from flask import Flask, jsonify, request
from model import Status, KeyManagementEntity
from errors import KeySizeError, ExtensionMandatoryUnsupportedError


app = Flask(__name__)
_KeyManager = KeyManagementEntity(
    id="AAAABBBBCCCCDDDD",
    key_size=352,
    max_key_count=1024,
    max_key_per_request=128,
    min_key_size=64,
    max_key_size=1024,
    max_SAE_ID_count=10,
)


@app.route("/")
def hello():
    return app.send_static_file("index.html")


@app.route("/api/v1/keys/<string:slave_SAE_ID>/enc_key", methods=["GET", "POST"])
def get_key(slave_SAE_ID):
    extension_mandatory = None
    extension_optional = None
    additional_slave_SAE_IDs = None
    amount_of_keys = 0

    if request.method == "POST":
        data = request.get_json()

        amount_of_keys = int(data.get("number", 1))
        key_size = int(data.get("size", _KeyManager.key_size))
        additional_slave_SAE_IDs = data.get("additional_slave_SAE_IDs", [])
        extension_mandatory = data.get("extension_mandatory", [])
        extension_optional = data.get("extension_optional", [])
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
    print(_KeyManager.get_keys(slave_SAE_ID, key_size, amount_of_keys))
    return jsonify(_KeyManager.get_keys(slave_SAE_ID, key_size, amount_of_keys)), 200


@app.route("/api/v1/keys/<string:master_SAE_ID>/dec_key", methods=["GET", "POST"])
def get_keys_by_id(master_SAE_ID):
    keys = None
    if request.method == "POST":
        data = request.get_json()

        amount_of_keys = data.get("number", 1)
    else:
        key_id = request.args.get("key_id", default = "", type = str)
        keys = _KeyManager.get_keys_with_ids([key_id])

    if keys: 
        return jsonify(keys), 200
    else:
        return jsonify({}), 400


@app.route("/api/v1/keys/<string:slave_ID>/status", methods=["GET"])
def get_status(slave_ID: str):
    return Status(
        source_KME_ID="AAAABBBBCCCCDDDD",
        target_KME_ID="EEEEFFFFGGGGHHHH",
        master_SAE_ID="IIIIJJJJKKKKLLLL",
        slave_SAE_ID="MMMMNNNNOOOOPPPP",
        key_size=_KeyManager.key_size,
        stored_key_count=1000,#_KeyManager.stored_key_count(),
        max_key_count=_KeyManager.max_key_count,
        max_key_per_request=_KeyManager.max_key_per_request,
        min_key_size=_KeyManager.min_key_size,
        max_key_size=_KeyManager.max_key_size,
        max_SAE_ID_count=_KeyManager.max_SAE_ID_count,
        status_extension={},
    ).to_JSON()
