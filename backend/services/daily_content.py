"""Daily Matcha content generator — auto-creates platform-optimized posts about matcha."""

import logging
from datetime import datetime, timezone

from config import settings

logger = logging.getLogger(__name__)

# 365-day topic rotation — matcha education, culture, recipes, health, terroir
TOPIC_CATEGORIES = [
    # Terroir & Origins (30 topics)
    "Why shade-growing matters: 21 days that transform a tea leaf",
    "Kagoshima vs Uji: two terroirs, two personalities",
    "What volcanic soil does for matcha flavor",
    "Single-origin matcha: why it matters",
    "The journey from Nishi Tea Factory to your cup",
    "Spring first flush (ichibancha): the most prized harvest",
    "How altitude affects matcha sweetness",
    "Organic farming in Kagoshima: JAS + USDA certified",
    "Why Japan's climate creates the world's best matcha",
    "The difference between tencha and matcha",
    "How matcha cultivars (Okumidori, Saemidori, Yabukita) affect taste",
    "What 'ceremonial grade' really means — and what it doesn't",
    "How stone-grinding (ishiusu) preserves nutrients",
    "Temperature control: why matcha is ground at 40g per hour",
    "The art of blending: how tea masters create consistent flavor",
    "From seed to cup: the 2-year journey of a matcha plant",
    "Why only 5% of Japanese green tea becomes matcha",
    "Shading techniques: traditional vs modern approaches",
    "The role of umami in premium matcha",
    "How harvest timing changes everything about matcha quality",
    "Why second flush matcha (nibancha) is different",
    "The geography of Japan's matcha-growing regions",
    "How soil pH affects matcha's amino acid content",
    "What makes Kagoshima's climate uniquely suited for matcha",
    "The history of matcha cultivation in southern Japan",
    "Organic pest management in tea farming",
    "How rainfall patterns shape each year's matcha harvest",
    "The importance of steaming (sassei) right after harvest",
    "Why freshly ground matcha tastes different from pre-ground",
    "Farm-to-cup traceability: knowing exactly where your matcha comes from",

    # Health & Wellness (30 topics)
    "L-theanine: calm focus without the crash — the science explained",
    "Matcha vs coffee: caffeine that works differently",
    "EGCG: the antioxidant that makes matcha a superfood",
    "Why matcha gives you 4-6 hours of sustained energy",
    "The catechin profile of matcha: what the research says",
    "Matcha for athletes: pre-workout benefits backed by science",
    "How matcha supports metabolism — what studies actually show",
    "The gut health benefits of matcha's polyphenols",
    "Matcha and cortisol: how L-theanine modulates stress",
    "Why matcha drinkers report better sleep despite the caffeine",
    "The skin benefits of matcha: antioxidants from the inside out",
    "Matcha's chlorophyll content: detox support explained",
    "How matcha affects blood sugar levels",
    "The cognitive benefits of regular matcha consumption",
    "Matcha vs green tea extract supplements: whole food wins",
    "Why ceremonial grade has more L-theanine than culinary grade",
    "Matcha for meditation: why monks chose this tea",
    "The amino acid profile of shade-grown matcha",
    "How matcha fits into an anti-inflammatory diet",
    "Matcha and longevity: lessons from Okinawa and Japanese tea culture",
    "Caffeine content in matcha: what you actually get per serving",
    "How matcha supports immune function",
    "The role of theanine in alpha brain wave production",
    "Matcha hydration: does it count toward daily water intake?",
    "Morning matcha ritual: setting the tone for your day",
    "Matcha and intermittent fasting: what you need to know",
    "Post-workout matcha: recovery benefits",
    "Why matcha is the original functional food",
    "Adaptogenic properties of matcha compounds",
    "How to get the most health benefits from your matcha",

    # Preparation & Technique (30 topics)
    "How to make the perfect usucha (thin tea) at home",
    "Koicha (thick tea): the most intense matcha experience",
    "Water temperature matters: why 80C/175F is the sweet spot",
    "Chasen (bamboo whisk) technique: the W-motion explained",
    "Why sifting your matcha prevents clumps",
    "The 3 tools you need: chawan, chasen, chashaku",
    "Cold-brew matcha: the easiest summer preparation",
    "How to make matcha without a whisk (blender, shaker, frother)",
    "The perfect matcha-to-water ratio for every taste preference",
    "How to tell if your matcha is fresh: color, aroma, taste",
    "Storing matcha properly: light, air, and temperature",
    "Why the first sip tastes different from the last",
    "Double-sifting technique for the smoothest matcha",
    "How long to whisk: the 15-second sweet spot",
    "Matcha with sparkling water: the unexpected refreshment",
    "Why pre-warming your bowl matters",
    "The art of the crema: achieving perfect foam",
    "Matcha on the go: travel preparation tips",
    "Common mistakes that ruin good matcha",
    "How to develop your matcha palate",
    "Tasting notes: what to look for in premium matcha",
    "The difference between whisking and stirring",
    "Making matcha concentrate for drinks all day",
    "How to clean and care for your bamboo whisk",
    "The ideal chasen: 80-prong vs 100-prong",
    "Matcha preparation in under 60 seconds",
    "Temperature experiments: how heat changes flavor",
    "Why filtered water makes a difference",
    "Seasonal preparation adjustments: summer vs winter",
    "From bitter to blissful: troubleshooting your matcha",

    # Recipes & Culinary (30 topics)
    "The perfect matcha latte: recipe and technique",
    "Matcha overnight oats: prep tonight, enjoy tomorrow",
    "Iced matcha latte: barista-quality at home",
    "Matcha smoothie bowl with seasonal fruit",
    "Matcha affogato: where tea meets ice cream",
    "Matcha banana bread: a weekend baking project",
    "How to make matcha mochi at home",
    "Matcha energy balls: 5 ingredients, no baking",
    "The ultimate matcha pancake recipe",
    "Matcha tiramisu: Japanese-Italian fusion",
    "Matcha chia pudding for meal prep",
    "Matcha honey toast: a 5-minute treat",
    "Savory matcha: pasta, risotto, and beyond",
    "Matcha white chocolate truffles",
    "The best milk alternatives for matcha lattes",
    "Oat milk matcha: why it's become the default",
    "Matcha coconut ice cream: dairy-free indulgence",
    "Matcha granola: homemade superfood breakfast",
    "How cafes create Instagram-worthy matcha drinks",
    "Matcha cocktails: gin, vodka, and whiskey pairings",
    "Matcha mocktails for every season",
    "Matcha margarita: the unexpected crowd-pleaser",
    "Baking with matcha: culinary vs ceremonial grade",
    "Matcha whipped cream: elevate any dessert",
    "Matcha dalgona: the viral drink made better",
    "Matcha popsicles for summer",
    "Holiday matcha drinks: seasonal inspiration",
    "Matcha and chocolate: the perfect pairing explained",
    "How to balance sweetness in matcha drinks",
    "Restaurant-quality matcha desserts at home",

    # Tea Ceremony & Culture (30 topics)
    "Wabi-sabi and matcha: finding beauty in imperfection",
    "The history of matcha: from China to Japan",
    "Sen no Rikyu: the tea master who shaped matcha culture",
    "Ichigo ichie: every tea moment is unique",
    "The four principles of tea: wa, kei, sei, jaku",
    "Why tea ceremony movements are meditative",
    "Matcha in Zen Buddhism: 800 years of mindful practice",
    "The seasonal awareness (kisetsukan) in tea ceremony",
    "How matcha became Japan's national drink",
    "The role of silence in tea practice",
    "Chanoyu explained: the way of tea for beginners",
    "Tea room architecture: design for mindfulness",
    "The evolution of matcha from medicine to daily ritual",
    "Matcha etiquette: how to receive tea gracefully",
    "The relationship between pottery and matcha culture",
    "Matcha's journey to the Western world",
    "Modern matcha culture in Tokyo, Kyoto, and beyond",
    "How tea ceremony principles apply to daily life",
    "The philosophy of 'less is more' in matcha tradition",
    "Matcha and seasonal wagashi (Japanese sweets)",
    "The global matcha movement: appreciation beyond Japan",
    "Why matcha is experiencing a worldwide renaissance",
    "Tea gardens (roji) and their symbolic meaning",
    "The connection between calligraphy and tea",
    "Matcha in Japanese literature and art",
    "How matcha ceremony differs across Japanese schools",
    "The democratization of matcha: from elite to everyday",
    "Mindful drinking: turning matcha into meditation",
    "The tactile experience: why the bowl matters",
    "Teaching the next generation about tea culture",

    # For Baristas & Professionals (30 topics)
    "Matcha menu engineering: what sells and why",
    "Latte art with matcha: techniques for green canvas",
    "Training staff on matcha preparation: a barista guide",
    "Wholesale matcha: what to look for as a buyer",
    "Matcha quality tiers: understanding grades for your menu",
    "Cost per cup analysis: matcha economics for cafes",
    "How to store matcha in a commercial kitchen",
    "Matcha drink development: seasonal menu ideas",
    "The rise of matcha bars: a business opportunity",
    "Customer education: helping guests appreciate quality matcha",
    "Matcha vs. green tea powder: educating your team",
    "Sourcing transparency: why your customers care about origins",
    "Matcha pairing menus for restaurants",
    "How fine dining is incorporating matcha",
    "Matcha in hotel F&B: spa, restaurant, and minibar",
    "Building a matcha-focused brand identity",
    "Matcha subscription models for cafes and retailers",
    "Photography tips: making matcha look irresistible",
    "Matcha trend forecasting: what's next",
    "Sustainability in matcha sourcing",
    "Why direct-from-farm matcha is worth the premium",
    "Matcha flights: offering a tasting experience",
    "Cross-selling with matcha: accessories and tools",
    "Matcha events and workshops: building community",
    "How to evaluate matcha samples from suppliers",
    "Scaling matcha preparation: from 1 cup to 100",
    "The business case for premium matcha vs. commodity",
    "Creating a matcha-centered cafe concept",
    "Matcha certifications that matter to consumers",
    "Packaging and presentation: first impressions count",

    # Matcha Science & Innovation (25 topics)
    "How electron microscopy reveals matcha particle size",
    "The Maillard reaction and matcha: what happens when you heat it",
    "Chlorophyll stability: why matcha turns brown and how to prevent it",
    "Catechin chemistry: EGCG, EGC, ECG explained",
    "Amino acid analysis: what lab tests reveal about quality",
    "The physics of whisking: creating stable microfoam",
    "Why matcha's color correlates with L-theanine content",
    "Spectrophotometry and matcha quality assessment",
    "How nitrogen fertilization increases umami",
    "The role of tannins in matcha's astringency",
    "Cold extraction vs hot: different compound profiles",
    "Matcha's bioavailability advantage over other green teas",
    "How UV light triggers shade-response in tea plants",
    "The microbiology of matcha: what's in your cup",
    "Particle size distribution and mouthfeel",
    "How oxidation levels classify different teas",
    "The future of matcha: sustainable farming innovations",
    "Lab-tested matcha: what we test and why",
    "How humidity affects matcha during storage",
    "The role of iron in matcha's nutritional profile",
    "Comparing antioxidant capacity: ORAC values of different teas",
    "Caffeine metabolism: why matcha feels different from coffee",
    "How processing methods affect matcha's nutritional density",
    "The neuroscience of L-theanine and alpha waves",
    "Matcha quality grading: objective metrics vs subjective taste",

    # Lifestyle & Modern Matcha (25 topics)
    "Morning matcha routine: replacing coffee mindfully",
    "Matcha desk setup: making great tea at work",
    "Travel matcha kit: essentials for matcha lovers on the go",
    "Matcha and yoga: the natural pairing",
    "Creating a home tea corner: minimal setup guide",
    "Matcha journaling: tracking your taste journey",
    "The minimalist matcha practice: chawan and chasen only",
    "Matcha gift guide: what to buy for tea lovers",
    "Starting a matcha collection: first purchases",
    "Matcha date night: sharing the experience",
    "Matcha for creative work: focus without jitters",
    "The 5-minute matcha break: micro-meditation at work",
    "Matcha and reading: the perfect slow afternoon",
    "Seasonal matcha enjoyment: adapting to the weather",
    "Matcha photography: capturing the green gold",
    "Building a matcha community: online and local",
    "Matcha subscription boxes: what to expect",
    "The matcha starter kit: everything a beginner needs",
    "Matcha social media: accounts worth following",
    "Hosting a matcha tasting party",
    "Matcha and music: curated playlists for tea time",
    "Digital detox with matcha: screen-free ritual",
    "Matcha in different cultures: how the world drinks it",
    "The economics of daily matcha vs daily coffee",
    "Why matcha people are matcha people for life",

    # Seasonal & Trending (25 topics)
    "New Year's matcha: starting fresh with tea",
    "Valentine's Day matcha treats for your loved one",
    "Spring matcha: celebrating the first harvest",
    "Cherry blossom season and matcha: the ultimate pairing",
    "Mother's Day matcha gift ideas",
    "Summer iced matcha: beating the heat Japanese-style",
    "Father's Day: introducing dad to quality matcha",
    "Back to school: matcha for students and focus",
    "Fall matcha: warm drinks for cooler days",
    "Matcha pumpkin latte: the seasonal favorite",
    "Halloween matcha: spooky green treats",
    "Thanksgiving matcha desserts",
    "Holiday matcha gifts: premium choices for tea lovers",
    "Winter matcha: koicha for cold nights",
    "Chinese New Year and tea traditions",
    "Matcha resolutions: healthier habits with tea",
    "World Health Day: celebrating matcha's benefits",
    "Earth Day: sustainable matcha farming practices",
    "International Tea Day: honoring matcha's heritage",
    "Summer solstice: the longest day deserves great matcha",
    "Matcha in autumn: harvest season reflections",
    "Black Friday: why quality matcha is worth the investment",
    "Winter solstice: the most intimate tea ceremony",
    "Year-end reflections: a year of matcha moments",
    "New harvest announcement: this year's first flush is here",

    # NAKAI Brand Stories (20 topics)
    "Meet NAKAI: our mission to share authentic Kagoshima matcha",
    "The Nishi Tea Factory: three generations of tea craftsmanship",
    "Why we chose single-origin over blended matcha",
    "Our organic certification journey: JAS and USDA",
    "Behind the scenes: a day at the tea factory",
    "How we select our cultivars each season",
    "The NAKAI taste profile: what makes our matcha distinctive",
    "Customer spotlight: how baristas use NAKAI matcha",
    "From Kagoshima to your kitchen: our supply chain",
    "Quality control at NAKAI: every batch tested",
    "Our packaging story: protecting freshness and the planet",
    "Why we do direct trade: cutting out the middlemen",
    "NAKAI community: stories from matcha lovers worldwide",
    "Our commitment to transparency in sourcing",
    "The NAKAI matcha grading system explained",
    "Seasonal releases: why each batch is unique",
    "How NAKAI supports local tea farming communities",
    "Our founder's story: why matcha became a mission",
    "NAKAI for professionals: our wholesale program",
    "The future of NAKAI: what's coming next",
]

SYSTEM_PROMPT = """You are NAKAI Matcha's content voice — an expert, warm, and educational guide
to the world of premium Japanese matcha. You combine deep tea knowledge with
accessible, engaging storytelling.

Rules:
- Write in English for a global audience (US/EU/Asia)
- Be genuinely educational — share real knowledge, not marketing fluff
- Include specific details (temperatures, times, measurements) when relevant
- Mention NAKAI products naturally when they fit the topic — never force it
- Use a confident but warm tone — you're a knowledgeable friend, not a salesperson
- Include 1-2 relevant emojis maximum
- Never make unsubstantiated health claims — cite "research suggests" not "matcha cures"
- End with something actionable the reader can try today
- Weave in Japanese terms naturally with brief explanations
- Reference the Nishi Tea Factory, Kagoshima, or NAKAI heritage when relevant"""

PLATFORM_PROMPTS = {
    "twitter": """Create a Twitter/X post about this matcha topic.
- Maximum 280 characters
- Include 3 hashtags: #matcha + 2 relevant ones (e.g., #greentea #ceremonialmatcha #matchalatte #japanesetea #NAKAImatcha)
- Start with a hook that makes people stop scrolling
- One clear insight or tip
- Output only the post text (no explanation)""",

    "threads": """Create a Threads post about this matcha topic.
- 300-500 characters
- More conversational and detailed than Twitter
- Include a specific tip, fact, or mini-story
- Use natural paragraph breaks for readability
- End with a question or call to try something
- Output only the post text (no explanation)""",

    "line": """Create a LINE message about this matcha topic.
- 400-600 characters
- Start with a warm greeting
- Include one actionable tip or recipe snippet
- Reference NAKAI products if naturally relevant
- Warm, personal tone — like a message from a matcha-loving friend
- End with a simple action they can take today
- Output only the message text (no explanation)""",

    "reddit": """Create a Reddit post about this matcha topic.
- Title: engaging, specific, 60-100 characters (output on first line)
- Body: 800-1500 characters, educational and detailed
- Write like a knowledgeable community member, NOT a brand
- Include specific details, measurements, or science
- DO NOT be promotional — focus purely on education and value
- If mentioning a product, do so naturally as "I use X" not "Buy X"
- Reddit rewards depth and authenticity
- Output format:
  TITLE: [title here]
  BODY: [body here]""",

    "blog": """Create a blog article about this matcha topic.
- Title: SEO-friendly, 50-70 characters (output on first line)
- Body: 800-1200 words in clean HTML
- Include an engaging introduction paragraph
- Use <h2> subheadings to break up sections (3-4 sections)
- Include specific details, measurements, temperatures, times
- Naturally mention NAKAI matcha and link to nakaimatcha.com where relevant
- End with a takeaway or call to action
- Optimize for search: include the topic keywords naturally throughout
- Output format:
  TITLE: [title here]
  TAGS: [comma-separated tags]
  BODY: [HTML body here]""",

    "reddit_community": """Create a Reddit community engagement post about this matcha topic.
- Title: a question or discussion prompt, 60-100 characters (output on first line)
- Body: 400-800 characters, casual and conversational
- Ask for community opinions, experiences, or tips
- Frame as a genuine community member starting a discussion
- DO NOT be promotional at all
- Output format:
  TITLE: [title here]
  BODY: [body here]""",
}


def _get_today_topic() -> str:
    """Get today's topic based on day-of-year rotation."""
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    idx = day_of_year % len(TOPIC_CATEGORIES)
    return TOPIC_CATEGORIES[idx]


def _get_slot_topic(slot: int) -> str:
    """Get a unique topic for the given slot (1-6) on today's date."""
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    idx = (day_of_year * 6 + slot) % len(TOPIC_CATEGORIES)
    return TOPIC_CATEGORIES[idx]


async def _build_context_block() -> str:
    """Build context from content_sources + today's research brief."""
    parts = []

    # Content sources from Supabase
    try:
        from services import supabase_client
        sources = await supabase_client.list_content_sources(active_only=True)
        if sources:
            parts.append("=== BRAND CONTEXT (use these themes/messages when relevant) ===")
            for s in sources[:10]:
                parts.append(f"[{s['type']}] {s['title']}: {s['content'][:300]}")
    except Exception:
        pass

    # Latest research brief
    try:
        from services import supabase_client
        # Use internal client to fetch latest research brief
        if supabase_client._is_configured():
            supabase_client._init()
            client = supabase_client._get_client()
            resp = await client.get(
                f"{supabase_client._BASE_URL}/matcha_research_briefs",
                headers=supabase_client._HEADERS,
                params={"order": "date.desc", "limit": "1"},
            )
            if resp.status_code == 200:
                briefs = resp.json()
                if briefs and briefs[0].get("insights"):
                    parts.append(f"\n=== TODAY'S MATCHA TRENDS ===\n{briefs[0]['insights']}")
    except Exception:
        pass

    return "\n".join(parts)


async def generate_daily_content(
    platforms: list[str] | None = None,
    slot: int = 0,
) -> dict[str, str]:
    """Generate daily matcha content for specified platforms.

    Args:
        platforms: List of platforms to generate for.
                   Defaults to ['twitter', 'threads', 'line'].
        slot: Content slot number (1-6) for unique topic per slot.
              0 = use default today's topic.

    Returns:
        Dict with keys for each platform + 'topic'
    """
    if platforms is None:
        platforms = ["twitter", "threads", "line"]

    topic = _get_slot_topic(slot) if slot else _get_today_topic()
    logger.info(f"[DAILY_CONTENT] Generating matcha content (slot={slot}) for topic: {topic}")

    if not settings.anthropic_api_key:
        logger.warning("[DAILY_CONTENT] Anthropic API key not set, using fallback")
        return _fallback_content(topic)

    # Build context from content sources and research
    context_block = await _build_context_block()

    results = {"topic": topic}

    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

        for platform in platforms:
            # Map reddit_community to reddit for posting
            platform_prompt = PLATFORM_PROMPTS.get(platform)
            if not platform_prompt:
                logger.warning(f"[DAILY_CONTENT] Unknown platform: {platform}")
                continue

            user_content = f"Today's topic: \"{topic}\"\n\n{platform_prompt}"
            if context_block:
                user_content = f"{context_block}\n\n{user_content}"

            response = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": user_content,
                }],
                temperature=0.8,
            )
            results[platform] = response.content[0].text.strip()
            logger.info(f"[DAILY_CONTENT] Generated {platform} content ({len(results[platform])} chars)")

    except Exception as e:
        logger.error(f"[DAILY_CONTENT] Content generation failed: {e}")
        return _fallback_content(topic)

    return results


# Keep backward compatibility
async def generate_daily_tips() -> dict[str, str]:
    """Backward-compatible wrapper — generates content for social platforms."""
    return await generate_daily_content(["twitter", "threads", "line"])


def _fallback_content(topic: str) -> dict[str, str]:
    """Fallback content when Claude API is unavailable."""
    return {
        "topic": topic,
        "twitter": f"Today's matcha insight: {topic}. Premium matcha isn't just a drink — it's centuries of Japanese craftsmanship in every sip. #matcha #japanesetea #NAKAImatcha",
        "threads": f"Let's talk about: {topic}\n\nThis is one of those details that separates truly great matcha from ordinary green tea powder. The difference is in the details — the shading, the stone-grinding, the single-origin sourcing.\n\nWhat's your experience with this? Drop a comment below.",
        "line": f"Good morning! Today let's explore: {topic}\n\nThis is something that makes premium matcha so special. At NAKAI, we obsess over these details because they're what give our Kagoshima matcha its distinctive character.\n\nTry this today: make your next matcha with extra attention to water temperature (80C/175F) and notice how it changes the flavor.",
    }
