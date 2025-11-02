from flask import Flask, request, jsonify
from serpapi import GoogleSearch
from flask_cors import CORS # Důležité pro komunikaci mezi frontendem (index.html) a backendem (Flask)

app = Flask(__name__)
CORS(app) # Povolení CORS

# --- SERPAPI KLÍČ ---
SERPAPI_API_KEY = "9709624787e9cb3ee11cf870dff9a1bdc776eef015700161623f3c77f6605f22" 
# ---------------------------------------------

@app.route('/search', methods=['POST'])
def search_google():
    """
    Zpracuje POST požadavek, zavolá SerpApi a vrátí výsledky přirozeného vyhledávání.
    """
    data = request.get_json()
    keyword = data.get('keyword')

    if not keyword:
        return jsonify({"error": "Chybí klíčové slovo v požadavku."}), 400

    try:
        # Parametry pro SerpApi
        params = {
            "engine": "google",          # Vyhledávací engine
            "q": keyword,                # Hledané klíčové slovo
            "api_key": SERPAPI_API_KEY,  # Váš API klíč
            "gl": "cz",                  # Geografická lokace (Česko)
            "hl": "cs",                  # Jazyk rozhraní (čeština)
            "num": 10                    # Počet výsledků na stránku (tj. 1. strana)
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        # Filtrace POUZE pro výsledky organického (přirozeného) vyhledávání
        # Formát SERPapi výsledků je strukturovaný JSON
        organic_results = results.get('organic_results', [])

        # Vytvoření čistšího seznamu dat pro uložení
        extracted_data = []
        for result in organic_results:
            extracted_data.append({
                "title": result.get('title'),
                "snippet": result.get('snippet'),
                "link": result.get('link'),
                "position": result.get('position')
            })

        return jsonify(extracted_data), 200

    except Exception as e:
        # V případě chyby API nebo jiné chyby
        print(f"Chyba při volání SerpApi: {e}")
        return jsonify({"error": f"Nastala chyba při komunikaci s vyhledávacím API: {str(e)}"}), 500

if __name__ == '__main__':
    # Při spouštění přes Gunicorn nebo jiný produkční server se tento blok ignoruje.
    # Ponecháno pro lokální spouštění (python app.py).
    print("Backend server spuštěn na http://127.0.0.1:5000")
    app.run(debug=True)
