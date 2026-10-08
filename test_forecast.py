"""Offline test: fakes the Open-Meteo response, checks the pvlib maths is sane."""
import os, tempfile
os.environ["SOLARSENSE_DB"] = os.path.join(tempfile.mkdtemp(), "t.db")
os.environ["SOLARSENSE_SECRET"] = "test-secret"
import numpy as np
from fastapi.testclient import TestClient
import main

def fake(lat, lon):
    t = [f"2026-10-{8 + d:02d}T{h:02d}:00" for d in range(2) for h in range(24)]
    bell = lambda h, pk: max(0.0, pk * np.sin(np.pi * (h - 6) / 12)) if 6 <= h <= 18 else 0.0
    hr = [h for _ in range(2) for h in range(24)]
    return {"latitude": lat, "longitude": lon, "timezone": "Asia/Kolkata", "hourly": {
        "time": t, "shortwave_radiation": [bell(h, 650) for h in hr],
        "direct_normal_irradiance": [bell(h, 750) for h in hr],
        "diffuse_radiation": [bell(h, 110) for h in hr],
        "temperature_2m": [28.0] * 48, "wind_speed_10m": [2.0] * 48, "cloud_cover": [10] * 48}}

main.fetch_open_meteo = fake
c = TestClient(main.app)

def test_forecast_shape_and_sanity():
    r = c.get("/forecast?lat=30.7&lon=76.72&kw=12"); assert r.status_code == 200
    d = r.json(); k = [x["kw"] for x in d["hours"]]
    assert len(k) == 48 and k[0] == 0 and k[3] == 0 and k[23] == 0
    assert 5 < max(k[:24]) <= 12 and 10 <= k.index(max(k[:24])) <= 14
    assert all(x["low"] <= x["kw"] <= x["high"] for x in d["hours"])
    assert d["energy_kwh"]["today"] > 20

def test_validation():
    assert c.get("/forecast?lat=999").status_code == 422


def test_auth_flow():
    r = c.post("/auth/register", json={"name": "Yash", "email": "Yash@Example.com", "password": "sunshine99"})
    assert r.status_code == 201 and r.json()["name"] == "Yash"
    assert c.post("/auth/register", json={"name": "X", "email": "yash@example.com", "password": "sunshine99"}).status_code == 409
    assert c.post("/auth/register", json={"name": "X", "email": "bad", "password": "sunshine99"}).status_code == 422
    assert c.post("/auth/register", json={"name": "X", "email": "a@b.co", "password": "short"}).status_code == 422
    assert c.post("/auth/login", json={"email": "yash@example.com", "password": "wrongpass1"}).status_code == 401
    tok = c.post("/auth/login", json={"email": "yash@example.com", "password": "sunshine99"}).json()["token"]
    assert c.get("/auth/me", headers={"Authorization": f"Bearer {tok}"}).json() == {"name": "Yash"}
    assert c.get("/auth/me").status_code == 401
    assert c.get("/auth/me", headers={"Authorization": "Bearer junk"}).status_code == 401

def test_lockout():
    for _ in range(5):
        c.post("/auth/login", json={"email": "nobody@example.com", "password": "whatever1"})
    assert c.post("/auth/login", json={"email": "nobody@example.com", "password": "whatever1"}).status_code == 429


def test_cors_preflight_for_login():
    r = c.options("/auth/register", headers={"Origin": "http://localhost:5500",
                  "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "content-type"})
    assert r.status_code == 200 and r.headers["access-control-allow-origin"] == "*"

def test_tampered_token_rejected():
    tok = c.post("/auth/login", json={"email": "yash@example.com", "password": "sunshine99"}).json()["token"]
    head, body, sig = tok.split(".")
    assert c.get("/auth/me", headers={"Authorization": f"Bearer {head}.{body}x.{sig}"}).status_code == 401