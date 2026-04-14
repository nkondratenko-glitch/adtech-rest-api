from __future__ import annotations

import os
from pathlib import Path
from textwrap import dedent

from PIL import Image, ImageDraw, ImageFont
from fastapi.testclient import TestClient

os.environ['DATABASE_URL'] = 'sqlite:///./demo_assets.db'
os.environ['USE_FAKE_REDIS'] = 'true'
os.environ['DB_SIMULATED_DELAY_MS'] = '25'

from app.main import app  # noqa: E402
from app.cache import get_cache_client  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCREEN_DIR = ROOT / 'screenshots'
SCREEN_DIR.mkdir(exist_ok=True)


def render_terminal(text: str, out_path: Path, width: int = 1500, pad: int = 28, line_height: int = 28):
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 22)
    except Exception:
        font = ImageFont.load_default()
    lines = text.splitlines() or ['']
    height = pad * 2 + line_height * (len(lines) + 2)
    img = Image.new('RGB', (width, height), '#111827')
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((12, 12, width - 12, height - 12), radius=18, outline='#374151', width=2, fill='#111827')
    y = pad
    for line in lines:
        draw.text((pad, y), line, font=font, fill='#E5E7EB')
        y += line_height
    img.save(out_path)


with TestClient(app) as client:
    cache = get_cache_client()
    cache.flushall()
    r1 = client.get('/campaign/101/performance')
    r2 = client.get('/campaign/101/performance')
    r3 = client.get('/advertiser/1/spending')
    r4 = client.get('/user/1/engagements')

campaign_demo = dedent(f'''\
$ curl -i http://localhost:8000/campaign/101/performance
HTTP/1.1 200 OK
X-Data-Source: {r1.headers.get('x-data-source')}
X-Response-Time-ms: {r1.headers.get('x-response-time-ms')}

{r1.text}

$ curl -i http://localhost:8000/campaign/101/performance
HTTP/1.1 200 OK
X-Data-Source: {r2.headers.get('x-data-source')}
X-Response-Time-ms: {r2.headers.get('x-response-time-ms')}

{r2.text}
''')

spending_demo = dedent(f'''\
$ curl -i http://localhost:8000/advertiser/1/spending
HTTP/1.1 200 OK
X-Data-Source: {r3.headers.get('x-data-source')}
X-Response-Time-ms: {r3.headers.get('x-response-time-ms')}

{r3.text}
''')

engagement_demo = dedent(f'''\
$ curl -i http://localhost:8000/user/1/engagements
HTTP/1.1 200 OK
X-Data-Source: {r4.headers.get('x-data-source')}
X-Response-Time-ms: {r4.headers.get('x-response-time-ms')}

{r4.text}
''')

benchmark_text = (ROOT / 'BENCHMARK_RESULTS.md').read_text(encoding='utf-8')

(ROOT / 'demo_outputs.txt').write_text(
    campaign_demo + '\n---\n' + spending_demo + '\n---\n' + engagement_demo,
    encoding='utf-8',
)

render_terminal(campaign_demo, SCREEN_DIR / 'campaign_performance_demo.png', width=1600)
render_terminal(spending_demo, SCREEN_DIR / 'advertiser_spending_demo.png', width=1400)
render_terminal(engagement_demo, SCREEN_DIR / 'user_engagements_demo.png', width=1800, line_height=26)
render_terminal(benchmark_text, SCREEN_DIR / 'benchmark_results.png', width=1700)
print('Generated demo outputs and screenshots.')
