import re, json, socket, ssl, time
import urllib.request, urllib.error
from collections import Counter, defaultdict

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def check(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko,en-US;q=0.8,en;q=0.6"})
    try:
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return ("OK", str(resp.status))
    except urllib.error.HTTPError as e:
        return ("HTTP_%d" % e.code, "HTTP %d" % e.code)
    except urllib.error.URLError as e:
        r = str(e.reason)
        if any(s in r for s in ["Name or service not known","getaddrinfo","Temporary failure","No address associated","nodename nor servname"]):
            return ("DNS", "DNS: " + r)
        if "timed out" in r.lower() or "timeout" in r.lower():
            return ("TIMEOUT", "Timeout")
        return ("URLERR", r[:100])
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

# Deep verify: ALL Other links (528) to get complete error picture
other = buckets["Other"]
print("=== Verifying ALL %d Other links ===" % len(other))
results = []
for i, u in enumerate(other):
    st, reason = check(u, timeout=10)
    if st != "OK":
        print("  [%3d] %-10s %s" % (i+1, st, u[:95]))
    results.append({"url": u, "host": host(u), "status": st, "reason": reason})
    time.sleep(0.1)

with open("verify_other_all.json","w",encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)

sc = Counter(r["status"] for r in results)
print("\n=== Other category status distribution (all %d) ===" % len(results))
for s, c in sc.most_common():
    print("  %-12s %4d" % (s, c))

# Group errors by host
err = [r for r in results if r["status"] != "OK"]
hosterr = Counter(r["host"] for r in err)
print("\n=== Error hosts (sorted) ===")
for h, c in hosterr.most_common():
    statuses = sorted(set(r["status"] for r in err if r["host"] == h))
    print("  %4d  %-10s %s" % (c, ",".join(statuses), h))
