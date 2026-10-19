"""End-to-end coverage of the local workflow: classify -> assets-plan -> build-manifest ->
check -> payload -> record. No network: the tests write the files the agent would write."""

import base64
import json

import pytest

import vtl_migration as vm

LEGACY = "<script>dojo.ready(function(){ dijit.byId('x'); });</script>"
INLINE_MIGRATED = "#if( $structures.isNewEditModeEnabled() )\n<p>new</p>\n#else\n" + LEGACY + "\n#end"
DA_ID = "0ec62ffd3666f23fc5228ef84a481b09"


def field(type_, name, values, component=False):
    return {"type": type_, "typeId": f"t-{type_}", "field": name, "fieldId": f"f-{name}", "values": values, "component": component}


def write_scan(workdir, *records):
    (workdir / "scan").mkdir(parents=True, exist_ok=True)
    (workdir / "scan" / "part-1.json").write_text(json.dumps(list(records)))


def write_meta(workdir, da_id=DA_ID, **overrides):
    meta = {
        "identifier": da_id,
        "inode": "inode-1",
        "languageId": 1,
        "contentType": "dotAsset",
        "live": True,
        "fileName": "count.vtl",
        "binaryField": "asset",
        **overrides,
    }
    (workdir / "assets").mkdir(parents=True, exist_ok=True)
    (workdir / "assets" / f"{da_id}.json").write_text(json.dumps(meta))


def download(workdir, name="count.vtl", text=LEGACY, da_id=DA_ID):
    path = workdir / "original" / "assets" / f"{da_id}__{name}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def build(workdir):
    vm.cmd_classify(workdir)
    vm.cmd_assets_plan(workdir)
    return vm.cmd_build_manifest(workdir, "demo.dotcms.dev")


def test_classify_sorts_every_category(tmp_path):
    write_scan(
        tmp_path,
        field("A", "viaAsset", f'#dotParse("/dA/{DA_ID}")'),
        field("A", "other", '#dotParse("/application/x.vtl")'),
        field("A", "core", "$velutil.mergeTemplate('/static/personas/x.vtl')"),
        field("A", "done", INLINE_MIGRATED),
        field("A", "legacy", LEGACY),
        field("A", "clean", "<p>hello</p>"),
    )
    result = vm.cmd_classify(tmp_path)
    assert result["counts"] == {
        "customFields": 6,
        "assetReferences": 1,
        "inlineLegacy": 1,
        "alreadyMigratedInline": 1,
        "coreFiles": 1,
        "inlineClean": 1,
        "otherPaths": 1,
    }
    assert result["assetsToResolve"] == [DA_ID]
    assert (tmp_path / "original" / "fields" / "A.legacy.vtl").read_text() == LEGACY


def test_classify_ignores_a_field_sent_twice(tmp_path):
    write_scan(tmp_path, field("A", "legacy", LEGACY), field("A", "legacy", LEGACY))
    assert vm.cmd_classify(tmp_path)["counts"]["customFields"] == 1


def test_classify_rejects_a_record_missing_ids(tmp_path):
    write_scan(tmp_path, {"type": "A", "field": "x", "values": LEGACY})
    with pytest.raises(vm.InputError):
        vm.cmd_classify(tmp_path)


def test_classify_neutralizes_path_traversal_in_variables(tmp_path):
    write_scan(tmp_path, field("../../etc", "passwd", LEGACY))
    vm.cmd_classify(tmp_path)
    assert (tmp_path / "original" / "fields" / ".._.._etc.passwd.vtl").exists()
    assert not (tmp_path.parent / "etc").exists()


def test_assets_plan_reports_unresolved_pinned_and_downloads(tmp_path):
    write_scan(
        tmp_path,
        field("A", "ok", f'#dotParse("/dA/{DA_ID}")'),
        field("A", "pinned", '#dotParse("/dA/pinned-inode")'),
        field("A", "missing", '#dotParse("/dA/nope")'),
        field("A", "noname", '#dotParse("/dA/noname")'),
    )
    write_meta(tmp_path)
    write_meta(tmp_path, "pinned-inode", identifier="the-identifier")
    write_meta(tmp_path, "noname", fileName=None)
    vm.cmd_classify(tmp_path)
    plan = vm.cmd_assets_plan(tmp_path)
    assert [d["id"] for d in plan["toDownload"]] == [DA_ID]
    assert plan["toDownload"][0]["destination"].endswith(f"original/assets/{DA_ID}__count.vtl")
    assert len(plan["pinned"]) == 1 and "the-identifier" in plan["pinned"][0]
    assert len(plan["unresolved"]) == 2


def test_assets_plan_neutralizes_a_hostile_file_name(tmp_path):
    write_scan(tmp_path, field("A", "ok", f'#dotParse("/dA/{DA_ID}")'))
    write_meta(tmp_path, fileName="../../evil.vtl")
    vm.cmd_classify(tmp_path)
    plan = vm.cmd_assets_plan(tmp_path)
    assert plan["toDownload"][0]["file"] == f"assets/{DA_ID}__.._.._evil.vtl"


def test_build_manifest_queues_assets_fields_and_render_mode(tmp_path):
    write_scan(
        tmp_path,
        field("A", "viaAsset", f'#dotParse("/dA/{DA_ID}")'),
        field("A", "legacy", LEGACY),
        field("A", "done", INLINE_MIGRATED),
    )
    write_meta(tmp_path)
    vm.cmd_classify(tmp_path)
    vm.cmd_assets_plan(tmp_path)
    download(tmp_path)
    result = vm.cmd_build_manifest(tmp_path, "demo.dotcms.dev")
    assert result["counts"]["pending"] == 2
    assert [e["kind"] for e in result["entries"]] == ["asset", "field", "renderMode", "renderMode"]
    by_key = {e["key"]: e for e in result["entries"] if e["kind"] == "renderMode"}
    assert by_key["A.viaAsset"]["requires"] == [DA_ID]
    assert by_key["A.done"]["requires"] == []


def test_build_manifest_flags_a_failed_download_and_an_already_migrated_file(tmp_path):
    write_scan(tmp_path, field("A", "one", f'#dotParse("/dA/{DA_ID}")'), field("A", "two", '#dotParse("/dA/other")'))
    write_meta(tmp_path)
    write_meta(tmp_path, "other", fileName="done.vtl")
    vm.cmd_classify(tmp_path)
    vm.cmd_assets_plan(tmp_path)
    download(tmp_path, "done.vtl", INLINE_MIGRATED, "other")  # DA_ID never downloaded
    result = vm.cmd_build_manifest(tmp_path, None)
    assert result["counts"]["unresolved"] == 1
    assert result["counts"]["pending"] == 0
    manifest = vm.read_manifest(tmp_path)
    assert manifest["knownMigrated"] == {"other": "inode-1"}


def test_render_mode_is_skipped_when_the_field_already_uses_component_mode(tmp_path):
    write_scan(tmp_path, field("A", "done", INLINE_MIGRATED, component=True))
    vm.cmd_classify(tmp_path)
    vm.cmd_assets_plan(tmp_path)
    assert vm.cmd_build_manifest(tmp_path, None)["counts"]["renderMode"] == 0


def test_render_mode_is_skipped_for_a_field_with_an_unhandled_path(tmp_path):
    write_scan(tmp_path, field("A", "mixed", f'#dotParse("/dA/{DA_ID}") #dotParse("/application/x.vtl")'))
    write_meta(tmp_path)
    vm.cmd_classify(tmp_path)
    vm.cmd_assets_plan(tmp_path)
    download(tmp_path)
    assert vm.cmd_build_manifest(tmp_path, None)["counts"]["renderMode"] == 0


def migrate(workdir, relative, text):
    path = workdir / "migrated" / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


@pytest.fixture
def instance(tmp_path):
    write_scan(tmp_path, field("A", "viaAsset", f'#dotParse("/dA/{DA_ID}")'), field("A", "legacy", LEGACY))
    write_meta(tmp_path)
    vm.cmd_classify(tmp_path)
    vm.cmd_assets_plan(tmp_path)
    download(tmp_path)
    vm.cmd_build_manifest(tmp_path, "demo.dotcms.dev")
    return tmp_path


def verdicts(result):
    return {e["key"]: e["verdict"] for e in result["entries"]}


def test_check_waits_for_files_that_are_not_migrated_yet(instance):
    result = vm.cmd_check(instance, [], False, False)
    assert verdicts(result) == {DA_ID: "waiting", "A.legacy": "waiting", "A.viaAsset": "waiting"}


def test_check_accepts_a_genuine_inline_migration(instance):
    migrate(instance, "fields/A.legacy.vtl", INLINE_MIGRATED)
    result = vm.cmd_check(instance, ["A.legacy"], False, False)
    entry = result["entries"][0]
    assert entry["verdict"] == "ready"
    assert entry["action"] == {"type": "update-field", "typeId": "t-A", "fieldId": "f-legacy"}


def test_check_skips_and_records_a_migration_that_loses_the_original(instance):
    migrate(instance, "fields/A.legacy.vtl", "#if( $structures.isNewEditModeEnabled() )\n<p>new</p>\n#else\n<p>edited</p>\n#end")
    result = vm.cmd_check(instance, ["A.legacy"], False, False)
    assert result["entries"][0]["verdict"] == "skipped"
    assert "verbatim" in result["entries"][0]["reason"]
    entry = next(e for e in vm.read_manifest(instance)["entries"] if e["key"] == "A.legacy")
    assert entry["status"] == "skipped"


def test_check_dry_run_does_not_record_anything(instance):
    migrate(instance, "fields/A.legacy.vtl", "not a migration")
    vm.cmd_check(instance, ["A.legacy"], True, False)
    entry = next(e for e in vm.read_manifest(instance)["entries"] if e["key"] == "A.legacy")
    assert entry["status"] == "pending"


def test_check_skips_a_file_identical_to_the_original(instance):
    migrate(instance, "fields/A.legacy.vtl", LEGACY)
    assert vm.cmd_check(instance, ["A.legacy"], False, False)["entries"][0]["reason"] == "migrated file is identical to original"


def test_one_bad_item_does_not_block_the_rest(instance):
    migrate(instance, "fields/A.legacy.vtl", "garbage")
    migrate(instance, f"assets/{DA_ID}__count.vtl", INLINE_MIGRATED)
    result = vm.cmd_check(instance, [DA_ID, "A.legacy"], False, False)
    assert verdicts(result)[DA_ID] == "ready"
    assert verdicts(result)["A.legacy"] == "skipped"


def test_selecting_an_asset_pulls_in_its_render_mode_switch(instance):
    result = vm.cmd_check(instance, [DA_ID], False, False)
    assert set(verdicts(result)) == {DA_ID, "A.viaAsset"}


def test_render_mode_waits_until_its_asset_is_published(instance):
    migrate(instance, f"assets/{DA_ID}__count.vtl", INLINE_MIGRATED)
    first = vm.cmd_check(instance, [DA_ID], False, False)
    assert verdicts(first) == {DA_ID: "ready", "A.viaAsset": "waiting"}
    vm.cmd_record(instance, DA_ID, "published", None, "inode-2")
    second = vm.cmd_check(instance, [DA_ID], False, False)
    assert verdicts(second) == {DA_ID: "done", "A.viaAsset": "ready"}


def test_dry_run_treats_a_ready_asset_as_published_for_its_render_mode(instance):
    migrate(instance, f"assets/{DA_ID}__count.vtl", INLINE_MIGRATED)
    result = vm.cmd_check(instance, [DA_ID], True, False)
    assert verdicts(result) == {DA_ID: "ready", "A.viaAsset": "ready"}


def test_finished_entries_are_not_reprocessed_unless_retried(instance):
    migrate(instance, "fields/A.legacy.vtl", INLINE_MIGRATED)
    vm.cmd_record(instance, "A.legacy", "published", None, None)
    assert vm.cmd_check(instance, [], False, False)["counts"].get("done") is None  # not selected without --only
    assert vm.cmd_check(instance, ["A.legacy"], False, False)["entries"][0]["verdict"] == "done"
    assert vm.cmd_check(instance, ["A.legacy"], False, True)["entries"][0]["verdict"] == "ready"


def test_check_warns_when_only_matches_nothing(instance):
    assert "matched none" in vm.cmd_check(instance, ["nope"], False, False)["warning"]


def test_payload_for_an_asset_carries_the_migrated_bytes(instance):
    migrate(instance, f"assets/{DA_ID}__count.vtl", INLINE_MIGRATED)
    payload = vm.cmd_payload(instance, DA_ID)
    assert base64.b64decode(payload["contentBase64"]).decode() == INLINE_MIGRATED
    assert payload["binaryField"] == "asset" and payload["expectedInode"] == "inode-1"


def test_payload_for_a_field_carries_only_ids(instance):
    migrate(instance, "fields/A.legacy.vtl", INLINE_MIGRATED)
    payload = vm.cmd_payload(instance, "A.legacy")
    assert payload["type"] == "update-field" and "migrated" not in payload and "contentBase64" not in payload


def test_payload_without_a_migrated_file_is_an_input_error(instance):
    with pytest.raises(vm.InputError):
        vm.cmd_payload(instance, "A.legacy")


def test_record_a_published_asset_requires_and_stores_the_new_inode(instance):
    with pytest.raises(vm.InputError):
        vm.cmd_record(instance, DA_ID, "published", None, None)
    vm.cmd_record(instance, DA_ID, "published", None, "inode-2")
    entry = next(e for e in vm.read_manifest(instance)["entries"] if e["key"] == DA_ID)
    assert (entry["status"], entry["inode"], entry["previousInode"]) == ("published", "inode-2", "inode-1")


def test_a_published_asset_is_not_downloaded_again_on_a_later_run(instance):
    vm.cmd_record(instance, DA_ID, "published", None, "inode-2")
    write_meta(instance, inode="inode-2")
    vm.cmd_classify(instance)
    plan = vm.cmd_assets_plan(instance)
    assert plan["toDownload"] == []
    assert len(plan["alreadyMigrated"]) == 1


def test_status_counts_entries(instance):
    vm.cmd_record(instance, "A.legacy", "failed", "boom", None)
    result = vm.cmd_status(instance)
    assert result["counts"] == {"pending": 2, "failed": 1}


def test_manifest_write_is_atomic_and_leaves_no_temp_file(instance):
    vm.cmd_record(instance, "A.legacy", "failed", "boom", None)
    assert not list(instance.glob("*.tmp"))
    json.loads((instance / "manifest.json").read_text())


def test_cli_prints_one_json_document_and_exits_2_on_bad_input(tmp_path, capsys):
    assert vm.main(["--workdir", str(tmp_path), "status"]) == 2
    assert "error" in json.loads(capsys.readouterr().err)
    write_scan(tmp_path, field("A", "legacy", LEGACY))
    assert vm.main(["--workdir", str(tmp_path), "classify"]) == 0
    assert json.loads(capsys.readouterr().out)["command"] == "classify"


# ─── regressions found in review ─────────────────────────────────────────


def test_rebuilding_the_manifest_keeps_the_progress_already_made(instance):
    vm.cmd_record(instance, "A.legacy", "failed", "boom", None)
    vm.cmd_record(instance, DA_ID, "skipped", "changed", None)
    vm.cmd_classify(instance)
    vm.cmd_assets_plan(instance)
    vm.cmd_build_manifest(instance, "demo.dotcms.dev")
    by_key = {e["key"]: e for e in vm.read_manifest(instance)["entries"]}
    assert (by_key["A.legacy"]["status"], by_key["A.legacy"]["statusReason"]) == ("failed", "boom")
    assert by_key[DA_ID]["status"] == "skipped"
    assert by_key["A.viaAsset"]["status"] == "pending"


def test_a_new_version_of_a_published_asset_starts_over_as_pending(instance):
    vm.cmd_record(instance, DA_ID, "published", None, "inode-2")
    write_meta(instance, inode="inode-3")  # edited on the server after publishing: queued again
    vm.cmd_classify(instance)
    vm.cmd_assets_plan(instance)
    download(instance)
    vm.cmd_build_manifest(instance, None)
    entry = next(e for e in vm.read_manifest(instance)["entries"] if e["key"] == DA_ID)
    assert entry["inode"] == "inode-3" and entry["status"] == "pending"
    assert "previousInode" not in entry


def test_a_skipped_asset_keeps_its_status_while_the_inode_is_unchanged(instance):
    vm.cmd_record(instance, DA_ID, "skipped", "changed", None)
    vm.cmd_classify(instance)
    vm.cmd_assets_plan(instance)
    vm.cmd_build_manifest(instance, None)
    entry = next(e for e in vm.read_manifest(instance)["entries"] if e["key"] == DA_ID)
    assert entry["status"] == "skipped"


def test_a_legacy_field_that_only_mentions_the_marker_is_still_migrated(tmp_path):
    mention = LEGACY + "\n// later: $structures.isNewEditModeEnabled()"
    write_scan(tmp_path, field("A", "legacy", mention))
    result = vm.cmd_classify(tmp_path)
    assert result["counts"]["inlineLegacy"] == 1 and result["counts"]["alreadyMigratedInline"] == 0


def test_a_legacy_asset_that_only_mentions_the_marker_gets_an_entry(tmp_path):
    write_scan(tmp_path, field("A", "viaAsset", f'#dotParse("/dA/{DA_ID}")'))
    write_meta(tmp_path)
    vm.cmd_classify(tmp_path)
    vm.cmd_assets_plan(tmp_path)
    download(tmp_path, text=LEGACY + "\n## isNewEditModeEnabled")
    result = vm.cmd_build_manifest(tmp_path, None)
    assert [e["key"] for e in result["entries"] if e["kind"] == "asset"] == [DA_ID]


def test_an_asset_not_confirmed_by_this_run_is_not_treated_as_migrated(instance):
    vm.cmd_record(instance, DA_ID, "published", None, "inode-2")
    (instance / "assets" / f"{DA_ID}.json").unlink()  # this run cannot resolve it any more
    vm.cmd_classify(instance)
    vm.cmd_assets_plan(instance)
    vm.cmd_build_manifest(instance, None)
    manifest = vm.read_manifest(instance)
    assert manifest["knownMigrated"] == {}
    assert not [e for e in manifest["entries"] if e["kind"] == "renderMode" and e["key"] == "A.viaAsset"]


def test_invalid_utf8_in_a_metadata_file_does_not_block_the_others(tmp_path):
    write_scan(tmp_path, field("A", "one", '#dotParse("/dA/abc")'), field("A", "two", '#dotParse("/dA/def")'))
    write_meta(tmp_path, "def")
    (tmp_path / "assets").mkdir(exist_ok=True)
    (tmp_path / "assets" / "abc.json").write_bytes(b"\xff\xfe{")
    vm.cmd_classify(tmp_path)
    plan = vm.cmd_assets_plan(tmp_path)
    assert [d["id"] for d in plan["toDownload"]] == ["def"]
    assert any("abc" in u for u in plan["unresolved"])


def test_a_corrupt_asset_metadata_file_does_not_block_the_others(tmp_path):
    write_scan(tmp_path, field("A", "one", '#dotParse("/dA/abc")'), field("A", "two", '#dotParse("/dA/def")'))
    write_meta(tmp_path, "def")
    (tmp_path / "assets" / "abc.json").write_text("{bad")
    vm.cmd_classify(tmp_path)
    plan = vm.cmd_assets_plan(tmp_path)
    assert [d["id"] for d in plan["toDownload"]] == ["def"]
    assert len(plan["unresolved"]) == 1 and "abc" in plan["unresolved"][0]


def test_a_corrupt_metadata_file_found_at_build_time_is_unresolved(tmp_path):
    write_scan(tmp_path, field("A", "one", f'#dotParse("/dA/{DA_ID}")'))
    write_meta(tmp_path)
    vm.cmd_classify(tmp_path)
    vm.cmd_assets_plan(tmp_path)
    download(tmp_path)
    (tmp_path / "assets" / f"{DA_ID}.json").write_text("{bad")
    result = vm.cmd_build_manifest(tmp_path, None)
    assert result["counts"]["unresolved"] == 1 and result["counts"]["pending"] == 0


def test_an_asset_edited_on_the_server_after_publishing_is_downloaded_again(instance):
    vm.cmd_record(instance, DA_ID, "published", None, "inode-2")
    write_meta(instance, inode="inode-9")  # someone edited it since
    vm.cmd_classify(instance)
    plan = vm.cmd_assets_plan(instance)
    assert [d["id"] for d in plan["toDownload"]] == [DA_ID]
    assert plan["alreadyMigrated"] == []


def test_a_finished_render_mode_switch_is_not_selected_again_through_its_asset(instance):
    vm.cmd_record(instance, "A.viaAsset", "published", None, None)
    assert "A.viaAsset" not in verdicts(vm.cmd_check(instance, [DA_ID], False, False))


def test_recording_an_unknown_status_is_an_input_error_not_an_assertion(instance):
    manifest = vm.read_manifest(instance)
    with pytest.raises(vm.InputError):
        vm.record_status(instance, manifest, "A.legacy", "bogus", None)


def test_a_missing_original_is_an_input_error(instance):
    migrate(instance, "fields/A.legacy.vtl", INLINE_MIGRATED)
    (instance / "original" / "fields" / "A.legacy.vtl").unlink()
    with pytest.raises(vm.InputError):
        vm.cmd_check(instance, ["A.legacy"], False, False)


def test_classify_reports_how_many_scan_parts_it_read(tmp_path):
    write_scan(tmp_path, field("A", "legacy", LEGACY))
    assert vm.cmd_classify(tmp_path)["scanParts"] == 1
