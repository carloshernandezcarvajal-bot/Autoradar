import urllib.request, json

# Test search with brand filter
data = json.dumps({"brand": "Mazda", "page": 1, "page_size": 5}).encode()
req = urllib.request.Request(
    "http://localhost:8000/api/search",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    res = urllib.request.urlopen(req, timeout=5)
    result = json.loads(res.read())
    print(f"Search Mazda: {result['total']} results")
    for item in result["items"][:3]:
        v = item["vehicle"]
        print(f"  {v['brand']} {v['model']} {v['year']} - ${item['current_price']:,.0f} - Score: {item['opportunity_score']} ({item['score_label']})")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"HTTP Error {e.code}: {body[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test search without filters
data2 = json.dumps({"page": 1, "page_size": 5}).encode()
req2 = urllib.request.Request(
    "http://localhost:8000/api/search",
    data=data2,
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    res2 = urllib.request.urlopen(req2, timeout=5)
    result2 = json.loads(res2.read())
    print(f"\nAll listings: {result2['total']} total")
    for item in result2["items"][:3]:
        v = item["vehicle"]
        print(f"  {v['brand']} {v['model']} {v['year']} - ${item['current_price']:,.0f} - Score: {item['opportunity_score']} ({item['score_label']})")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"\nHTTP Error {e.code}: {body[:500]}")
except Exception as e:
    print(f"Error: {e}")
