"""FR-010 gap fix: `inline_problem` must verify the original legacy code is verbatim
specifically INSIDE the top-level #else branch — not merely present anywhere in the
migrated file. Regression coverage for the gap both GitHub Copilot's and Claude's
review flagged on PR dotCMS/core#37768."""

import vtl_migration as mcf

ORIGINAL = b"<script>dojo.ready(function(){ dijit.byId('userIdField'); });</script>"


def test_verbatim_in_else_still_passes():
    """Baseline: unchanged behavior for the simple, honest case."""
    migrated = (
        b"#if( $structures.isNewEditModeEnabled() )\n"
        b"<p>new component</p>\n"
        b"#else\n" + ORIGINAL + b"\n"
        b"#end"
    )
    assert mcf.inline_problem(ORIGINAL, migrated) is None


def test_missing_marker_still_reports_missing_branch():
    """Baseline: unchanged behavior when the marker itself is absent."""
    migrated = b"<p>no branch here, oops</p>"
    problem = mcf.inline_problem(ORIGINAL, migrated)
    assert problem is not None
    assert "isNewEditModeEnabled" in problem


def test_not_verbatim_simple_else_still_rejected():
    """Baseline: a genuinely different, non-nested #else is still rejected."""
    migrated = (
        b"#if( $structures.isNewEditModeEnabled() )\n"
        b"<p>migrated</p>\n"
        b"#else\n<p>NOT the original code</p>\n#end"
    )
    problem = mcf.inline_problem(ORIGINAL, migrated)
    assert problem is not None
    assert "verbatim" in problem


def test_original_hidden_in_if_branch_is_rejected():
    """THE REGRESSION TEST: the old substring-anywhere check would wrongly PASS this,
    because ORIGINAL appears inside a comment in the #if branch while the #else branch
    has genuinely different (broken) legacy behavior."""
    migrated = (
        b"#if( $structures.isNewEditModeEnabled() )\n"
        b"<!-- legacy reference, no longer used:\n" + ORIGINAL + b"\n-->\n"
        b"<p>brand new modern UI</p>\n"
        b"#else\n"
        b"<p>TOTALLY DIFFERENT -- legacy behavior silently dropped</p>\n"
        b"#end"
    )
    assert ORIGINAL in migrated  # sanity check the trap actually exists
    problem = mcf.inline_problem(ORIGINAL, migrated)
    assert problem is not None
    assert "verbatim" in problem


def test_original_hidden_in_if_branch_with_empty_else_is_rejected():
    """Variant: the #else branch is empty instead of merely different."""
    migrated = (
        b"#if( $structures.isNewEditModeEnabled() )\n"
        b"<!-- " + ORIGINAL + b" -->\n"
        b"<p>new</p>\n"
        b"#else\n#end"
    )
    problem = mcf.inline_problem(ORIGINAL, migrated)
    assert problem is not None
    assert "verbatim" in problem


def test_nested_if_else_in_both_branches_finds_true_top_level_else():
    """THE DEFEATING CASE: both the #if (migrated) and #else (legacy) halves contain
    their own nested #if/#else/#end. A naive "take the first #else" would wrongly grab
    the nested one inside the #if-branch instead of the real top-level one."""
    legacy_nested = (
        b"#if( $inode )\n<p>Editing existing legacy content</p>\n"
        b"#else\n<p>New legacy content</p>\n#end"
    )
    migrated = (
        b"#if( $structures.isNewEditModeEnabled() )\n"
        b"#if( $field.required() )\n<p>required field UI</p>\n"
        b"#else\n<p>optional field UI</p>\n#end\n"
        b"#else\n" + legacy_nested + b"\n"
        b"#end"
    )
    assert mcf.inline_problem(legacy_nested, migrated) is None


def test_nested_if_else_does_not_let_migrated_branch_content_leak_as_verbatim():
    """Companion: confirms the nested case is a real test, not a tautology — if the
    "legacy" bytes we check for actually belong to the migrated half, it must still be
    rejected."""
    not_the_legacy_branch = b"<p>required field UI</p>"
    migrated = (
        b"#if( $structures.isNewEditModeEnabled() )\n"
        b"#if( $field.required() )\n" + not_the_legacy_branch + b"\n"
        b"#else\n<p>optional field UI</p>\n#end\n"
        b"#else\n#if( $inode )\n<p>Editing existing legacy content</p>\n"
        b"#else\n<p>New legacy content</p>\n#end\n"
        b"#end"
    )
    problem = mcf.inline_problem(not_the_legacy_branch, migrated)
    assert problem is not None
    assert "verbatim" in problem


def test_no_top_level_else_is_reported_not_crashed():
    """Malformed input: marker present, but no #else at all."""
    migrated = b"#if( $structures.isNewEditModeEnabled() )\n<p>only if, no else</p>\n#end"
    problem = mcf.inline_problem(ORIGINAL, migrated)
    assert problem is not None
    assert "else" in problem


def test_unbalanced_block_is_reported_not_crashed():
    """Malformed input: a #foreach in the #else branch is never closed."""
    migrated = (
        b"#if( $structures.isNewEditModeEnabled() )\n<p>new</p>\n"
        b"#else\n#foreach( $x in $list )\n<p>$x</p>\n" + ORIGINAL + b"\n#end"
    )
    problem = mcf.inline_problem(ORIGINAL, migrated)
    assert problem is not None


def test_missing_header_is_reported_not_crashed():
    """Malformed input: the marker string appears, but not as line 1's real header."""
    migrated = b"<!-- isNewEditModeEnabled mentioned in passing, not a real #if -->\n" + ORIGINAL
    problem = mcf.inline_problem(ORIGINAL, migrated)
    assert problem is not None


def test_end_date_selector_inside_legacy_code_is_flagged_not_silently_mismatched():
    """SKILL.md's own worked example: `#end-date` inside a jQuery-style selector IS a
    real #end directive per Velocity's directive-name-boundary rule (name greedily
    matches "end", "-date" is ordinary text) — not a coincidental string match. Because
    this specific legacy snippet also wraps that selector in its own #if( $maxChar )
    ... #end, the #end-date directive actually closes that #if in real Velocity, leaving
    the snippet's own trailing #end unmatched — i.e. this legacy code is *itself*
    unbalanced (SKILL.md's own "Before emitting inline" blocking case #2: "the legacy
    branch would not parse on its own"), which is out of scope for the skill's inline
    mode to have produced in the first place. `inline_problem` must not crash on it, and
    correctly refuses to treat it as a verified-verbatim match (better to flag it for a
    human than silently publish a file carrying this latent parsing hazard)."""
    original = (
        b"#if( $maxChar )\n"
        b"<script>dojo.query('#end-date').style('width', '8em');</script>\n"
        b"#end"
    )
    migrated = (
        b"#if( $structures.isNewEditModeEnabled() )\n<p>new</p>\n"
        b"#else\n" + original + b"\n#end"
    )
    problem = mcf.inline_problem(original, migrated)
    assert problem is not None  # never crashes; correctly declines to pass this as safe


def test_end_date_selector_without_surrounding_block_is_recognized_as_a_real_directive():
    """Companion, without the self-unbalancing #if/#end wrapper: confirms `#end-date` is
    read as a real #end (per Velocity's grammar) rather than ignored as plain text — the
    tokenizer must not be fooled into treating it as harmless string content either."""
    legacy = b"<script>dojo.query('#end-date').style('width', '8em');</script>"
    migrated = b"#if( $structures.isNewEditModeEnabled() )\n<p>new</p>\n#else\n" + legacy + b"\n#end"
    # The embedded "#end" (from "#end-date") is a real directive that closes the header's
    # own #if early in actual Velocity parsing, before this file's own final #end — so
    # the located "legacy branch" is truncated at that point, and the verbatim check
    # correctly does not consider the untruncated original verbatim-matched.
    problem = mcf.inline_problem(legacy, migrated)
    assert problem is not None


HEADER = b"#if( $structures.isNewEditModeEnabled() )\n"


def inline(new: bytes, original: bytes = ORIGINAL) -> bytes:
    return HEADER + new + b"\n#else\n" + original + b"\n#end"


def test_a_stray_end_after_the_inline_block_is_rejected():
    problem = mcf.inline_problem(ORIGINAL, inline(b"<p>new</p>") + b"\n#end")
    assert problem and "unmatched #end" in problem


def test_a_stray_else_after_the_inline_block_is_rejected():
    assert mcf.inline_problem(ORIGINAL, inline(b"<p>new</p>") + b"\n#else") is not None


def test_balanced_blocks_after_the_inline_block_are_allowed():
    assert mcf.inline_problem(ORIGINAL, inline(b"<p>new</p>") + b"\n#if( $x )a#end") is None


def test_a_second_top_level_else_is_rejected():
    migrated = HEADER + b"<p>new</p>\n#else\n" + ORIGINAL + b"\n#else\nmore\n#end"
    assert "more than one top-level #else" in mcf.inline_problem(ORIGINAL, migrated)


def test_extra_code_in_the_else_branch_is_rejected():
    migrated = HEADER + b"<p>new</p>\n#else\nextra code\n" + ORIGINAL + b"\n#end"
    assert "verbatim" in mcf.inline_problem(ORIGINAL, migrated)


def test_the_else_branch_keeps_crlf_and_a_missing_final_newline():
    original = b"line one\r\nline two dojo.ready(x)"
    assert mcf.inline_problem(original, inline(b"<p>new</p>", original)) is None


def test_legacy_copied_into_both_branches_is_rejected():
    problem = mcf.inline_problem(ORIGINAL, inline(ORIGINAL))
    assert problem and "#if branch still has legacy code" in problem


def test_the_same_macro_in_both_branches_is_rejected():
    original = b"#macro( show $x )old $x#end\n<p>legacy dojo.byId('a')</p>"
    problem = mcf.inline_problem(original, inline(b"#macro( show $x )new $x#end", original))
    assert problem and "show" in problem


def test_different_macros_in_each_branch_are_allowed():
    original = b"#macro( showOld $x )old $x#end\n<p>legacy</p>"
    assert mcf.inline_problem(original, inline(b"#macro( showNew $x )new $x#end", original)) is None


def test_is_inline_migrated_needs_the_real_wrapper_not_a_mention():
    assert mcf.is_inline_migrated(inline(b"<p>new</p>"))
    assert not mcf.is_inline_migrated(b"<script>// $structures.isNewEditModeEnabled()</script>")
    assert not mcf.is_inline_migrated(b"")
