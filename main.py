from fastapi import FastAPI, HTTPException, Request
from datetime import datetime
import whois
import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Allow CORS for all origins (adjust as necessary for your use case)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, or specify your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def render_homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/website-age/")
def get_webiste_age(domain: str):
    try:
        # Fetch domain information using the whois package
        domain_info = whois.whois(domain)

        if domain_info.creation_date:
            creation_date = domain_info.creation_date

            if isinstance(creation_date, list):
                creation_date = creation_date[0]

            # calculate te age
            current_time = datetime.now()
            age_in_days = (current_time - creation_date).days

            age_in_years = age_in_days / 364.25

            return {
                "domain":domain,
                "creation_date": creation_date.strftime("%Y-%m-%d"),
                "age_in_days": age_in_days,
                "age_in_years": round(age_in_years)
                }
        else:
            raise HTTPException(status_code=404, detail="creation date not found!!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/find_subdomains/{domain}")
def find_subdomains(domain: str):
    url = f"https://crt.sh/?q={domain}&output=json"
    response = requests.get(url)

    # Check if the response is successful
    if response.status_code == 200:
        data = response.json()

        subdomains = set()  # Use a set to avoid duplicates
        for i in data:
            name_value = i.get('name_value')
            print("name_value", name_value)
            if name_value:
                # Split the subdomain names on newline characters and add to set
                subdomains.update(name_value.split('\n'))
        
        # Sort the subdomains for better readability
        return {"domain": domain, "subdomains": sorted(subdomains)}
    else:
        return {"error": f"Error fetching subdomain for {domain}, status code: {response.status_code}"}
    
        