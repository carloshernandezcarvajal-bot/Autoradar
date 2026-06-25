import urllib.request, json, time

# Test health
r = urllib.request.urlopen("http://localhost:8000/api/health", timeout=5)
print("Health:", json.loads(r.read()))

# Test brands
r = urllib.request.urlopen("http://localhost:8000/api/vehicles/brands/list", timeout=5)
print("Brands:", json.loads(r.read()))

# Test search
data = json.dumps({"brand": "Mazda", "page": 1, "page_size": 5}).encode()
req = urllib.request.Request(
    "http://localhost:8000/api/search",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST",
)
res = urllib.request.urlopen(req, timeout=5)
result = json.loads(res.read())
print(f"\nSearch Mazda: {result['total']} results")
for item in result["items"][:3]:
    v = item["vehicle"]
    print(
        f"  {v['brand']} {v['model']} {v['year']} - "
        f"${item['current_price']:,.0f} - "
        f"Score: {item['opportunity_score']} ({item['score_label']})"
    )
print(f"Market stats: avg=${result['market_stats']['avg']:,.0f}, "
      f"median=${result['market_stats']['median']:,.0f}")

# Test login
data = json.dumps({"email": "demo@autoradar.co", "password": "demo123"}).encode()
req = urllib.request.Request(
    "http://localhost:8000/api/auth/login",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST",
)
res = urllib.request.urlopen(req, timeout=5)
token = json.loads(res.read())["access_token"]
print(f"\nLogin OK - token: {token[:20]}...")

# Test favorites with auth
data = json.dumps({"listing_id": result["items"][0]["id"]}).encode()
req = urllib.request.Request(
    "http://localhost:8000/api/favorites",
    data=data,
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    method="POST",
)
res = urllib.request.urlopen(req, timeout=5)
print("Favorite added:", json.loads(res.read()))

print("\n=== API funcionando correctamente ===")
