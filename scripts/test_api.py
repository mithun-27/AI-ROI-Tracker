import urllib.request
import json

try:
    r = urllib.request.urlopen('http://localhost:8000/analytics')
    data = json.loads(r.read())
    print(f"Features: {data['total_features']}")
    print(f"Cost: ${data['total_cost']}")
    print(f"Value: ${data['total_value']}")
    print(f"ROI: {data['overall_roi']}")
    print(f"Daily points: {len(data['daily_usage'])}")
    print(f"Feature comps: {len(data['feature_comparisons'])}")
    print(f"Alerts: {len(data['alerts'])}")
except Exception as e:
    if hasattr(e, 'read'):
        print(f"Error: {e.read().decode()}")
    else:
        print(f"Error: {e}")
