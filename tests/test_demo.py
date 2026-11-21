from h1 import demo, importer, scoring


def test_demo_data_runs_through_the_normal_pipeline(tmp_path):
    result = importer.load(demo.write(tmp_path / "Referrals-demo.xlsx"))
    assert result.forbidden_columns == [] and result.scrubbed_values == 0
    train, test = scoring.split(result.rows)
    assert len(train) == 240 and len(test) == 24
    scored = scoring.score(result.rows)
    assert scored["overall"]["n"] == 23                 # one review row has no recorded vendor
    assert scored["intake"]["with_issue"] == scored["intake"]["flagged"] == 5


def test_app_writes_demo_file_only_under_ignored_output():
    source = open("app.py", encoding="utf-8").read()
    assert 'ROOT / "output" / "demo"' in source and 'ROOT / "logs" / "demo-decisions.jsonl"' in source
