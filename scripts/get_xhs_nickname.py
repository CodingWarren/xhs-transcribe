#!/usr/bin/env python3
"""
Extract author nickname from Xiaohongshu note pages.

Strategy:
1. Get uploader_id from yt-dlp (yt-dlp CAN extract this)
2. Fetch page HTML and search for "nickname" value near the user_id in HTML
   (the author nickname appears in the page near their profile link with user_id)
3. If not found, fallback to first "nickname" occurrence

Usage:
    python3 get_xhs_nickname.py "https://www.xiaohongshu.com/discovery/item/..."
"""
import sys
import json
import gzip
import subprocess
import re
import urllib.request


def get_uploader_id(url):
    """Get uploader_id from yt-dlp (yt-dlp can extract this for XHS)."""
    try:
        result = subprocess.run(
            ['yt-dlp', '--dump-json', '--no-download', '--no-update', '--', url],
            capture_output=True, text=True, timeout=30
        )
        if result.stdout.strip():
            data = json.loads(result.stdout)
            return data.get('uploader_id')
    except Exception:
        pass
    return None


def get_nickname_from_html(html, user_id):
    """
    Extract nickname from HTML, using user_id to find the correct one.
    The author nickname appears in a <a> tag with href containing user_id.
    """
    if not html or not user_id:
        return None

    # Strategy: find the profile link with the user_id and get its text
    # Pattern: <a ... href=".../user/profile/{user_id}..." ...>nickname</a>
    pattern = rf'href="[^"]*user/profile/{re.escape(user_id)}[^"]*"[^>]*>([^<]+)</a>'
    match = re.search(pattern, html)
    if match:
        return match.group(1).strip()

    # Fallback: look for user_id followed by "nickname" in the HTML
    pattern2 = rf'{re.escape(user_id)}[^>]*(?:nickname|nick_name)\s*[\-:]\s*["\']([^"\']+)["\']'
    match = re.search(pattern2, html)
    if match:
        return match.group(1).strip()

    # Fallback: find "nickname":"xxx" near the user_id in the HTML source
    # Look for the user_id in HTML, then search for "nickname" within next 200 chars
    idx = html.find(user_id)
    if idx != -1:
        snippet = html[idx:idx+500]
        match = re.search(r'"nickname"\s*:\s*"([^"]+)"', snippet)
        if match:
            return match.group(1).strip()

    return None


def get_nickname_simple(html):
    """
    Fallback: extract first "nickname" from HTML.
    May return a commenter's nickname instead of the author, but better than nothing.
    """
    match = re.search(r'"nickname"\s*:\s*"([^"]+)"', html)
    if match:
        return match.group(1)
    return None


def fetch_xhs_page(url):
    """Fetch XHS page with proper headers to get actual content (not bot page)."""
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            # Try to decode, handling compression
            content = resp.read()
            # If content is gzip-compressed, decompress
            if resp.info().get('Content-Encoding') == 'gzip':
                content = gzip.decompress(content)
            return content.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"HTTP fetch failed: {e}", file=sys.stderr)
        return None


if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read().strip()

    if not url:
        print('')
        sys.exit(0)

    # Step 1: Get uploader_id from yt-dlp
    user_id = get_uploader_id(url)

    # Step 2: Fetch page HTML
    html = fetch_xhs_page(url)

    nickname = None
    if html and user_id:
        # Try to find the author nickname using user_id as anchor
        nickname = get_nickname_from_html(html, user_id)

    if not nickname and html:
        # Fallback: take first "nickname" found
        nickname = get_nickname_simple(html)

    print(nickname if nickname else '')
