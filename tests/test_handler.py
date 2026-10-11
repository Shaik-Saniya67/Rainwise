import base64
import json

from rainwise.handler import lambda_handler


def _event(body, **extra):
    return {"requestContext": {"http": {"method": "POST"}}, "body": body, **extra}


def _post(payload):
    return lambda_handler(_event(json.dumps(payload)))


def test_success_matches_reference_example():
    res = _post({"roof_area_m2": 200, "rainfall_mm": 50, "efficiency_percent": 80})
    body = json.loads(res["body"])
    assert res["statusCode"] == 200
    assert res["headers"]["Content-Type"] == "application/json"
    assert body["harvestable_litres"] == 8000
    assert body["harvestable_kl"] == 8.0
    assert body["recommended_tank_litres"] == 10_000
    assert "8,000 litres" in body["message"]


def test_values_follow_the_request():
    body = json.loads(_post({"roof_area_m2": 100, "rainfall_mm": 20, "efficiency_percent": 50})["body"])
    assert body["harvestable_litres"] == 1000
    assert body["recommended_tank_litres"] == 1000


def test_base64_body_supported():
    raw = json.dumps({"roof_area_m2": 200, "rainfall_mm": 50, "efficiency_percent": 80})
    res = lambda_handler(_event(base64.b64encode(raw.encode()).decode(), isBase64Encoded=True))
    assert res["statusCode"] == 200


def test_missing_body():
    assert lambda_handler({})["statusCode"] == 400
    assert lambda_handler(_event(None))["statusCode"] == 400
    assert lambda_handler(_event(""))["statusCode"] == 400


def test_not_a_dict_event():
    assert lambda_handler("nope")["statusCode"] == 400
    assert lambda_handler(None)["statusCode"] == 400


def test_invalid_json():
    assert lambda_handler(_event("{not json"))["statusCode"] == 400


def test_nan_and_infinity_literals_rejected():
    res = lambda_handler(_event('{"roof_area_m2": 200, "rainfall_mm": NaN, "efficiency_percent": 80}'))
    assert res["statusCode"] == 400
    res = lambda_handler(_event('{"roof_area_m2": Infinity, "rainfall_mm": 5, "efficiency_percent": 80}'))
    assert res["statusCode"] == 400


def test_json_but_not_an_object():
    assert lambda_handler(_event("[1, 2, 3]"))["statusCode"] == 400
    assert lambda_handler(_event('"text"'))["statusCode"] == 400


def test_missing_fields_listed():
    res = _post({"roof_area_m2": 200})
    body = json.loads(res["body"])
    assert res["statusCode"] == 400
    assert body["details"] == ["Missing: rainfall_mm", "Missing: efficiency_percent"]


def test_invalid_values_return_400_with_details():
    res = _post({"roof_area_m2": -5, "rainfall_mm": 50, "efficiency_percent": 120})
    body = json.loads(res["body"])
    assert res["statusCode"] == 400
    assert body["error"] == "Invalid input."
    assert len(body["details"]) == 2


def test_string_numbers_rejected():
    res = _post({"roof_area_m2": "200", "rainfall_mm": 50, "efficiency_percent": 80})
    assert res["statusCode"] == 400


def test_oversized_body_rejected():
    res = lambda_handler(_event(json.dumps({"pad": "x" * 10_000})))
    assert res["statusCode"] == 413


def test_bad_base64_rejected():
    assert lambda_handler(_event("%%%not-base64%%%", isBase64Encoded=True))["statusCode"] == 400
