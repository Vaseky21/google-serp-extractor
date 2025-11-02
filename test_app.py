import unittest
import json
import os
from unittest.mock import patch, MagicMock
from app import app # Importuje Flask instanci z vašeho souboru app.py

# Důležité: Nastaví testovací mód pro Flask aplikaci
app.config['TESTING'] = True

class SerpApiSearchTest(unittest.TestCase):
    """
    Testovací třída pro endpoint /search ve Flask aplikaci.
    """

    def setUp(self):
        """
        Nastavení klienta před každým testem.
        """
        self.client = app.test_client()
        self.client.testing = True

    @patch('app.GoogleSearch')
    def test_search_success_mocked(self, MockGoogleSearch):
        """
        Testuje úspěšný výsledek (status 200) s mockováním SerpApi.
        Simuluje, že SerpApi vrátilo výsledky.
        """
        
        # --- 1. Nastavení simulovaných dat ---
        # Data, která by v reálu vrátila SerpApi (zjednodušená verze)
        mock_organic_results = [
            {
                "title": "Testovací Titulek 1",
                "snippet": "Testovací Popis 1.",
                "link": "http://example.com/1",
                "position": 1
            },
            {
                "title": "Testovací Titulek 2",
                "snippet": "Testovací Popis 2.",
                "link": "http://example.com/2",
                "position": 2
            }
        ]
        
        # Kompletní data s organickými výsledky, které SERP API vrací
        mock_full_response = {
            "search_metadata": {"status": "success"},
            "organic_results": mock_organic_results,
            # Mnoho dalších klíčů...
        }

        # Konfigurace mock objektu: get_dict() má vrátit mock_full_response
        mock_search_instance = MagicMock()
        mock_search_instance.get_dict.return_value = mock_full_response
        MockGoogleSearch.return_value = mock_search_instance
        
        # --- 2. Spuštění testovacího požadavku ---
        response = self.client.post(
            '/search',
            data=json.dumps({'keyword': 'testovaci_dotaz'}),
            content_type='application/json'
        )
        
        # --- 3. Asertace (Ověření) ---
        self.assertEqual(response.status_code, 200) # Ověření HTTP status kódu
        
        # Převedení odpovědi na JSON
        data = json.loads(response.get_data(as_text=True))
        
        # Ověření, že odpověď je seznam
        self.assertIsInstance(data, list)
        
        # Ověření počtu výsledků
        self.assertEqual(len(data), 2)
        
        # Ověření struktury a obsahu prvního výsledku
        self.assertDictEqual(data[0], {
            "title": "Testovací Titulek 1",
            "snippet": "Testovací Popis 1.",
            "link": "http://example.com/1",
            "position": 1
        })
        
        # Ověření, že SerpApi bylo voláno se správnými parametry
        MockGoogleSearch.assert_called_once()
        # Zkontrolujte, zda byla metoda get_dict() volána
        mock_search_instance.get_dict.assert_called_once()

    def test_search_missing_keyword(self):
        """
        Testuje chybový stav 400 (Bad Request), když chybí klíčové slovo.
        Tento test nevolá SerpApi.
        """
        # Spuštění požadavku s prázdným tělem
        response_empty = self.client.post(
            '/search',
            data=json.dumps({}),
            content_type='application/json'
        )

        # Spuštění požadavku s chybějícím klíčem 'keyword'
        response_missing_key = self.client.post(
            '/search',
            data=json.dumps({'query': 'neco'}), # Použití špatného klíče
            content_type='application/json'
        )
        
        # Ověření HTTP status kódu 400 pro oba případy
        self.assertEqual(response_empty.status_code, 400)
        self.assertEqual(response_missing_key.status_code, 400)

        # Ověření chybové zprávy pro první případ
        data = json.loads(response_empty.get_data(as_text=True))
        self.assertIn("Chybí klíčové slovo", data.get('error'))

# Pro spuštění testů, pokud je soubor spuštěn přímo
if __name__ == '__main__':
    unittest.main()