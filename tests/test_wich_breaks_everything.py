import pytest
import requests
from .base import utils
from .conftest import BACKEND_BASE_URL
from urllib.parse import quote


TEST_SETUP = [
    {
        "test_description": "",
        "payload": {"file": ('!@#$%.yml', open('etc/data_fixtures/!@#$%.yml', 'rb'))},
        "tmpl_id": "!@#$%"
    },
    {
        "test_description": "",
        "payload": {"file": ('😺.yaml', open('etc/data_fixtures/😺.yaml', 'rb'))},
        "tmpl_id": "😺"
    },
    {
        "test_description": "",
        "payload": {"file": ('шаблон.yaml', open('etc/data_fixtures/шаблон.yaml', 'rb'))},
        "tmpl_id": "шаблон"
    }
]

# Дефект №3:
@pytest.mark.skip(reason='''После загрузки файла, название которого содержит кириллицу/спецсимволы/эмоджи 
на списке шаблонов он отображается с tmpl_id = yaml, а не названием переданного файла. 
Это делает загруженный файл неудаляемым и не инсталлируемым (т.к. в реальности такого имени нет).
Фикстура для очистки становится бесполезной''')
@pytest.mark.parametrize("config", TEST_SETUP)
def test_upload_and_delete_error(config):
    response = requests.put(BACKEND_BASE_URL, files = config["payload"])
    assert response.status_code == 200
    assert response.json() == utils.success_upload(config["tmpl_id"])

    tmpl_ids_list = requests.get(BACKEND_BASE_URL)
    assert tmpl_ids_list.status_code == 200
    assert config["tmpl_id"] in tmpl_ids_list.json()["templates"]

    install_resp = requests.post(f"{BACKEND_BASE_URL}/{quote(config['tmpl_id'])}/install")
    assert install_resp.status_code == 200
    assert response.json() == utils.success_install(config["tmpl_id"])

    del_response = requests.delete(f"{BACKEND_BASE_URL}/{quote(config['tmpl_id'])}")
    assert del_response.json() == utils.success_delete(config["tmpl_id"])
    