import pytest
import requests
from .base import utils
from .conftest import BACKEND_BASE_URL
from urllib.parse import quote



TEST_TEMPLATES = [
   "etc/data_fixtures/999.yml",
   "etc/data_fixtures/element_boundary_values.yaml",
   "etc/data_fixtures/id_not_unique.yaml",
   "etc/data_fixtures/empty_str_in_link.yaml",
   "etc/data_fixtures/no_parent_id_in_tmpl.yaml",
   "etc/data_fixtures/not_link_at_all.yaml",
   "etc/data_fixtures/only_id.yaml",
   "etc/data_fixtures/only_lable.yaml"
]


TEST_SETUP = [
    {
        "test_description": "Шаблон есть в списке. Содержит 1 элемент только с обязательными параметрами",
        "tmpl_id": "999",
        "status_code_mock": 200,
        "file": "etc/data_fixtures/999.yml"
    },
    {
        "test_description": "Шаблон есть в списке. Содержит много валидных элементов с проверкой граничных значений",
        "tmpl_id": "element_boundary_values",
        "status_code_mock": 200,
        "file": "etc/data_fixtures/element_boundary_values.yaml"
    },
    # Дефект №9:
    pytest.param({
        "test_description": "Шаблон есть в списке. Содержит только id",
        "tmpl_id": "only_id",
        "status_code_mock": 400,
        "mock_message": "No \\\"label\\\" field in {'label': 'Только лэйбл'}"
    }, marks=pytest.mark.xfail),
    # Дефект №9:
    pytest.param({
        "test_description": "Шаблон есть в списке. Содержит только label",
        "tmpl_id": "only_lable",
        "status_code_mock": 400,
        "mock_message": "No \\\"id\\\" field in {'label': 'Только лэйбл'}"
    }, marks=pytest.mark.xfail),
    # Дефект №4:
    pytest.param({
        "test_description": "Шаблон есть в списке. Содержит повторяющиеся id",
        "tmpl_id": "id_not_unique",
        "status_code_mock": 400,
        "mock_message": "Element id should be unique"
    }, marks=pytest.mark.xfail),
    # Дефект №14:
    pytest.param({
        "test_description": "Шаблон есть в списке. Указан 'родительский' id, которого нет в списке",
        "tmpl_id": "no_parent_id_in_tmpl",
        "status_code_mock": 400,
        "mock_message_fragments": ["Dependency form", "is not presented in templat"]
    }, marks=pytest.mark.xfail),
    {
        "test_description": "Шаблон есть в списке. Содержит в качестве ссылки пустую строку",
        "tmpl_id": "empty_str_in_link",
        "status_code_mock": 200,
        "file": "etc/data_fixtures/empty_str_in_link.yaml"
    },
    {
        "test_description": "Шаблон есть в списке. Содержит в качестве ссылки int",
        "tmpl_id": "not_link_at_all",
        "status_code_mock": 200,
        "file": "etc/data_fixtures/not_link_at_all.yaml"
    },
    {
        "test_description": "Шаблон нет в списке.",
        "tmpl_id": "boo",
        "status_code_mock": 404
    }

]

@pytest.mark.load_templates(TEST_TEMPLATES)
@pytest.mark.parametrize("config", TEST_SETUP)
def test_install_template(load_templates, config):
    response = requests.post(f"{BACKEND_BASE_URL}/{quote(config['tmpl_id'])}/install")
    assert response.status_code == config["status_code_mock"]
    if response.status_code == 200:
        assert response.json() == utils.success_install(config["tmpl_id"])
        utils.check_success_install(config["file"])
    elif response.status_code == 404:
        response.json() == utils.success_install(config['tmpl_id'])
    elif response.status_code == 400:
        if "mock_message" in config:
            assert response.json()["message"] == config["mock_message"]
        elif "mock_message_fragments" in config:
            for fragment in config["mock_message_fragments"]:
                assert fragment in response.json()["message"]

# Проверка, что при перезагрузке на один и тот же tmpl_id разных файлов они перезгружаются
# (для этого нужна инсталляция и сверка содержания шаблона и страницы).
def test_reupload_template():
    tmpl_file1 = 'etc/data_fixtures/999.yml'
    tmpl_file2 = 'etc/data_fixtures/kapibara.yAMl'
    put_resp1 = requests.put(BACKEND_BASE_URL,files=[('file', open(tmpl_file1,'rb'))])
    assert put_resp1.status_code == 201

    post_resp1 = requests.post(f"{BACKEND_BASE_URL}/999/install")
    assert post_resp1.status_code == 200
    utils.check_success_install(tmpl_file1)

    put_resp2 = requests.put(BACKEND_BASE_URL,files=[('file', open(tmpl_file2,'rb')), ('data', (None, '{"tmpl_id":"999"}'))])
    assert put_resp2.status_code == 201

    post_resp2 = requests.post(f"{BACKEND_BASE_URL}/999/install")
    assert post_resp2.status_code == 200
    utils.check_success_install(tmpl_file2)



# Поведение требует уточнения. Мне кажется можно удалять инсталлированный шаблон, но он должен
# пропадать с главной страницы (этот тест проверяет именно такую реализацию).
# Или можно вообще запретить удаление инсталированного шаблона (тогда status_code = 400).
# В любом случае - здесь дефект.
# Дефект №5:
@pytest.mark.xfail
def test_delete_installed_template():
    tmpl_file = 'etc/data_fixtures/unexistent_link.yaml'
    put_resp = requests.put(BACKEND_BASE_URL,files=[('file', open(tmpl_file,'rb'))])
    assert put_resp.status_code == 201
    
    post_resp = requests.post(f"{BACKEND_BASE_URL}/unexistent_link/install")
    assert post_resp.status_code == 200
    utils.check_success_install(tmpl_file)

    del_resp = requests.delete(f"{BACKEND_BASE_URL}/unexistent_link")
    assert del_resp.status_code == 200
    utils.check_no_template_installed()

