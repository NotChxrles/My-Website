import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from urllib.parse import urljoin

def search_sep(keyword):
    """Search the Stanford Encyclopedia of Philosophy for a keyword."""
    base_url = "https://plato.stanford.edu/"
    search_url = urljoin(base_url, "search/searcher.py")
    
    params = {
        "query": keyword.strip(),
        "start": 0,
        "limit": 10
    }
    
    headers = {
        "User-Agent": "Philosophy Research Bot (Academic Project)"
    }
    
    response = requests.get(search_url, params=params, headers=headers)
    if response.status_code != 200:
        print(f"Error searching for '{keyword}': HTTP {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find search results
    results = soup.select('.result_title a')
    if not results:
        print(f"No results found for '{keyword}'")
        return None
    
    # Get the first result URL
    first_result_url = urljoin(base_url, results[0]['href'])
    return first_result_url

def extract_content(url):
    """Extract content from an SEP entry."""
    headers = {
        "User-Agent": "Philosophy Research Bot (Academic Project)"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error accessing '{url}': HTTP {response.status_code}")
        return None, None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract title
    title = soup.select_one('h1').text.strip() if soup.select_one('h1') else "Unknown Title"
    
    # Extract main content (excluding navigation, bibliography, etc.)
    content_div = soup.select_one('#article-content')
    
    if not content_div:
        print(f"Could not find main content in '{url}'")
        return title, None
    
    # Remove bibliography, notes, etc.
    for to_remove in content_div.select('.bibliography, .note'):
        if to_remove:
            to_remove.decompose()
    
    # Get text content
    content = content_div.get_text(separator=' ', strip=True)
    
    # Clean up extra whitespace
    content = re.sub(r'\s+', ' ', content).strip()
    
    return title, content

def main():
    print("Stanford Encyclopedia of Philosophy Content Extractor")
    print("----------------------------------------------------")
    keywords = input("Enter keywords (separated by commas): ").split(',')
    
    results = []
    
    for keyword in keywords:
        keyword = keyword.strip()
        if not keyword:
            continue
            
        print(f"\nSearching for '{keyword}'...")
        url = search_sep(keyword)
        
        if url:
            print(f"Found entry at {url}")
            print("Extracting content...")
            title, content = extract_content(url)
            
            if content:
                results.append({"Title": title, "Content": content})
                print(f"Successfully extracted '{title}' ({len(content)} characters)")
            else:
                print(f"Failed to extract content for '{keyword}'")
        
        # Be respectful with rate limiting
        time.sleep(2)
    
    if results:
        filename = "stanford_philosophy_entries.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Title', 'Content']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        
        print(f"\nSuccessfully saved {len(results)} entries to {filename}")
    else:
        print("\nNo entries were found or extracted.")

if __name__ == "__main__":
    main()