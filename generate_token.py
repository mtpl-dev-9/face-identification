"""
Generate a dummy JWT token for testing
Run: python generate_token.py
"""
from auth import generate_access_token, generate_refresh_token

# Generate tokens for user_id = 1
user_id = 1

access_token = generate_access_token(user_id)
refresh_token = generate_refresh_token(user_id)

print("=" * 60)
print("DUMMY TOKENS FOR TESTING")
print("=" * 60)
print(f"\nUser ID: {user_id}")
print(f"\nAccess Token (valid for 1 hour):")
print(access_token)
print(f"\nRefresh Token (valid for 7 days):")
print(refresh_token)
print("\n" + "=" * 60)
print("\nHow to use in Swagger:")
print("1. Click 'Authorize' button (🔒)")
print("2. Enter: Bearer " + access_token[:50] + "...")
print("3. Click 'Authorize' and 'Close'")
print("=" * 60)
