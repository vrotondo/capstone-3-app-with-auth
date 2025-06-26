import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
import json
import os

class BlackBeltWikiScraper:
    """
    Fixed web scraper for BlackBeltWiki.com
    Uses actual working URLs and respectful scraping
    """
    
    def __init__(self, base_url='https://blackbeltwiki.com', delay=2):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DojoTracker/1.0 (Educational Martial Arts App)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        
        self.cache_dir = 'scraped_content'
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _make_request(self, url):
        """Make a respectful HTTP request with rate limiting"""
        print(f"🌐 Fetching: {url}")
        
        try:
            time.sleep(self.delay)
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            print(f"✅ Success: {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def discover_technique_urls(self, max_pages=5):
        """Discover technique URLs from BlackBeltWiki using real URLs"""
        technique_urls = set()
        
        # These are actual working URLs based on BlackBeltWiki structure
        discovery_urls = [
            f"{self.base_url}/wiki/Main_Page",
            f"{self.base_url}/wiki/Kicks",
            f"{self.base_url}/wiki/Punches", 
            f"{self.base_url}/wiki/Strikes",
            f"{self.base_url}/wiki/Blocks",
            f"{self.base_url}/wiki/Karate",
            f"{self.base_url}/wiki/Taekwondo",
            f"{self.base_url}/wiki/Martial_Arts"
        ]
        
        print("🔍 Discovering technique URLs from BlackBeltWiki...")
        
        for discovery_url in discovery_urls:
            print(f"🔍 Checking: {discovery_url}")
            
            response = self._make_request(discovery_url)
            if not response:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href')
                if not href:
                    continue
                
                full_url = urljoin(self.base_url, href)
                link_text = link.get_text().strip()
                
                if self._is_technique_url(full_url, link_text):
                    technique_urls.add(full_url)
            
            if len(technique_urls) >= max_pages * 20:
                break
        
        # Add some known technique URLs for testing
        known_techniques = [
            f"{self.base_url}/wiki/Front_Kick",
            f"{self.base_url}/wiki/Side_Kick", 
            f"{self.base_url}/wiki/Roundhouse_Kick",
            f"{self.base_url}/wiki/Back_Kick",
            f"{self.base_url}/wiki/Hook_Kick",
            f"{self.base_url}/wiki/Axe_Kick",
            f"{self.base_url}/wiki/Reverse_Punch",
            f"{self.base_url}/wiki/Jab",
            f"{self.base_url}/wiki/Cross_Punch",
            f"{self.base_url}/wiki/Uppercut"
        ]
        
        for url in known_techniques:
            technique_urls.add(url)
        
        print(f"📊 Discovered {len(technique_urls)} potential technique URLs")
        return list(technique_urls)
    
    def _is_technique_url(self, url, link_text=''):
        """Determine if a URL likely contains technique information"""
        url_lower = url.lower()
        text_lower = link_text.lower()
        
        # Technique-related keywords
        technique_keywords = [
            'kick', 'punch', 'strike', 'block', 'throw', 'sweep', 'grappling',
            'technique', 'form', 'kata', 'poomsae', 'hyung',
            'front', 'side', 'round', 'back', 'hook', 'upper', 'reverse',
            'chop', 'elbow', 'knee', 'heel', 'toe'
        ]
        
        # Exclude non-technique URLs
        exclude_keywords = [
            'category:', 'file:', 'image:', 'template:', 'user:',
            'special:', 'help:', 'talk:', 'edit', 'history',
            'login', 'register', 'search', 'random', 'main_page',
            'index.php', 'action=', '#'
        ]
        
        # Check exclusions
        for exclude in exclude_keywords:
            if exclude in url_lower:
                return False
        
        # Check for technique keywords
        for keyword in technique_keywords:
            if keyword in url_lower or keyword in text_lower:
                return True
        
        # Check if it's a wiki page (likely to be a technique)
        if '/wiki/' in url_lower and len(link_text) > 3:
            # Additional checks for likely technique pages
            if any(char.isupper() for char in link_text):  # Has capital letters
                return True
        
        return False
    
    def _parse_technique_page(self, html_content, url):
        """Parse a technique page and extract structured data"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        technique_data = {
            'name': '',
            'style': '',
            'category': '',
            'description': '',
            'instructions': '',
            'tips': '',
            'variations': '',
            'source_url': url,
            'tags': [],
            'difficulty_level': None,
            'belt_level': None
        }
        
        try:
            # Extract title - try multiple selectors
            title_selectors = [
                'h1.firstHeading',
                'h1.page-title', 
                'h1',
                '.mw-page-title-main',
                '#firstHeading'
            ]
            
            title_elem = None
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    break
            
            if title_elem:
                technique_data['name'] = title_elem.get_text().strip()
            
            # Extract main content
            content_selectors = [
                '#mw-content-text',
                '.mw-parser-output',
                '#content',
                '.entry-content',
                'main'
            ]
            
            content_area = None
            for selector in content_selectors:
                content_area = soup.select_one(selector)
                if content_area:
                    break
            
            if content_area:
                # Extract text content
                paragraphs = content_area.find_all('p')
                descriptions = []
                instructions = []
                
                for i, p in enumerate(paragraphs[:8]):
                    text = p.get_text().strip()
                    if text and len(text) > 20:  # Meaningful content
                        if i < 3:
                            descriptions.append(text)
                        else:
                            instructions.append(text)
                
                technique_data['description'] = '\n\n'.join(descriptions)
                technique_data['instructions'] = '\n\n'.join(instructions)
                
                # Extract lists for steps/variations
                lists = content_area.find_all(['ul', 'ol'])
                variations = []
                for list_elem in lists:
                    items = [li.get_text().strip() for li in list_elem.find_all('li')]
                    variations.extend(items[:5])  # Limit items
                
                if variations:
                    technique_data['variations'] = '\n'.join(f"• {item}" for item in variations)
            
            # Extract category from URL or title
            url_parts = url.lower().split('/')
            title_lower = technique_data['name'].lower()
            
            if 'kick' in url_parts or 'kick' in title_lower:
                technique_data['category'] = 'Kicks'
            elif 'punch' in url_parts or 'punch' in title_lower:
                technique_data['category'] = 'Punches'
            elif 'block' in url_parts or 'block' in title_lower:
                technique_data['category'] = 'Blocks'
            elif 'throw' in url_parts or 'throw' in title_lower:
                technique_data['category'] = 'Throws'
            elif any(word in title_lower for word in ['strike', 'chop', 'elbow']):
                technique_data['category'] = 'Strikes'
            
            # Extract style from content or URL
            content_text = soup.get_text().lower()
            styles = ['karate', 'taekwondo', 'judo', 'jiu-jitsu', 'bjj', 'kung fu', 'aikido', 'boxing']
            
            for style in styles:
                if style in content_text or style in url.lower():
                    technique_data['style'] = style.title()
                    break
            
            if not technique_data['style']:
                technique_data['style'] = 'General'
            
            # Estimate difficulty
            if technique_data['instructions']:
                instruction_length = len(technique_data['instructions'])
                if 'advanced' in content_text or 'difficult' in content_text:
                    technique_data['difficulty_level'] = 8
                elif 'intermediate' in content_text:
                    technique_data['difficulty_level'] = 5
                elif 'basic' in content_text or 'beginner' in content_text:
                    technique_data['difficulty_level'] = 3
                elif instruction_length > 500:
                    technique_data['difficulty_level'] = 6
                else:
                    technique_data['difficulty_level'] = 4
            
            # Extract belt level
            belt_patterns = [
                r'(white|yellow|orange|green|blue|brown|black)\s+belt',
                r'beginner|intermediate|advanced'
            ]
            
            for pattern in belt_patterns:
                match = re.search(pattern, content_text)
                if match:
                    technique_data['belt_level'] = match.group(0).strip().title()
                    break
            
            # Create tags
            tags = []
            if technique_data['category']:
                tags.append(technique_data['category'].lower())
            if technique_data['style'] and technique_data['style'] != 'General':
                tags.append(technique_data['style'].lower())
            
            # Add descriptive tags
            if 'front' in title_lower:
                tags.append('linear')
            elif 'round' in title_lower or 'hook' in title_lower:
                tags.append('circular')
            elif 'reverse' in title_lower or 'back' in title_lower:
                tags.append('reverse')
            
            technique_data['tags'] = tags
            
        except Exception as e:
            print(f"⚠️ Error parsing technique page: {e}")
        
        return technique_data
    
    def scrape_techniques(self, max_techniques=20):
        """Main method to scrape techniques"""
        print("🥋 Starting BlackBeltWiki technique scraping...")
        
        # Discover URLs
        technique_urls = self.discover_technique_urls()
        
        if not technique_urls:
            print("❌ No technique URLs discovered")
            return []
        
        scraped_techniques = []
        urls_to_scrape = technique_urls[:max_techniques]
        
        print(f"📥 Scraping {len(urls_to_scrape)} technique pages...")
        
        for i, url in enumerate(urls_to_scrape, 1):
            print(f"\n📄 {i}/{len(urls_to_scrape)}: Processing {url}")
            
            # Check cache first
            cached_data = self._load_from_cache(url)
            if cached_data:
                print("📁 Using cached data")
                scraped_techniques.append(cached_data)
                continue
            
            # Scrape the page
            response = self._make_request(url)
            if not response:
                continue
            
            technique_data = self._parse_technique_page(response.text, url)
            
            if technique_data['name']:
                scraped_techniques.append(technique_data)
                self._save_to_cache(url, technique_data)
                print(f"✅ Scraped: {technique_data['name']} ({technique_data['style']})")
            else:
                print("⚠️ No technique name found, skipping")
        
        print(f"\n🎉 Scraping complete! Found {len(scraped_techniques)} techniques")
        return scraped_techniques
    
    def _load_from_cache(self, url):
        """Load cached technique data"""
        cache_filename = self._get_cache_filename(url)
        cache_path = os.path.join(self.cache_dir, cache_filename)
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Cache read error: {e}")
        return None
    
    def _save_to_cache(self, url, data):
        """Save technique data to cache"""
        cache_filename = self._get_cache_filename(url)
        cache_path = os.path.join(self.cache_dir, cache_filename)
        
        try:
            data['cached_at'] = datetime.utcnow().isoformat()
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Cache write error: {e}")
    
    def _get_cache_filename(self, url):
        """Generate cache filename from URL"""
        parsed = urlparse(url)
        filename = f"{parsed.netloc}_{parsed.path}".replace('/', '_').replace('\\', '_')
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)[:100]
        return f"{filename}.json"

# Test function
def test_scraper():
    """Test the scraper with a few techniques"""
    scraper = BlackBeltWikiScraper(delay=1)
    techniques = scraper.scrape_techniques(max_techniques=3)
    
    print("\n📊 Test Results:")
    for technique in techniques:
        print(f"✅ {technique['name']} ({technique['style']})")
        if technique['description']:
            print(f"   Description: {technique['description'][:100]}...")
        print()

if __name__ == "__main__":
    test_scraper()