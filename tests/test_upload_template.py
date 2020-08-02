import pytest
import requests
from .conftest import BACKEND_BASE_URL
from .base import utils

import logging
from http.client import HTTPConnection


TEST_SETUP = [
    {
        "test_description": "Загрузка шаблона: только file. Название файла = латиница. Шаблон валидный. Все граничные значения элементов",
        "body": {
            "file": (open('etc/data_fixtures/element_boundary_values.yaml', 'rb'))
        },
        "expected_tmpl_id": "element_boundary_values",
        "status_code_mock": 201
    },
    {
        "test_description": "Загрузка шаблона: названия файла. Цифры + расширение .yml",
        "body": {
            "file": (open('etc/data_fixtures/999.yml', 'rb'))
        },
        "expected_tmpl_id": "999",
        "status_code_mock": 201
    },
    # Тесты с названиями файлов = спецсимволы/кириллица/эмоджи вынесены в отдельный модуль
    # test_wich_breaks_everything.py,т.к. их починку надо проверять комплексно
    {
        "test_description": "Загрузка шаблона: регистроНЕзависимость расширения",
        "body": {
            "file": (open('etc/data_fixtures/kapibara.yAMl', 'rb'))
        },
        "expected_tmpl_id": "kapibara",
        "status_code_mock": 201
    },
    {
        "test_description": "Загрузка шаблона: недопустимое расширение",
        "body": {
            "file": (open('etc/data_fixtures/text.txt', 'rb'))
        },
        "mock_message": ["Allowed file types are {'yml', 'yaml'}", "Allowed file types are {'yaml', 'yml'}"],
        "status_code_mock": 400
    },
    {
        "test_description": "Загрузка шаблона: не передан ключ file",
        "body": None,
        "mock_message": "No file part in the request",
        "status_code_mock": 400
    },
    {
        "test_description": "Загрузка шаблона: не передан шаблон в file",
        "body": {"file": ("", "")},
        "mock_message": "No file selected for uploading",
        "status_code_mock": 400
    },
    # Дефект №1
    pytest.param({
        "test_description": "Загрузка шаблона: название файла с верхним регистром",
        "body": {
            "file": (open('etc/data_fixtures/Lambrusco.yml', 'rb'))
        },
        "expected_tmpl_id": "Lambrusco",
        "status_code_mock": 201
    }, marks=pytest.mark.xfail),
    {
        "test_description": "Загрузка шаблона: файл с таким именем уже был загружен (должен один раз встречаться в списке) + расширение .yaml",
        "body": {
            "file": (open('etc/data_fixtures/element_boundary_values.yaml', 'rb'))
        },
        "expected_tmpl_id": "element_boundary_values",
        "status_code_mock": 201
    },
    {
        "test_description": "Загрузка шаблона: Имя файла = tmpl_id. В link передан int",
        "body": {
            "file": (open('etc/data_fixtures/not_link_at_all.yaml', 'rb')),
            "data": (None, '{"tmpl_id":"not_link_at_all"}')
        },
        "expected_tmpl_id": "not_link_at_all",
        "status_code_mock": 201
    },
    {
        "test_description": "Загрузка шаблона: file + data (валидные). Имя файла != tmpl_id. Файл с таким именем ранее загружали",
        "body": {
            "file": (open('etc/data_fixtures/999.yml', 'rb')),
            "data": (None, '{"tmpl_id":"1"}')
        },
        "expected_tmpl_id": "1",
        "status_code_mock": 201
    },
    # Дефект №1:
    pytest.param({
        "test_description": "Загрузка шаблона: Имя файла != tmpl_id; tmpl_id = латиница с верхним регистром",
        "body": {
            "file": (open('etc/data_fixtures/999.yml', 'rb')),
            "data": (None, '{"tmpl_id":"Foo"}')
        },
        "expected_tmpl_id": "Foo",
        "status_code_mock": 201
    }, marks=pytest.mark.xfail),
    {
        "test_description": "Загрузка шаблона: Имя файла != tmpl_id; tmpl_id = кириллица. В link пустая строка",
        "body": {
            "file": (open('etc/data_fixtures/empty_str_in_link.yaml', 'rb')),
            "data": (None, '{"tmpl_id":"кот"}')
        },
        "expected_tmpl_id": "кот",
        "status_code_mock": 201
    },
    {
        "test_description": "Загрузка шаблона: Имя файла != tmpl_id; tmpl_id = спецсимволы",
        "body": {
            "file": (open('etc/data_fixtures/999.yml', 'rb')),
            "data": (None, '{"tmpl_id":"!@#"}')
        },
        "expected_tmpl_id": "!@#",
        "status_code_mock": 201
    },
    # Дефект №7
    pytest.param({
        "test_description": "Загрузка шаблона: Имя файла != tmpl_id; tmpl_id = 251 символ",
        "body": {
            "file": (open('etc/data_fixtures/999.yml', 'rb')),
            "data": (None, '{"tmpl_id":"%s"}' % "1"*251)
        },
        "mock_message": "Allowed tmpl_id lenght is 100 characters or less",
        "status_code_mock": 400
    }, marks=pytest.mark.xfail),
    {
    # Улучшение №6
        "test_description": "Загрузка нескольких файлов одновременно + несуществующая ссылка в элменете",
        "body": [
            ('file', open('etc/data_fixtures/unexistent_link.yaml','rb')),
            ('file', open('etc/data_fixtures/999.yml','rb'))
            ],
        "expected_tmpl_id": "unexistent_link",
        "status_code_mock": 201
    },
    {   
    # Улучшение №8
        "test_description": "Загрузка шаблона: валидация внутри шаблона = не уникальный id",
        "body": {
            "file": (open('etc/data_fixtures/id_not_unique.yaml', 'rb'))
        },
        "expected_tmpl_id": "id_not_unique",
        "status_code_mock": 201
    },
    {   
    # Улучшение №8
        "test_description": "Загрузка шаблона: валидация внутри шаблона = нет переданного родительскл элемента",
        "body": {
            "file": (open('etc/data_fixtures/no_parent_id_in_tmpl.yaml', 'rb'))
        },
        "expected_tmpl_id": "no_parent_id_in_tmpl",
        "status_code_mock": 201
    },
    {   
    # Улучшение №8:
        "test_description": "Загрузка шаблона: валидация внутри шаблона = не передан lable",
        "body": {
            "file": (open('etc/data_fixtures/only_id.yaml', 'rb'))
        },
        "expected_tmpl_id": "only_id",
        "status_code_mock": 201
    },
    {   
    # Улучшение №8:
        "test_description": "Загрузка шаблона: валидация внутри шаблона = не передан id",
        "body": {
            "file": (open('etc/data_fixtures/only_lable.yaml', 'rb'))
        },
        "expected_tmpl_id": "only_lable",
        "status_code_mock": 201
    },
    # Дефект № 10:
    pytest.param({
        "test_description": "Загрузка шаблона: очень большой файл",
        "body": {
            "file": (open('etc/data_fixtures/very_big_file.yaml', 'rb'))
        },
        "mock_message": "Maximum allowed file size [size] bytes",
        "status_code_mock": 400
    }, marks=pytest.mark.xfail),
    # Дефект № 11:
    pytest.param({   
        "test_description": "Загрузка шаблона: в качестве идентификатора передана пустая строка",
        "body": {
            "file": (open('etc/data_fixtures/999.yml', 'rb')),
            "data": (None, '{"tmpl_id":""}')
        },
        "mock_message": "tmpl_id value could not be empty",
        "status_code_mock": 400
    }, marks=pytest.mark.skip(reason="Без исправления после загрузки такой шаблон нельзя удалить")),
    # Дефект №12:
    pytest.param({
        "test_description": "Загрузка шаблона: валидация data - не передан tmpl_id",
        "body": {
            "file": (open('etc/data_fixtures/999.yml', 'rb')),
            "data": (None, '{}')
        },
        "mock_message": "For data tmpl_id is required",
        "status_code_mock": 400
    }, marks=pytest.mark.skip(reason="Без исправления после загрузки такой шаблон нельзя удалить")),
    # Дефект №13:
    pytest.param({
        "test_description": "Загрузка шаблона: в data не JSON",
        "body": {
            "file": (open('etc/data_fixtures/999.yml', 'rb')),
            "data": (None, 'hrgolrh')
        },
        "mock_message": "Not valid JSON in data",
        "status_code_mock": 400
    }, marks=pytest.mark.xfail),
    # Улучшение №14:
    {
        "test_description": "Загрузка шаблона: дважды передан tmpl_id (с разными значениями)",
        "body": {
            "file": (open('etc/data_fixtures/999.yml', 'rb')),
            "data": (None, '{"tmpl_id":"1", "tmpl_id":"2"}')
        },
        "expected_tmpl_id": "2",
        "status_code_mock": 201
    }
]



@pytest.mark.parametrize("config", TEST_SETUP)
def test_upload_template(config):
    response = requests.put(BACKEND_BASE_URL,files=config["body"])

    assert response.status_code == config["status_code_mock"]
    if response.status_code == 201:
        assert response.json() == utils.success_upload(config["expected_tmpl_id"])
        
        get_info = requests.get(BACKEND_BASE_URL)
        assert get_info.status_code == 200
        assert config['expected_tmpl_id'] in get_info.json()["templates"]
        assert get_info.json()["templates"].count(config['expected_tmpl_id']) == 1
    elif response.status_code == 400:
        assert response.json()["message"] in config["mock_message"]