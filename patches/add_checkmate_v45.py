from pathlib import Path
import base64, zlib
root = Path(__file__).resolve().parent
payload = "".join((root / f"v45_payload_{i}.b64").read_text(encoding="utf-8").strip() for i in range(1, 7))
source = zlib.decompress(base64.b64decode(payload)).decode("utf-8")
source = source.replace('var label := glyphs[i] +', 'var label: String = str(glyphs[i]) +')
source = source.replace('q.pressed.connect(_show_notice.bind(quick_names[i] + " — раздел в разработке"))', 'q.disabled = true\n            q.text = "🔒\\n" + quick_names[i] + "\\nСКОРО"')
source = source.replace('featured_hit.pressed.connect(_show_notice.bind("Королевский скин — скоро в магазине"))', 'featured_hit.disabled = true\n    featured_hit.tooltip_text = "🔒 Скоро"')
exec(compile(source, str(Path(__file__).resolve()), "exec"), globals())
