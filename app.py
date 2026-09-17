import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai


# ============================================================
# TOURIST DATA
# ============================================================

tourist_places = {
    "Andhra Pradesh": [
        {
            "name": "Tirupati",
            "category": "Temples",
            "description": "A major pilgrimage destination famous for Sri Venkateswara Temple."
        },
        {
            "name": "Araku Valley",
            "category": "Hill Stations",
            "description": "A scenic hill region known for valleys, coffee plantations and waterfalls."
        },
        {
            "name": "Borra Caves",
            "category": "Caves",
            "description": "Large limestone caves in the Ananthagiri Hills with natural rock formations."
        },
    ],

    "Arunachal Pradesh": [
        {
            "name": "Tawang",
            "category": "Hill Stations",
            "description": "A mountain destination known for monasteries, lakes and Himalayan scenery."
        },
        {
            "name": "Ziro Valley",
            "category": "Valleys",
            "description": "A scenic valley surrounded by green hills and known for its natural beauty."
        },
        {
            "name": "Sela Pass",
            "category": "Mountains",
            "description": "A high-altitude mountain pass surrounded by dramatic Himalayan landscapes."
        },
    ],

    "Assam": [
        {
            "name": "Kaziranga National Park",
            "category": "Wildlife",
            "description": "A famous national park known for its one-horned rhinoceroses and rich wildlife."
        },
        {
            "name": "Majuli",
            "category": "Islands",
            "description": "A river island in the Brahmaputra known for its culture and satras."
        },
        {
            "name": "Kamakhya Temple",
            "category": "Temples",
            "description": "A historic temple and important pilgrimage site in Guwahati."
        },
    ],

    "Bihar": [
        {
            "name": "Mahabodhi Temple",
            "category": "Historical Places",
            "description": "A major Buddhist pilgrimage site at Bodh Gaya associated with the enlightenment of Buddha."
        },
        {
            "name": "Nalanda",
            "category": "Historical Places",
            "description": "Ancient university ruins representing an important center of learning."
        },
        {
            "name": "Rajgir",
            "category": "Historical Places",
            "description": "An ancient city surrounded by hills and important Buddhist and Jain sites."
        },
    ],

    "Chhattisgarh": [
        {
            "name": "Chitrakote Falls",
            "category": "Waterfalls",
            "description": "A spectacular waterfall on the Indravati River."
        },
        {
            "name": "Kanger Valley National Park",
            "category": "Wildlife",
            "description": "A forested national park known for caves, waterfalls and biodiversity."
        },
        {
            "name": "Bastar",
            "category": "Nature",
            "description": "A region known for forests, tribal culture, waterfalls and natural landscapes."
        },
    ],

    "Goa": [
        {
            "name": "Baga Beach",
            "category": "Beaches",
            "description": "A popular beach destination known for its coastline and lively tourist area."
        },
        {
            "name": "Dudhsagar Falls",
            "category": "Waterfalls",
            "description": "A dramatic multi-tiered waterfall located in the Western Ghats."
        },
        {
            "name": "Fort Aguada",
            "category": "Forts",
            "description": "A historic Portuguese-era fort overlooking the Arabian Sea."
        },
    ],

    "Gujarat": [
        {
            "name": "Statue of Unity",
            "category": "Historical Places",
            "description": "A major landmark near Kevadia dedicated to Sardar Vallabhbhai Patel."
        },
        {
            "name": "Rann of Kutch",
            "category": "Nature",
            "description": "A vast salt desert famous for its unique landscape and cultural festivals."
        },
        {
            "name": "Somnath Temple",
            "category": "Temples",
            "description": "A renowned Hindu temple located on the Arabian Sea coast."
        },
    ],

    "Haryana": [
        {
            "name": "Sultanpur National Park",
            "category": "Wildlife",
            "description": "A protected area near Gurugram known for migratory and resident birds."
        },
        {
            "name": "Kurukshetra",
            "category": "Historical Places",
            "description": "An important historical and pilgrimage region."
        },
        {
            "name": "Pinjore Gardens",
            "category": "Gardens",
            "description": "Historic Mughal-style gardens near Panchkula."
        },
    ],

    "Himachal Pradesh": [
        {
            "name": "Shimla",
            "category": "Hill Stations",
            "description": "A famous Himalayan hill station known for mountain views and colonial-era architecture."
        },
        {
            "name": "Manali",
            "category": "Hill Stations",
            "description": "A popular mountain destination known for valleys, rivers and adventure activities."
        },
        {
            "name": "Spiti Valley",
            "category": "Valleys",
            "description": "A high-altitude cold desert valley with monasteries and dramatic mountain scenery."
        },
    ],

    "Jharkhand": [
        {
            "name": "Hundru Falls",
            "category": "Waterfalls",
            "description": "A prominent waterfall on the Subarnarekha River near Ranchi."
        },
        {
            "name": "Betla National Park",
            "category": "Wildlife",
            "description": "A protected forest area known for wildlife and natural landscapes."
        },
        {
            "name": "Deoghar",
            "category": "Temples",
            "description": "A major pilgrimage destination famous for Baidyanath Jyotirlinga Temple."
        },
    ],

    "Karnataka": [
        {
            "name": "Mysuru Palace",
            "category": "Historical Places",
            "description": "A grand palace and one of the major attractions of Mysuru."
        },
        {
            "name": "Coorg",
            "category": "Hill Stations",
            "description": "A scenic hill region known for coffee plantations, forests and waterfalls."
        },
        {
            "name": "Hampi",
            "category": "Historical Places",
            "description": "A UNESCO World Heritage area containing extensive ruins of the Vijayanagara Empire."
        },
    ],

    "Kerala": [
        {
            "name": "Munnar",
            "category": "Hill Stations",
            "description": "A mountain destination known for tea plantations, valleys and cool weather."
        },
        {
            "name": "Alappuzha",
            "category": "Backwaters",
            "description": "A famous backwater destination known for houseboats and waterways."
        },
        {
            "name": "Athirappilly Falls",
            "category": "Waterfalls",
            "description": "A major waterfall surrounded by lush forests in the Western Ghats."
        },
    ],

    "Madhya Pradesh": [
        {
            "name": "Khajuraho",
            "category": "Historical Places",
            "description": "A UNESCO World Heritage site famous for historic temple architecture."
        },
        {
            "name": "Kanha National Park",
            "category": "Wildlife",
            "description": "A major tiger reserve and wildlife destination."
        },
        {
            "name": "Sanchi",
            "category": "Historical Places",
            "description": "A UNESCO World Heritage site known for ancient Buddhist monuments."
        },
    ],

    "Maharashtra": [
        {
            "name": "Ajanta Caves",
            "category": "Caves",
            "description": "A UNESCO World Heritage site famous for ancient Buddhist rock-cut caves and paintings."
        },
        {
            "name": "Ellora Caves",
            "category": "Caves",
            "description": "A UNESCO World Heritage site featuring Buddhist, Hindu and Jain rock-cut monuments."
        },
        {
            "name": "Gateway of India",
            "category": "Historical Places",
            "description": "An iconic Mumbai waterfront monument overlooking the Arabian Sea."
        },
        {
            "name": "Mahabaleshwar",
            "category": "Hill Stations",
            "description": "A scenic hill station known for viewpoints, forests and strawberry farms."
        },
        {
            "name": "Lonavala",
            "category": "Hill Stations",
            "description": "A popular hill destination known for valleys, forts and monsoon scenery."
        },
        {
            "name": "Raigad Fort",
            "category": "Forts",
            "description": "A historic hill fort in the Sahyadri mountains."
        },
        {
            "name": "Thoseghar Waterfalls",
            "category": "Waterfalls",
            "description": "A group of waterfalls near Satara surrounded by green landscapes."
        },
        {
            "name": "Alibaug",
            "category": "Beaches",
            "description": "A coastal destination known for beaches and historic forts."
        },
    ],

    "Manipur": [
        {
            "name": "Loktak Lake",
            "category": "Lakes",
            "description": "The largest freshwater lake in northeastern India, famous for floating phumdis."
        },
        {
            "name": "Keibul Lamjao National Park",
            "category": "Wildlife",
            "description": "A unique floating national park associated with the sangai deer."
        },
        {
            "name": "Imphal",
            "category": "Cities",
            "description": "The capital city and a center of history, culture and local attractions."
        },
    ],

    "Meghalaya": [
        {
            "name": "Shillong",
            "category": "Hill Stations",
            "description": "A scenic hill city known for waterfalls, lakes and surrounding hills."
        },
        {
            "name": "Cherrapunji",
            "category": "Nature",
            "description": "A famous destination known for rainfall, waterfalls and living root bridges."
        },
        {
            "name": "Dawki",
            "category": "Rivers",
            "description": "A border destination known for the clear waters of the Umngot River."
        },
    ],

    "Mizoram": [
        {
            "name": "Aizawl",
            "category": "Hill Stations",
            "description": "A hill city known for panoramic views and Mizo culture."
        },
        {
            "name": "Phawngpui",
            "category": "Mountains",
            "description": "A scenic mountain area with forests and viewpoints."
        },
        {
            "name": "Vantawng Falls",
            "category": "Waterfalls",
            "description": "One of the prominent waterfalls of Mizoram surrounded by forested hills."
        },
    ],

    "Nagaland": [
        {
            "name": "Kohima",
            "category": "Cities",
            "description": "The capital city known for hills, history and Naga culture."
        },
        {
            "name": "Dzukou Valley",
            "category": "Valleys",
            "description": "A scenic valley famous for rolling green landscapes and seasonal flowers."
        },
        {
            "name": "Kisama Heritage Village",
            "category": "Cultural Places",
            "description": "A cultural attraction associated with the Hornbill Festival."
        },
    ],

    "Odisha": [
        {
            "name": "Konark Sun Temple",
            "category": "Historical Places",
            "description": "A UNESCO World Heritage monument famous for its temple architecture."
        },
        {
            "name": "Jagannath Temple",
            "category": "Temples",
            "description": "A major pilgrimage temple in Puri dedicated to Lord Jagannath."
        },
        {
            "name": "Chilika Lake",
            "category": "Lakes",
            "description": "A large coastal lagoon known for birds, dolphins and scenic landscapes."
        },
    ],

    "Punjab": [
        {
            "name": "Golden Temple",
            "category": "Temples",
            "description": "A major Sikh pilgrimage site in Amritsar known for its golden architecture."
        },
        {
            "name": "Jallianwala Bagh",
            "category": "Historical Places",
            "description": "A historic memorial site in Amritsar."
        },
        {
            "name": "Wagah-Attari Border",
            "category": "Places",
            "description": "A well-known border location famous for ceremonial activities."
        },
    ],

    "Rajasthan": [
        {
            "name": "Jaipur City Palace",
            "category": "Historical Places",
            "description": "A major palace complex in the historic city of Jaipur."
        },
        {
            "name": "Amer Fort",
            "category": "Forts",
            "description": "A famous hill fort near Jaipur known for its architecture and courtyards."
        },
        {
            "name": "Jaisalmer Fort",
            "category": "Forts",
            "description": "A historic sandstone fort rising from the Thar Desert."
        },
    ],

    "Sikkim": [
        {
            "name": "Gangtok",
            "category": "Hill Stations",
            "description": "A mountain city known for Himalayan views, monasteries and culture."
        },
        {
            "name": "Tsomgo Lake",
            "category": "Lakes",
            "description": "A high-altitude glacial lake near Gangtok."
        },
        {
            "name": "Nathula Pass",
            "category": "Mountains",
            "description": "A high-altitude mountain pass in the eastern Himalayas."
        },
    ],

    "Tamil Nadu": [
        {
            "name": "Ooty",
            "category": "Hill Stations",
            "description": "A popular hill station known for gardens, tea plantations and cool weather."
        },
        {
            "name": "Meenakshi Amman Temple",
            "category": "Temples",
            "description": "A famous historic temple complex in Madurai."
        },
        {
            "name": "Mahabalipuram",
            "category": "Historical Places",
            "description": "A UNESCO World Heritage site known for ancient rock-cut monuments and temples."
        },
    ],

    "Telangana": [
        {
            "name": "Charminar",
            "category": "Historical Places",
            "description": "An iconic historic monument in Hyderabad."
        },
        {
            "name": "Golconda Fort",
            "category": "Forts",
            "description": "A historic fort complex known for its architecture and history."
        },
        {
            "name": "Ramappa Temple",
            "category": "Temples",
            "description": "A UNESCO World Heritage temple known for distinctive medieval architecture."
        },
    ],

    "Tripura": [
        {
            "name": "Ujjayanta Palace",
            "category": "Historical Places",
            "description": "A prominent palace and landmark in Agartala."
        },
        {
            "name": "Neermahal",
            "category": "Palaces",
            "description": "A beautiful palace located in the middle of Rudrasagar Lake."
        },
        {
            "name": "Unakoti",
            "category": "Historical Places",
            "description": "A historic site famous for large rock-cut sculptures."
        },
    ],

    "Uttar Pradesh": [
        {
            "name": "Taj Mahal",
            "category": "Historical Places",
            "description": "A UNESCO World Heritage monument and iconic example of Mughal architecture."
        },
        {
            "name": "Varanasi Ghats",
            "category": "Cultural Places",
            "description": "Historic riverfront ghats along the Ganges in Varanasi."
        },
        {
            "name": "Agra Fort",
            "category": "Forts",
            "description": "A UNESCO World Heritage fort in Agra with major Mughal-era structures."
        },
    ],

    "Uttarakhand": [
        {
            "name": "Nainital",
            "category": "Hill Stations",
            "description": "A popular hill station centered around Naini Lake."
        },
        {
            "name": "Mussoorie",
            "category": "Hill Stations",
            "description": "A well-known Himalayan foothill hill station."
        },
        {
            "name": "Valley of Flowers",
            "category": "National Parks",
            "description": "A Himalayan valley famous for alpine flowers and mountain scenery."
        },
    ],

    "West Bengal": [
        {
            "name": "Darjeeling",
            "category": "Hill Stations",
            "description": "A famous hill station known for tea gardens and Himalayan views."
        },
        {
            "name": "Victoria Memorial",
            "category": "Historical Places",
            "description": "A prominent marble monument and museum in Kolkata."
        },
        {
            "name": "Sundarbans National Park",
            "category": "Wildlife",
            "description": "A UNESCO World Heritage mangrove ecosystem known for rich wildlife."
        },
    ],

    # Union Territories

    "Andaman and Nicobar Islands": [
        {
            "name": "Swaraj Dweep",
            "category": "Beaches",
            "description": "A popular island destination known for beaches and marine activities."
        },
        {
            "name": "Radhanagar Beach",
            "category": "Beaches",
            "description": "A well-known beach on Swaraj Dweep."
        },
        {
            "name": "Cellular Jail",
            "category": "Historical Places",
            "description": "A historic former prison and important memorial in Port Blair."
        },
    ],

    "Chandigarh": [
        {
            "name": "Rock Garden",
            "category": "Gardens",
            "description": "A unique sculpture garden created from industrial and household waste materials."
        },
        {
            "name": "Sukhna Lake",
            "category": "Lakes",
            "description": "A popular man-made lake and recreation area."
        },
        {
            "name": "Capitol Complex",
            "category": "Architecture",
            "description": "A major architectural landmark of Chandigarh."
        },
    ],

    "Dadra and Nagar Haveli and Daman and Diu": [
        {
            "name": "Diu Fort",
            "category": "Forts",
            "description": "A historic coastal fort overlooking the Arabian Sea."
        },
        {
            "name": "Nagoa Beach",
            "category": "Beaches",
            "description": "A popular beach destination in Diu."
        },
        {
            "name": "Silvassa",
            "category": "Nature",
            "description": "A destination known for greenery, gardens and nearby attractions."
        },
    ],

    "Delhi": [
        {
            "name": "India Gate",
            "category": "Historical Places",
            "description": "A prominent war memorial and landmark in central Delhi."
        },
        {
            "name": "Red Fort",
            "category": "Forts",
            "description": "A UNESCO World Heritage Mughal fort and major Delhi landmark."
        },
        {
            "name": "Qutub Minar",
            "category": "Historical Places",
            "description": "A UNESCO World Heritage monument known for its historic minaret complex."
        },
    ],

    "Jammu and Kashmir": [
        {
            "name": "Srinagar",
            "category": "Cities",
            "description": "A scenic destination known for Dal Lake, gardens and Himalayan surroundings."
        },
        {
            "name": "Gulmarg",
            "category": "Hill Stations",
            "description": "A mountain destination known for meadows and the surrounding Himalayas."
        },
        {
            "name": "Pahalgam",
            "category": "Valleys",
            "description": "A scenic valley destination surrounded by mountains and forests."
        },
    ],

    "Ladakh": [
        {
            "name": "Leh",
            "category": "Mountains",
            "description": "A high-altitude town surrounded by dramatic Himalayan landscapes."
        },
        {
            "name": "Pangong Lake",
            "category": "Lakes",
            "description": "A high-altitude lake famous for its striking mountain scenery."
        },
        {
            "name": "Nubra Valley",
            "category": "Valleys",
            "description": "A high-altitude valley known for mountains, villages and unique landscapes."
        },
    ],

    "Lakshadweep": [
        {
            "name": "Kavaratti",
            "category": "Islands",
            "description": "A beautiful island known for lagoons, beaches and marine scenery."
        },
        {
            "name": "Agatti Island",
            "category": "Beaches",
            "description": "An island known for its lagoon, beaches and clear coastal waters."
        },
        {
            "name": "Bangaram Island",
            "category": "Islands",
            "description": "A scenic island destination surrounded by turquoise waters."
        },
    ],

    "Puducherry": [
        {
            "name": "Promenade Beach",
            "category": "Beaches",
            "description": "A popular seafront area in the heart of Puducherry."
        },
        {
            "name": "Auroville",
            "category": "Cultural Places",
            "description": "An international community known for its distinctive cultural and architectural setting."
        },
        {
            "name": "Sri Aurobindo Ashram",
            "category": "Cultural Places",
            "description": "A well-known spiritual and cultural center in Puducherry."
        },
    ],
}


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Explore India Tourist API",
    description="API for discovering tourist places across Indian States and Union Territories.",
    version="2.0.0"
)


# ============================================================
# FRONTEND
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# GEMINI SETUP
# ============================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)

client = (
    genai.Client(api_key=GOOGLE_API_KEY)
    if GOOGLE_API_KEY
    else None
)


# ============================================================
# REQUEST MODEL
# ============================================================

class AskRequest(BaseModel):
    question: str
    state: Optional[str] = None


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/", include_in_schema=False)
def home():
    return FileResponse("static/index.html")


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "gemini_configured": client is not None,
        "gemini_model": GEMINI_MODEL
    }


# ============================================================
# GET STATES
# ============================================================

@app.get("/states")
def get_states():
    return {
        "total_states_and_ut": len(tourist_places),
        "states": sorted(tourist_places.keys())
    }


# ============================================================
# GET PLACES BY STATE
# ============================================================

@app.get("/places/{state}")
def get_places(state: str):

    matched_state = next(
        (
            name
            for name in tourist_places
            if name.lower() == state.lower()
        ),
        None
    )

    if matched_state is None:
        raise HTTPException(
            status_code=404,
            detail="State or Union Territory not found"
        )

    places = tourist_places[matched_state]

    return {
        "state": matched_state,
        "total_places": len(places),
        "places": places
    }


# ============================================================
# GET CATEGORIES
# ============================================================

@app.get("/categories")
def get_categories():

    categories = sorted({
        place["category"]
        for places in tourist_places.values()
        for place in places
    })

    return {
        "total_categories": len(categories),
        "categories": categories
    }


# ============================================================
# SEARCH
# ============================================================

@app.get("/search")
def search_places(q: str):

    query = q.strip().lower()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    results = []

    for state, places in tourist_places.items():

        for place in places:

            searchable_text = (
                place["name"]
                + " "
                + place["category"]
                + " "
                + place["description"]
            ).lower()

            if query in searchable_text:

                results.append({
                    "state": state,
                    **place
                })

    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }


# ============================================================
# GEMINI AI TOURISM ASSISTANT
# ============================================================

@app.post("/ask")
def ask_gemini(request: AskRequest):

    if client is None:

        raise HTTPException(
            status_code=500,
            detail="GOOGLE_API_KEY is not configured on the server."
        )

    context = ""

    if request.state:

        matched_state = next(
            (
                name
                for name in tourist_places
                if name.lower() == request.state.lower()
            ),
            None
        )

        if matched_state:

            context = (
                f"\nTourist data for {matched_state}:\n"
                + str(tourist_places[matched_state])
            )

    prompt = f"""
You are a helpful India tourism assistant.

Answer the user's tourism question clearly and briefly.

Use the provided tourist data when relevant.

Do not invent exact prices, opening hours, travel distances,
or current conditions.

User question:
{request.question}

{context}
"""

    try:

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        return {
            "model": GEMINI_MODEL,
            "answer": response.text
        }

    except Exception as e:

        raise HTTPException(
            status_code=503,
            detail=f"Gemini service temporarily unavailable: {str(e)}"
        )


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    port = int(
        os.getenv("PORT", "8000")
    )

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port
    )
