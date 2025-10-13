#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 SCRIPT DE PRUEBA DE LA API
Test simple para verificar que la API funciona correctamente.
"""

import requests


def test_api():
    """Probar la API del chatbot."""
    print("🧪 Probando API del chatbot...")

    try:
        # Hacer request a la API
        response = requests.post(
            "http://127.0.0.1:5000/api/chat/send",
            json={"message": "Hola! Di solo OK si funciona"},
            timeout=10,
            headers={"Content-Type": "application/json"},
        )

        print(f"✅ Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"🤖 Respuesta: {data.get('response', 'Sin respuesta')}")
            print(f"📝 Session ID: {data.get('session_id', 'Sin session')}")
            print("🎉 ¡API FUNCIONA CORRECTAMENTE!")
        else:
            print(f"❌ Error: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor")
    except requests.exceptions.Timeout:
        print("❌ Timeout - El servidor tardó demasiado en responder")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    test_api()
