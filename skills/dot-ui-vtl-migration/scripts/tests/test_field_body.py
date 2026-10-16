"""`field-body` builds the PUT body for a field update. The v3 update replaces the field's
variables wholesale, so what matters is that nothing else is dropped."""

import json

import pytest

import vtl_migration as vm
from test_workflow import DA_ID, INLINE_MIGRATED, LEGACY, download, field, migrate, write_meta, write_scan

OTHER_VARIABLE = {"clazz": vm.FIELD_VARIABLE_CLAZZ, "key": "keepMe", "value": "42", "id": "v1", "fieldId": "f-legacy"}


def fetched(values=LEGACY, variables=None):
    return {"id": "f-legacy", "variable": "legacy", "values": values, "fieldVariables": variables or [], "required": True}


def write_field(workdir, **kwargs):
    path = workdir / "fetched.json"
    path.write_text(json.dumps(fetched(**kwargs)))
    return path


@pytest.fixture
def instance(tmp_path):
    write_scan(
        tmp_path,
        field("A", "legacy", LEGACY),
        field("A", "viaAsset", f'#dotParse("/dA/{DA_ID}")'),
    )
    write_meta(tmp_path)
    vm.cmd_classify(tmp_path)
    vm.cmd_assets_plan(tmp_path)
    download(tmp_path)
    vm.cmd_build_manifest(tmp_path, None)
    migrate(tmp_path, "fields/A.legacy.vtl", INLINE_MIGRATED)
    return tmp_path


def test_a_field_gets_the_migrated_code_and_component_mode(instance):
    result = vm.cmd_field_body(instance, "A.legacy", write_field(instance))
    updated = result["body"]["field"]
    assert result["verdict"] == "ok"
    assert updated["values"] == INLINE_MIGRATED
    assert [(v["key"], v["value"]) for v in updated["fieldVariables"]] == [("newRenderMode", "component")]
    assert updated["required"] is True


def test_every_other_field_variable_is_kept(instance):
    result = vm.cmd_field_body(instance, "A.legacy", write_field(instance, variables=[OTHER_VARIABLE]))
    keys = [v["key"] for v in result["body"]["field"]["fieldVariables"]]
    assert keys == ["keepMe", "newRenderMode"]


def test_an_existing_render_mode_variable_is_updated_not_duplicated(instance):
    existing = {"clazz": vm.FIELD_VARIABLE_CLAZZ, "key": "newRenderMode", "value": "iframe", "id": "keep-this-id", "fieldId": "f-legacy"}
    result = vm.cmd_field_body(instance, "A.legacy", write_field(instance, variables=[existing, OTHER_VARIABLE]))
    flags = [v for v in result["body"]["field"]["fieldVariables"] if v["key"] == "newRenderMode"]
    assert len(flags) == 1 and flags[0]["value"] == "component" and flags[0]["id"] == "keep-this-id"


def test_a_field_changed_on_the_server_since_download_is_skipped(instance):
    result = vm.cmd_field_body(instance, "A.legacy", write_field(instance, values=LEGACY + " // edited"))
    assert result["verdict"] == "skipped" and "changed on the server" in result["reason"]
    assert "body" not in result


def test_a_render_mode_switch_changes_only_the_variable(instance):
    code = "<p>already migrated code</p>"
    result = vm.cmd_field_body(instance, "A.viaAsset", write_field(instance, values=code, variables=[OTHER_VARIABLE]))
    updated = result["body"]["field"]
    assert updated["values"] == code
    assert [v["key"] for v in updated["fieldVariables"]] == ["keepMe", "newRenderMode"]


def test_a_render_mode_switch_is_skipped_when_already_component(instance):
    flag = {"clazz": vm.FIELD_VARIABLE_CLAZZ, "key": "newRenderMode", "value": "component", "id": "x", "fieldId": "f-legacy"}
    result = vm.cmd_field_body(instance, "A.viaAsset", write_field(instance, variables=[flag]))
    assert result["verdict"] == "skipped" and "already" in result["reason"]


def test_the_input_field_is_not_modified_in_place(instance):
    original = fetched(variables=[OTHER_VARIABLE])
    vm.with_component_render_mode(original)
    assert original["fieldVariables"] == [OTHER_VARIABLE]


def test_an_asset_entry_is_refused(instance):
    with pytest.raises(vm.InputError):
        vm.cmd_field_body(instance, DA_ID, write_field(instance))


def test_a_field_file_without_an_id_is_refused(instance):
    path = instance / "bad.json"
    path.write_text(json.dumps({"values": LEGACY}))
    with pytest.raises(vm.InputError):
        vm.cmd_field_body(instance, "A.legacy", path)


def test_the_cli_prints_the_body(instance, capsys):
    path = write_field(instance)
    assert vm.main(["--workdir", str(instance), "field-body", "A.legacy", "--field-file", str(path)]) == 0
    assert json.loads(capsys.readouterr().out)["body"]["field"]["values"] == INLINE_MIGRATED
