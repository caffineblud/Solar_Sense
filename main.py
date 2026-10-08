"""SolarSense backend: live solar forecast from Open-Meteo weather + pvlib.

Run:  uvicorn main:app --reload --port 8000
Try:  http://localhost:8000/forecast?lat=30.70&lon=76.72&kw=12
"""
import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
import numpy as np
import pandas as pd
import pvlib
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="SolarSense API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])

OPEN_METEO = "https://api.open-meteo.com/v1/forecast"
HOURLY = ("shortwave_radiation,direct_normal_irradiance,diffuse_radiation,"
          "temperature_2m,wind_speed_10m,cloud_cover")
CACHE_TTL = 600  # seconds; weather forecasts change slowly
_cache: dict = {}


def fetch_open_meteo(lat: float, lon: float) -> dict:
    """Two-day hourly forecast, local time, cached for 10 minutes."""
    key = (round(lat, 2), round(lon, 2))
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < CACHE_TTL:
        return hit[1]
    params = {"latitude": lat, "longitude": lon, "hourly": HOURLY,
              "forecast_days": 2, "timezone": "auto", "wind_speed_unit": "ms"}
    try:
        r = httpx.get(OPEN_METEO, params=params, timeout=10)
        r.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(502, f"Open-Meteo unavailable: {e}")
    data = r.json()
    _cache[key] = (time.time(), data)
    return data


def pv_power(data: dict, kw: float, tilt: float, azimuth: float, losses: float = 0.86):
    """Convert weather data to AC power (kW) per hour using pvlib."""
    h, tz = data["hourly"], data["timezone"]
    lat, lon = data["latitude"], data["longitude"]
    idx = pd.DatetimeIndex(pd.to_datetime(h["time"])).tz_localize(tz)

    def col(name):
        return pd.to_numeric(pd.Series(h[name]), errors="coerce").fillna(0).to_numpy(float)

    ghi, dni, dhi = col("shortwave_radiation"), col("direct_normal_irradiance"), col("diffuse_radiation")
    temp, wind, cloud = col("temperature_2m"), col("wind_speed_10m"), col("cloud_cover")

    # Open-Meteo radiation is the mean of the preceding hour: use the hour's midpoint for sun position.
    sp = pvlib.solarposition.get_solarposition(idx - pd.Timedelta(minutes=30), lat, lon)
    poa = pvlib.irradiance.get_total_irradiance(
        tilt, azimuth, sp["apparent_zenith"].to_numpy(), sp["azimuth"].to_numpy(),
        dni=dni, ghi=ghi, dhi=dhi)["poa_global"]
    poa = np.nan_to_num(np.asarray(poa, float))

    cell = pvlib.temperature.faiman(poa, temp, np.maximum(wind, 0.5))
    pdc0 = kw * 1000
    dc = pvlib.pvsystem.pvwatts_dc(poa, cell, pdc0, gamma_pdc=-0.004)
    ac = pvlib.inverter.pvwatts(dc, pdc0, eta_inv_nom=0.96)
    kw_ac = np.clip(np.nan_to_num(ac) * losses / 1000, 0, kw)
    return idx, kw_ac, cloud, temp


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/forecast")
def forecast(
    lat: float = Query(30.70, ge=-90, le=90, description="Latitude"),
    lon: float = Query(76.72, ge=-180, le=180, description="Longitude"),
    kw: float = Query(12, gt=0, le=1000, description="Array size in kW"),
    tilt: float | None = Query(None, ge=0, le=90, description="Panel tilt, default ~latitude"),
    azimuth: float | None = Query(None, ge=0, le=360, description="180 = south"),
):
    tilt = min(abs(lat), 40) if tilt is None else tilt
    azimuth = (180 if lat >= 0 else 0) if azimuth is None else azimuth
    data = fetch_open_meteo(lat, lon)
    idx, p, cloud, temp = pv_power(data, kw, tilt, azimuth)

    u = 0.08 + 0.30 * cloud / 100          # wider band when cloudier
    low, high = np.clip(p * (1 - u), 0, kw), np.clip(p * (1 + u), 0, kw)
    hours = [{"t": t.isoformat(), "kw": round(float(a), 2), "low": round(float(b), 2),
              "high": round(float(c), 2), "cloud": int(d), "temp": round(float(e), 1)}
             for t, a, b, c, d, e in zip(idx, p, low, high, cloud, temp)]
    return {
        "source": "Open-Meteo + pvlib",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lat": data["latitude"], "lon": data["longitude"], "tz": data["timezone"],
        "kw": kw, "tilt": tilt, "azimuth": azimuth,
        "confidence": round(float(100 * (1 - u.mean())), 1),
        "energy_kwh": {"today": round(float(p[:24].sum()), 1), "tomorrow": round(float(p[24:48].sum()), 1)},
        "hours": hours,
    }


# ---------------------------------------------------------------- accounts ---
BASE = Path(__file__).parent
DB_PATH = os.environ.get("SOLARSENSE_DB", str(BASE / "solarsense.db"))
TOKEN_DAYS = 7
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _secret() -> str:
    """Signing key: env var, else a random key saved once next to this file."""
    if os.environ.get("SOLARSENSE_SECRET"):
        return os.environ["SOLARSENSE_SECRET"]
    f = BASE / ".secret"
    if not f.exists():
        f.write_text(secrets.token_hex(32))
    return f.read_text().strip()


SECRET = _secret()


def db() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL,"
              " name TEXT NOT NULL, salt TEXT NOT NULL, pw TEXT NOT NULL, created REAL NOT NULL)")
    return c


def hash_pw(pw: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 200_000).hex()


def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _unb64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def make_token(uid: int, name: str) -> str:
    """HS256-signed token (standard JWT layout), built with the standard library only."""
    head = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    body = _b64(json.dumps({"sub": str(uid), "name": name, "exp": int(time.time()) + TOKEN_DAYS * 86400}).encode())
    sig = hmac.new(SECRET.encode(), f"{head}.{body}".encode(), hashlib.sha256).digest()
    return f"{head}.{body}.{_b64(sig)}"


def read_token(tok: str) -> dict:
    try:
        head, body, sig = tok.split(".")
        good = hmac.new(SECRET.encode(), f"{head}.{body}".encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(good, _unb64(sig)):
            raise ValueError("bad signature")
        p = json.loads(_unb64(body))
        if p["exp"] < time.time():
            raise ValueError("expired")
        return p
    except Exception:
        raise HTTPException(401, "Session expired. Please sign in again.")


class Register(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    email: str = Field(max_length=120)
    password: str = Field(min_length=8, max_length=128)


class Login(BaseModel):
    email: str = Field(max_length=120)
    password: str = Field(max_length=128)


_fails: dict = {}  # email -> recent failed-login timestamps (simple brute-force guard)


@app.post("/auth/register", status_code=201)
def register(b: Register):
    email = b.email.strip().lower()
    if not EMAIL_RE.match(email):
        raise HTTPException(422, "Enter a valid email address.")
    salt = secrets.token_hex(16)
    try:
        with db() as c:
            cur = c.execute("INSERT INTO users(email,name,salt,pw,created) VALUES(?,?,?,?,?)",
                            (email, b.name.strip(), salt, hash_pw(b.password, salt), time.time()))
    except sqlite3.IntegrityError:
        raise HTTPException(409, "An account with this email already exists.")
    return {"token": make_token(cur.lastrowid, b.name.strip()), "name": b.name.strip()}


@app.post("/auth/login")
def login(b: Login):
    email = b.email.strip().lower()
    now = time.time()
    recent = [t for t in _fails.get(email, []) if now - t < 300]
    if len(recent) >= 5:
        raise HTTPException(429, "Too many attempts. Try again in a few minutes.")
    row = db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    salt = row["salt"] if row else "00" * 16          # same work whether or not the user exists
    ok = hmac.compare_digest(hash_pw(b.password, salt), row["pw"] if row else "x")
    if not (row and ok):
        _fails[email] = recent + [now]
        raise HTTPException(401, "Incorrect email or password.")
    _fails.pop(email, None)
    return {"token": make_token(row["id"], row["name"]), "name": row["name"]}


@app.get("/auth/me")
def me(authorization: str | None = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Not signed in.")
    return {"name": read_token(authorization[7:])["name"]}