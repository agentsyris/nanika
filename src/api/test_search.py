import asyncio
from src.worker.search_service import WebSearchService

async def test_search():
    service = WebSearchService()
    
    # Test company search
    results = await service.search_companies("WeWork New York expansion")
    print("Company Search Results:")
    print(json.dumps(results, indent=2))
    
    # Test LinkedIn search
    linkedin = await service.search_linkedin_companies("Spotify")
    print("\nLinkedIn Results:")
    print(json.dumps(linkedin, indent=2))

if __name__ == "__main__":
    asyncio.run(test_search())