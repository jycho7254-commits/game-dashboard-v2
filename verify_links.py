import re, json, socket, ssl, time
import urllib.request, urllib.error
from collections import Counter, defaultdict

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def check(url, timeout=12):
    """Return (status, reason). status='OK' for 2xx/3xx, or HTTP code, or ERROR type."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko,en-US;q=0.8,en;q=0.6"})
    try:
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return ("OK", str(resp.status))
    except urllib.error.HTTPError as e:
        return ("HTTP_%d" % e.code, "HTTP %d" % e.code)
    except urllib.error.URLError as e:
        r = str(e.reason)
        if "Name or service not known" in r or "getaddrinfo" in r or "Temporary failure" in r or "No address associated" in r:
            return ("DNS", "DNS: " + r)
        if "timed out" in r.lower() or "timeout" in r.lower():
            return ("TIMEOUT", "Timeout")
        return ("URLERR", r[:120])
    except socket.gaierror as e:
        return ("DNS", "DNS: " + str(e))
    except socket.timeout:
        return ("TIMEOUT", "Timeout")
    except ssl.SSLError as e:
        return ("SSL", "SSL: " + str(e)[:80])
    except Exception as e:
        return ("ERROR", type(e).__name__ + ": " + str(e)[:80])

with open("index.html","r",encoding="utf-8") as f:
    html = f.read()
urls = re.findall(r"https?://[A-Za-z0-9._~:/?#@!&()*+,;=%-]+", html)
def host(u):
    m = re.match(r"https?://([^/]+)", u)
    return m.group(1).replace("www.","") if m else "?"
buckets = defaultdict(list)
for u in set(urls):
    h = host(u)
    if "youtube" in h: buckets["YouTube"].append(u)
    elif "bilibili" in h: buckets["Bilibili"].append(u)
    elif "chzzk" in h: buckets["Chzzk"].append(u)
    elif "googleusercontent" in h or "play-lh" in h: buckets["Icon"].append(u)
    elif "googleapis" in h or "jsdelivr" in h or "googlesyndication" in h: buckets["CDN"].append(u)
    else: buckets["Other"].append(u)

samples = {
    "Other": buckets["Other"][:50],
    "YouTube": buckets["YouTube"][:20],
    "Bilibili": buckets["Bilibili"][:10],
    "Chzzk": buckets["Chzzk"][:10],
}

results = {}
for cat, lst in samples.items():
    print("\n=== %s (%d samples) ===" % (cat, len(lst)))
    cat_res = []
    for i, u in enumerate(lst):
        st, reason = check(u, timeout=12)
        print("  [%2d] %-8s %s" % (i+1, st, u[:90]))
        cat_res.append({"url": u, "status": st, "reason": reason})
        time.sleep(0.15)
    results[cat] = cat_res

with open("verify_results.json","w",encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("\nSaved verify_results.json")
