import requests
import json

def test_auth_endpoints():
    base_url = 'http://localhost:5000/api'
    
    print("=== TESTING API ENDPOINTS ===\n")
    
    # 1. Health check
    print("1. Health Check:")
    try:
        response = requests.get(f'{base_url}/health')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # 2. Login
    print("2. Login Test:")
    login_data = {
        'email': 'admin@gym.local',
        'password': 'tu_contraseña_segura_aqui'
    }
    
    try:
        response = requests.post(f'{base_url}/auth/login', json=login_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 200:
            token = result.get('access_token')
            headers = {'Authorization': f'Bearer {token}'}
            
            # 3. Validate token
            print("\n3. Token Validation:")
            response = requests.get(f'{base_url}/auth/validate', headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            # 4. Get usuarios
            print("\n4. Get Usuarios:")
            response = requests.get(f'{base_url}/auth/usuarios', headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
        else:
            print("Login falló, no se pueden probar otros endpoints")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_auth_endpoints()