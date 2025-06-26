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
    Enhanced BlackBeltWiki scraper with better URL discovery and content parsing
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
    
    def discover_technique_urls(self, max_pages=50):
        """Enhanced technique URL discovery"""
        technique_urls = set()
        
        # Updated discovery strategy - use actual BlackBeltWiki structure
        discovery_pages = [
            # Main technique category pages
            f"{self.base_url}/kicking-techniques",
            f"{self.base_url}/striking-techniques", 
            f"{self.base_url}/blocking-techniques",
            f"{self.base_url}/grappling-techniques",
            f"{self.base_url}/punching-techniques",
            f"{self.base_url}/karate-techniques",
            f"{self.base_url}/taekwondo-techniques",
            f"{self.base_url}/aikido-techniques",
            f"{self.base_url}/judo-techniques",
            f"{self.base_url}/kung-fu-techniques",
            f"{self.base_url}/martial-arts-kicks",
            f"{self.base_url}/martial-arts-punches",
            f"{self.base_url}/self-defense-techniques"
        ]
        
        # Add some known individual technique URLs
        known_techniques = [
            f"{self.base_url}/front-kick",
            f"{self.base_url}/roundhouse-kick",
            f"{self.base_url}/side-kick",
            f"{self.base_url}/back-kick",
            f"{self.base_url}/hook-kick",
            f"{self.base_url}/axe-kick",
            f"{self.base_url}/crescent-kick",
            f"{self.base_url}/spinning-heel-kick",
            f"{self.base_url}/jumping-front-kick",
            f"{self.base_url}/reverse-punch",
            f"{self.base_url}/jab-punch",
            f"{self.base_url}/cross-punch",
            f"{self.base_url}/hook-punch",
            f"{self.base_url}/uppercut",
            f"{self.base_url}/hammer-fist",
            f"{self.base_url}/knife-hand-strike",
            f"{self.base_url}/elbow-strike",
            f"{self.base_url}/rising-block",
            f"{self.base_url}/down-block",
            f"{self.base_url}/inside-block",
            f"{self.base_url}/outside-block",
            f"{self.base_url}/hip-throw",
            f"{self.base_url}/shoulder-throw",
            f"{self.base_url}/foot-sweep",
            f"{self.base_url}/arm-bar",
            f"{self.base_url}/rear-naked-choke"
        ]
        
        # Add known techniques first
        for url in known_techniques:
            technique_urls.add(url)
        
        print("🔍 Discovering technique URLs from BlackBeltWiki category pages...")
        
        for discovery_url in discovery_pages:
            if len(technique_urls) >= max_pages:
                break
                
            print(f"🔍 Checking category page: {discovery_url}")
            
            response = self._make_request(discovery_url)
            if not response:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links on the page
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href')
                if not href:
                    continue
                
                # Create full URL
                if href.startswith('/'):
                    full_url = self.base_url + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(discovery_url, href)
                
                link_text = link.get_text().strip()
                
                # Check if this looks like a technique URL
                if self._is_technique_url(full_url, link_text):
                    technique_urls.add(full_url)
                    
                    if len(technique_urls) >= max_pages:
                        break
        
        print(f"📊 Discovered {len(technique_urls)} potential technique URLs")
        return list(technique_urls)
    
    def _is_technique_url(self, url, link_text=''):
        """Enhanced technique URL detection"""
        url_lower = url.lower()
        text_lower = link_text.lower()
        
        # Must be from blackbeltwiki
        if 'blackbeltwiki.com' not in url_lower:
            return False
        
        # Exclude obvious non-technique pages
        exclude_patterns = [
            'category:', 'file:', 'image:', 'template:', 'user:', 'special:', 'help:',
            'talk:', 'edit', 'history', 'login', 'register', 'search', 'random',
            'main-page', 'index.php', 'action=', '#', 'contact', 'about',
            'privacy', 'terms', 'legal', 'disclaimer', 'best-books', 'amazon',
            'donate', 'forum', 'blog', 'news', 'events', 'shop', 'store'
        ]
        
        for pattern in exclude_patterns:
            if pattern in url_lower:
                return False
        
        # Look for technique-related keywords
        technique_keywords = [
            # Basic techniques
            'kick', 'punch', 'strike', 'block', 'throw', 'sweep', 'choke', 'lock',
            'grab', 'hold', 'takedown', 'submission', 'escape', 'counter',
            
            # Specific techniques
            'front', 'side', 'round', 'back', 'hook', 'axe', 'crescent', 'spinning',
            'jumping', 'flying', 'heel', 'toe', 'knee', 'elbow', 'head', 'hammer',
            'knife', 'ridge', 'palm', 'finger', 'thumb', 'reverse', 'straight',
            'cross', 'jab', 'uppercut', 'overhead', 'rising', 'down', 'inside',
            'outside', 'circular', 'linear',
            
            # Positions and stances
            'stance', 'guard', 'position', 'ready', 'fighting', 'horse',
            
            # Grappling terms
            'arm-bar', 'leg-lock', 'hip-throw', 'shoulder-throw', 'foot-sweep',
            'rear-naked', 'triangle', 'kimura', 'americana', 'guillotine',
            
            # General martial arts terms
            'technique', 'form', 'kata', 'poomsae', 'hyung', 'pattern', 'set',
            'combination', 'sequence', 'drill', 'exercise', 'training',
            
            # Weapons (if applicable)
            'staff', 'stick', 'sword', 'knife', 'nunchaku', 'sai', 'tonfa'
        ]
        
        # Check for technique keywords in URL or link text
        for keyword in technique_keywords:
            if keyword in url_lower or keyword in text_lower:
                return True
        
        # Additional checks for likely technique pages
        if len(link_text) > 3 and len(link_text) < 100:
            # Check if it looks like a technique name
            words = text_lower.split()
            if len(words) >= 2 and len(words) <= 6:
                # Contains martial arts terms
                martial_arts_terms = [
                    'martial', 'arts', 'karate', 'taekwondo', 'judo', 'jiu-jitsu',
                    'bjj', 'kung', 'fu', 'aikido', 'boxing', 'muay', 'thai',
                    'krav', 'maga', 'wing', 'chun', 'hapkido', 'capoeira'
                ]
                
                for term in martial_arts_terms:
                    if term in text_lower or term in url_lower:
                        return True
        
        return False
    
    def _parse_technique_page(self, html_content, url):
        """Enhanced technique page parsing"""
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
            # Extract title with better selectors
            title_selectors = [
                'h1.entry-title',
                'h1.page-title',
                'h1.post-title',
                'h1.firstHeading',
                'h1',
                '.entry-header h1',
                '.page-header h1'
            ]
            
            title_elem = None
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    break
            
            if title_elem:
                title_text = title_elem.get_text().strip()
                # Clean up common title suffixes
                title_text = re.sub(r'\s*[-–—]\s*Martial Arts.*$', '', title_text)
                title_text = re.sub(r'\s*[-–—]\s*Black Belt Wiki.*$', '', title_text)
                technique_data['name'] = title_text
            
            # Extract main content with better selectors
            content_selectors = [
                '.entry-content',
                '.post-content', 
                '.content',
                '#mw-content-text',
                '.mw-parser-output',
                'main',
                'article'
            ]
            
            content_area = None
            for selector in content_selectors:
                content_area = soup.select_one(selector)
                if content_area:
                    break
            
            if content_area:
                # Extract structured content
                sections = self._extract_content_sections(content_area)
                
                technique_data['description'] = sections.get('description', '')
                technique_data['instructions'] = sections.get('instructions', '')
                technique_data['tips'] = sections.get('tips', '')
                technique_data['variations'] = sections.get('variations', '')
            
            # Extract category and style with better logic
            self._extract_technique_metadata(technique_data, soup, url)
            
            # Extract difficulty and belt level
            self._extract_difficulty_info(technique_data, soup)
            
            # Generate tags
            technique_data['tags'] = self._generate_tags(technique_data)
            
        except Exception as e:
            print(f"⚠️ Error parsing technique page: {e}")
        
        return technique_data
    
    def _extract_content_sections(self, content_area):
        """Extract structured content sections"""
        sections = {
            'description': '',
            'instructions': '',
            'tips': '',
            'variations': ''
        }
        
        # Get all paragraphs and headings
        elements = content_area.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol'])
        
        current_section = 'description'
        description_paragraphs = []
        instruction_paragraphs = []
        tip_paragraphs = []
        variation_items = []
        
        for element in elements:
            text = element.get_text().strip()
            
            if not text or len(text) < 10:
                continue
            
            # Check for section headers
            if element.name in ['h1', 'h2', 'h3', 'h4']:
                header_text = text.lower()
                if any(word in header_text for word in ['instruction', 'step', 'how to', 'technique']):
                    current_section = 'instructions'
                elif any(word in header_text for word in ['tip', 'hint', 'remember', 'important']):
                    current_section = 'tips'
                elif any(word in header_text for word in ['variation', 'alternative', 'similar', 'related']):
                    current_section = 'variations'
                continue
            
            # Process content based on current section
            if element.name == 'p':
                if current_section == 'description' and len(description_paragraphs) < 3:
                    description_paragraphs.append(text)
                elif current_section == 'instructions':
                    instruction_paragraphs.append(text)
                elif current_section == 'tips':
                    tip_paragraphs.append(text)
            
            elif element.name in ['ul', 'ol']:
                items = [li.get_text().strip() for li in element.find_all('li')]
                if current_section == 'variations':
                    variation_items.extend(items[:5])  # Limit variations
                elif current_section == 'instructions' and not instruction_paragraphs:
                    instruction_paragraphs.extend(items[:10])  # Use list as instructions
        
        # Compile sections
        sections['description'] = '\n\n'.join(description_paragraphs)
        sections['instructions'] = '\n\n'.join(instruction_paragraphs)
        sections['tips'] = '\n\n'.join(tip_paragraphs)
        
        if variation_items:
            sections['variations'] = '\n'.join(f"• {item}" for item in variation_items)
        
        return sections
    
    def _extract_technique_metadata(self, technique_data, soup, url):
        """Extract style and category information"""
        content_text = soup.get_text().lower()
        
        # Extract martial arts style
        style_patterns = [
            r'\b(karate)\b', r'\b(taekwondo)\b', r'\b(judo)\b', r'\b(jiu-jitsu|jiujitsu|bjj)\b',
            r'\b(kung fu|kungfu)\b', r'\b(aikido)\b', r'\b(boxing)\b', r'\b(muay thai)\b',
            r'\b(krav maga)\b', r'\b(wing chun)\b', r'\b(hapkido)\b', r'\b(capoeira)\b',
            r'\b(kickboxing)\b', r'\b(mixed martial arts|mma)\b'
        ]
        
        for pattern in style_patterns:
            match = re.search(pattern, content_text)
            if match:
                style = match.group(1).replace('-', ' ').title()
                if style == 'Bjj':
                    style = 'Brazilian Jiu-Jitsu'
                elif style == 'Mma':
                    style = 'Mixed Martial Arts'
                technique_data['style'] = style
                break
        
        if not technique_data['style']:
            # Fallback: check URL for style indicators
            url_lower = url.lower()
            if 'karate' in url_lower:
                technique_data['style'] = 'Karate'
            elif 'taekwondo' in url_lower:
                technique_data['style'] = 'Taekwondo'
            else:
                technique_data['style'] = 'General'
        
        # Extract category
        name_lower = technique_data['name'].lower()
        
        if any(word in name_lower for word in ['kick', 'heel', 'knee']):
            technique_data['category'] = 'Kicks'
        elif any(word in name_lower for word in ['punch', 'jab', 'cross', 'hook', 'uppercut', 'fist']):
            technique_data['category'] = 'Punches'
        elif any(word in name_lower for word in ['block', 'deflect', 'parry']):
            technique_data['category'] = 'Blocks'
        elif any(word in name_lower for word in ['throw', 'takedown', 'sweep']):
            technique_data['category'] = 'Throws'
        elif any(word in name_lower for word in ['choke', 'lock', 'hold', 'submission']):
            technique_data['category'] = 'Grappling'
        elif any(word in name_lower for word in ['strike', 'chop', 'elbow', 'hammer']):
            technique_data['category'] = 'Strikes'
        elif any(word in name_lower for word in ['stance', 'position', 'guard']):
            technique_data['category'] = 'Stances'
    
    def _extract_difficulty_info(self, technique_data, soup):
        """Extract difficulty and belt level information"""
        content_text = soup.get_text().lower()
        
        # Extract difficulty level
        if any(word in content_text for word in ['advanced', 'expert', 'master', 'black belt']):
            technique_data['difficulty_level'] = 8
        elif any(word in content_text for word in ['intermediate', 'moderate']):
            technique_data['difficulty_level'] = 5
        elif any(word in content_text for word in ['beginner', 'basic', 'fundamental', 'simple']):
            technique_data['difficulty_level'] = 3
        elif len(technique_data.get('instructions', '')) > 800:
            technique_data['difficulty_level'] = 7
        elif len(technique_data.get('instructions', '')) > 400:
            technique_data['difficulty_level'] = 5
        else:
            technique_data['difficulty_level'] = 4
        
        # Extract belt level
        belt_patterns = [
            r'(white|yellow|orange|green|blue|purple|brown|black)\s+belt',
            r'(kyu|dan)\s+\d+',
            r'\d+\s+(kyu|dan)',
            r'(beginner|intermediate|advanced)\s+level'
        ]
        
        for pattern in belt_patterns:
            match = re.search(pattern, content_text)
            if match:
                technique_data['belt_level'] = match.group(0).strip().title()
                break
    
    def _generate_tags(self, technique_data):
        """Generate relevant tags for the technique"""
        tags = []
        
        # Add category as tag
        if technique_data['category']:
            tags.append(technique_data['category'].lower())
        
        # Add style as tag
        if technique_data['style'] and technique_data['style'] != 'General':
            tags.append(technique_data['style'].lower().replace(' ', '-'))
        
        # Add descriptive tags based on name
        name_lower = technique_data['name'].lower()
        
        if 'front' in name_lower:
            tags.append('linear')
        if any(word in name_lower for word in ['round', 'hook', 'circular']):
            tags.append('circular')
        if 'spinning' in name_lower:
            tags.append('spinning')
        if 'jumping' in name_lower:
            tags.append('jumping')
        if 'reverse' in name_lower or 'back' in name_lower:
            tags.append('reverse')
        if any(word in name_lower for word in ['power', 'strong', 'heavy']):
            tags.append('power')
        if any(word in name_lower for word in ['quick', 'fast', 'snap']):
            tags.append('speed')
        
        # Add difficulty tags
        difficulty = technique_data.get('difficulty_level')
        if difficulty:
            if difficulty <= 3:
                tags.append('basic')
            elif difficulty <= 6:
                tags.append('intermediate')
            else:
                tags.append('advanced')
        
        return tags[:8]  # Limit to 8 tags
    
    def scrape_techniques(self, max_techniques=30):
        """Enhanced technique scraping with better error handling"""
        print("🥋 Starting enhanced BlackBeltWiki technique scraping...")
        
        # Discover URLs
        technique_urls = self.discover_technique_urls(max_pages=max_techniques * 2)
        
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
            if cached_data and self._is_cache_valid(cached_data):
                print("📁 Using cached data")
                scraped_techniques.append(cached_data)
                continue
            
            # Scrape the page
            response = self._make_request(url)
            if not response:
                continue
            
            technique_data = self._parse_technique_page(response.text, url)
            
            if technique_data['name'] and len(technique_data['name']) > 2:
                scraped_techniques.append(technique_data)
                self._save_to_cache(url, technique_data)
                print(f"✅ Scraped: {technique_data['name']} ({technique_data['style']})")
                
                # Show brief preview
                if technique_data['description']:
                    preview = technique_data['description'][:100] + "..." if len(technique_data['description']) > 100 else technique_data['description']
                    print(f"   Preview: {preview}")
            else:
                print("⚠️ No valid technique data found, skipping")
        
        print(f"\n🎉 Scraping complete! Successfully scraped {len(scraped_techniques)} techniques")
        return scraped_techniques
    
    def _is_cache_valid(self, cached_data, max_age_days=7):
        """Check if cached data is still valid"""
        if 'cached_at' not in cached_data:
            return False
        
        try:
            cached_time = datetime.fromisoformat(cached_data['cached_at'])
            age = datetime.utcnow() - cached_time
            return age.days < max_age_days
        except:
            return False
    
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
        filename = f"{parsed.netloc}{parsed.path}".replace('/', '_').replace('\\', '_')
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)[:100]
        return f"{filename}.json"

# Test function
def test_enhanced_scraper():
    """Test the enhanced scraper"""
    print("🧪 Testing Enhanced BlackBeltWiki Scraper")
    print("=" * 50)
    
    scraper = BlackBeltWikiScraper(delay=1)
    techniques = scraper.scrape_techniques(max_techniques=5)
    
    print(f"\n📊 Test Results: Found {len(techniques)} techniques")
    
    for i, technique in enumerate(techniques, 1):
        print(f"\n{i}. {technique['name']}")
        print(f"   Style: {technique['style']}")
        print(f"   Category: {technique['category']}")
        print(f"   Difficulty: {technique['difficulty_level']}")
        print(f"   Tags: {', '.join(technique['tags'])}")
        if technique['description']:
            preview = technique['description'][:150] + "..." if len(technique['description']) > 150 else technique['description']
            print(f"   Description: {preview}")

if __name__ == "__main__":
    test_enhanced_scraper()