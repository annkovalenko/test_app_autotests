import pytest
import requests
from .base import utils
from .conftest import BACKEND_BASE_URL
from urllib.parse import quote

TEST_TEMPLATES = [
   "etc/data_fixtures/Lambrusco.yml",
   "etc/data_fixtures/999.yml",
   "etc/data_fixtures/kapibara.yAMl"
]

TEST_SETUP = [
    pytest.param({
        # Дефект №2
        "test_description": "Шаблон есть в списке. Шаблон не инсталлирован. tmpl_id = латиница",
        "tmpl_id": "Lambrusco",
        "status_code_mock": 200
    }, marks=pytest.mark.xfail),
    {
        "test_description": "Шаблон есть в списке. Шаблон не инсталлирован. tmpl_id = цифры",
        "tmpl_id": "999",
        "status_code_mock": 200
    },
    {
        "test_description": "Шаблон есть в списке. Шаблон не инсталлирован. При загрузке в расширении верхний регистр",
        "tmpl_id": "kapibara",
        "status_code_mock": 200
    },
    {
        "test_description": "Шаблона нет в списке.",
        "tmpl_id": "mark",
        "status_code_mock": 404
    },
    {
        "test_description": "Шаблона нет в списке. tmpl_id = пробел",
        "tmpl_id": " ",
        "status_code_mock": 404
    }  
]

# Тест на удалени инсталлированного шаблона вынесен в test_install_template.py, т.к. невозможен без инсталляции.

@pytest.mark.parametrize("config", TEST_SETUP)
@pytest.mark.load_templates(TEST_TEMPLATES)
def test_delete_template(load_templates, config):
    response = requests.delete(f"{BACKEND_BASE_URL}/{quote(config['tmpl_id'])}")
    assert response.status_code == config["status_code_mock"]
    
    if response.status_code == 200:
        assert response.json() == utils.success_delete(config["tmpl_id"])
    
    elif response.status_code == 404:
        assert response.json() == utils.not_found_message(config["tmpl_id"])
        