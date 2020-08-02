import pytest
import requests
from .conftest import BACKEND_BASE_URL
from .base import utils

# Можно было и не писать этот модуль тестов, 
# т.к. подобное поведение уже протестировано в test_smoke.py

TEST_TEMPLATES = [
   "etc/data_fixtures/element_boundary_values.yaml",
   "etc/data_fixtures/999.yml",
]



@pytest.mark.load_templates(TEST_TEMPLATES)
def test_templates_list(load_templates):
    response = requests.get(BACKEND_BASE_URL)
    assert response.status_code == 200

    tmpl_ids_list = [utils.get_tmpl_id_from_filename(filename) for filename in TEST_TEMPLATES]
    assert sorted(response.json()["templates"]) == sorted(tmpl_ids_list)


def test_empty_templates_list():
    response = requests.get(BACKEND_BASE_URL)
    assert response.status_code == 200
    assert response.json()["templates"] == []