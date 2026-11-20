from pathlib import Path
import base64, zlib
root = Path(__file__).resolve().parent
payload = "".join((root / f"v45_payload_{i}.b64").read_text(encoding="utf-8").strip() for i in range(1, 7))
source = zlib.decompress(base64.b64decode(payload)).decode("utf-8")
source = source.replace('var label := glyphs[i] +', 'var label: String = str(glyphs[i]) +')
exec(compile(source, str(Path(__file__).resolve()), "exec"), globals())
