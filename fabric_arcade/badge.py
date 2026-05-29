"""
Badge issuance for Fabric Arcade.

Generates a tamper-resistant share link for game completion. The token embeds
the player/game/rank/score/timestamp and is signed with HMAC-SHA256. The
website's badge.html verifies the signature in-browser and renders an SVG
medal that the player can download or share on social media.

Security note: the HMAC secret is intentionally embedded in this package so
that anyone can `issue_badge()` from a notebook without provisioning. This
prevents trivial URL editing but is NOT a strong security boundary — anyone
who reads the source code can forge a badge. That trade-off is fine for a
gamified learning catalog.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass

# Keep in sync with website/badge.html (window.FA_BADGE_SECRET).
BADGE_SECRET = b"fabric-arcade-badge-v1-7K9mP3xQ"
BADGE_VERSION = 1
DEFAULT_BASE_URL = "https://fabric-arcade.netlify.app"


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


@dataclass
class Badge:
    token: str
    url: str
    payload: dict

    def share_block(self) -> str:
        """Markdown-friendly share block to print/display in a notebook."""
        return (
            f"### 🏅 Your Fabric Arcade Badge\n\n"
            f"**{self.payload['p']}** — *{self.payload['r']}* · score **{self.payload['s']}**\n\n"
            f"[🔗 Open & download badge]({self.url})\n\n"
            f"Share this link on LinkedIn / Twitter / Bluesky."
        )


def issue_badge(
    game_id: str,
    player: str,
    rank: str,
    score: int,
    base_url: str = DEFAULT_BASE_URL,
    timestamp: int | None = None,
) -> Badge:
    """
    Issue a signed badge for a completed game.

    Parameters
    ----------
    game_id : str   Catalog id, e.g. "calc-groups-cathedral".
    player  : str   Player display name (any string the player wants on the badge).
    rank    : str   Final rank, e.g. "Cathedral Builder".
    score   : int   Final numeric score.
    base_url: str   Site root that hosts /badge.html.
    """
    payload = {
        "v": BADGE_VERSION,
        "g": game_id,
        "p": str(player),
        "r": str(rank),
        "s": int(score),
        "t": int(timestamp if timestamp is not None else time.time()),
    }
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    sig = hmac.new(BADGE_SECRET, body, hashlib.sha256).digest()
    token = f"{_b64u(body)}.{_b64u(sig)}"
    url = f"{base_url.rstrip('/')}/badge.html?t={token}"
    return Badge(token=token, url=url, payload=payload)


def verify_token(token: str) -> dict | None:
    """Verify a token (server-side helper). Returns the payload dict or None."""
    try:
        body_b64, sig_b64 = token.split(".", 1)
        pad = "=" * (-len(body_b64) % 4)
        body = base64.urlsafe_b64decode(body_b64 + pad)
        pad = "=" * (-len(sig_b64) % 4)
        sig = base64.urlsafe_b64decode(sig_b64 + pad)
    except Exception:
        return None
    expected = hmac.new(BADGE_SECRET, body, hashlib.sha256).digest()
    if not hmac.compare_digest(expected, sig):
        return None
    try:
        return json.loads(body.decode("utf-8"))
    except Exception:
        return None
