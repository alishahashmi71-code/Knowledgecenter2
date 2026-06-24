#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the seven Knowledge & Solutions Center module files from the
content in the assigned spreadsheet. Run:  python3 build_modules.py
Outputs module-01..07 HTML files (pure markup, no <style>/<script>).

Article preview images are optional: if a file named 'article-images.csv'
exists next to this script with columns including 'Article URL' and
'Image URL', any row with both filled will render that image in the card.
Articles without an image keep the grey placeholder.
"""
import html, os, csv, re

OUT = os.path.dirname(os.path.abspath(__file__))

def _nurl(u):
    """Normalize a URL for matching: drop query string and trailing slash."""
    if not u:
        return ''
    return str(u).split('?')[0].strip().rstrip('/').lower()

def load_images():
    """normalized url -> hosted image url, from article-images.csv if present."""
    path = os.path.join(OUT, 'article-images.csv')
    images = {}
    if os.path.exists(path):
        with open(path, newline='', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                u = (row.get('Article URL') or '').strip()
                img = (row.get('Image URL') or '').strip()
                if u and img:
                    images[_nurl(u)] = img
    return images

IMAGES = load_images()

# ----- shared SVG snippets ------------------------------------------------
ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" '
         'aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')
CHEVRON = ('<svg class="aih-chevron" viewBox="0 0 24 24" fill="none" '
           'stroke="currentColor" stroke-width="2.5" stroke-linecap="round" '
           'stroke-linejoin="round" aria-hidden="true" width="16" height="16">'
           '<path d="M6 9l6 6 6-6"/></svg>')
PLAY = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
        '<path d="M8 5v14l11-7z"/></svg>')

# ----- industry slug/label map -------------------------------------------
IND = {
    'aggregate': 'Aggregate', 'automotive': 'Automotive',
    'chemicals-petrochemicals': 'Chemicals & Petrochemicals',
    'food-beverage': 'Food & Beverage', 'lubrication': 'Lubrication',
    'metals': 'Metals', 'oil-gas': 'Oil & Gas', 'government': 'Government',
    'forestry': 'Forestry',
}
# order shown in the Industry filter
IND_ORDER = ['aggregate', 'automotive', 'chemicals-petrochemicals',
             'food-beverage', 'lubrication', 'metals', 'oil-gas',
             'government', 'forestry']

def isl(*slugs):
    return list(slugs)

# ----- suppliers (slug, label, homepage) ---------------------------------
SUPPLIERS = [
    ('abb', 'ABB', 'https://global.abb/'),
    ('climax', 'Climax Metal Products', 'https://climaxmetal.com/'),
    ('continental', 'Continental', 'https://www.continental.com/'),
    ('danfoss', 'Danfoss', 'https://www.danfoss.com/'),
    ('dixon', 'Dixon', 'https://dixonvalve.com/'),
    ('dodge', 'Dodge Industrial', 'https://dodgeindustrial.com/'),
    ('donaldson', 'Donaldson', 'https://www.donaldson.com/'),
    ('enerpac', 'Enerpac', 'https://www.enerpac.com/'),
    ('garlock', 'Garlock Safety', 'https://garlocksafety.com/'),
    ('graco', 'Graco', 'https://www.graco.com/'),
    ('loctite', 'Loctite', 'https://www.loctiteproducts.com/'),
    ('pip', 'PIP', 'https://us.pipglobal.com/'),
    ('milwaukee', 'Milwaukee Tool', 'https://www.milwaukeetool.com/'),
    ('regal-rexnord', 'Regal Rexnord', 'https://www.regalrexnord.com/'),
    ('renold', 'Renold', 'https://www.renold.com/'),
    ('schaeffler', 'Schaeffler', 'https://www.schaeffler.com/'),
    ('trico', 'Trico', 'https://www.tricocorp.com/'),
]
SUP_LABEL = {s[0]: s[1] for s in SUPPLIERS}

# =========================================================================
# CONTENT DATA  (supplier_slug, title, [industry slugs], url, kind)
# kind: 'case-study' or 'article'
# =========================================================================
SUCCESS = [
    ('abb', "Powering and protecting systems in the world's tallest building",
     isl('government'), 'https://www.abb.com/global/en/company/stories/protecting-burj-khalifa'),
    ('abb', "World's largest offshore wind farm powers 6m UK homes",
     isl('oil-gas'), 'https://www.abb.com/global/en/company/stories/uk-offshore-wind-farm'),
    ('continental', "Revolutionizing the port industry",
     isl('government'), 'https://www.continental.com/en/stories/smart-ports/'),
    ('continental', "Steering electric buses safely into the future",
     isl('automotive'), 'https://www.continental.com/en/stories/technologies-for-electric-buses/'),
    ('danfoss', "Danfoss iC7 series powers new electric ferry Nerthus",
     isl('government'), 'https://www.danfoss.com/en/about-danfoss/news/cf/danfoss-ic7-series-powers-new-electric-ferry-nerthus/'),
    ('dodge', "Bin it to win it",
     isl('food-beverage'), 'https://dodgeindustrial.com/bin-it-to-win-it/'),
    ('dodge', "No more wasted time or savings",
     isl('aggregate'), 'https://dodgeindustrial.com/no-more-wasted-time-or-savings/'),
    ('dodge', "Elevating efficiency and cost savings",
     isl('aggregate'), 'https://dodgeindustrial.com/elevating-efficiency-and-cost-savings/'),
    ('dodge', "Don't trash talk cost savings",
     isl('food-beverage'), 'https://dodgeindustrial.com/dont-trash-talk-cost-savings/'),
    ('garlock', "Case study: manufacturer of metal tubing",
     isl('metals'), 'https://garlocksafety.com/case-study-manufacturer-of-metal-tubing/'),
    ('garlock', "Case study: MeasureSafe technology identifies fall hazards",
     isl('government'), 'https://garlocksafety.com/case-study-use-of-measuresafe-technology-to-identify-fall-hazards/'),
]

FEATURED = [
    ('abb', "Industrial energy efficiency: from ambition to scalable execution",
     isl('chemicals-petrochemicals'), 'https://www.abb.com/global/en/company/stories/energy-efficiency'),
    ('abb', "The role of AI in predictive maintenance",
     isl('metals'), 'https://www.abb.com/global/en/company/stories/ai-predictive-maintenance'),
    ('abb', "Nuclear ship propulsion: powering low-emission maritime transport",
     isl('government'), 'https://www.abb.com/global/en/company/stories/nuclear-ship-propulsion'),
    ('abb', "The role of AI in energy optimization",
     isl('oil-gas'), 'https://www.abb.com/global/en/company/stories/ai-energy-optimization'),
    ('abb', "Energy resilience: the foundation of a reliable energy system",
     isl('government'), 'https://www.abb.com/global/en/company/stories/energy-resilience'),
    ('abb', "Generations in the workplace",
     isl('government'), 'https://www.abb.com/global/en/company/stories/generations-in-the-workplace'),
    ('abb', "Smart stadiums: running the future of sports venues",
     isl('government'), 'https://www.abb.com/global/en/company/stories/smart-stadium-automation'),
    ('climax', "New product: shaft mount stackable shaft collars (2SMC series)",
     isl('metals'), 'https://climaxmetal.com/blog/shaft-mount-stackable-collars/'),
    ('climax', "Celebrating 80 years of American manufacturing excellence",
     isl('automotive'), 'https://climaxmetal.com/blog/american-manufacturing-excellence/'),
    ('continental', "What drives people when mobility changes?",
     isl('automotive'), 'https://www.continental.com/en/stories/when-mobility-changes/'),
    ('continental', "120 years of tread: from the idea to the ideal",
     isl('automotive'), 'https://www.continental-tires.com/about-us/stories/120-years-tread-pattern/'),
    ('continental', "Sustainable. Lightweight. Efficient.",
     isl('automotive'), 'https://www.continental.com/en/stories/green-concept/'),
    ('danfoss', "Supporting France's ambition to ramp up heat pump production",
     isl('government'), 'https://www.danfoss.com/en/about-danfoss/news/cf/danfoss-supports-france-s-ambition-to-ramp-up-heat-pump-production-and-installation/'),
    ('danfoss', "Denmark launches energy-efficient AI supercomputer",
     isl('government'), 'https://www.danfoss.com/en/about-danfoss/news/cf/denmark-launches-energy-efficient-ai-supercomputer/'),
    ('danfoss', "Climate ambitions reaffirmed with updated SBTi-approved targets",
     isl('government'), 'https://www.danfoss.com/en/about-danfoss/news/cf/danfoss-reaffirms-climate-ambitions-with-updated-targets-approved-by-science-based-targets-initiative-sbti/'),
    ('danfoss', "Danfoss earns CDP leadership recognition",
     isl('government'), 'https://www.danfoss.com/en/about-danfoss/news/cf/danfoss-earns-cdp-leadership-recognition/'),
    ('danfoss', "Green technology demand drives largest production facility in China",
     isl('automotive'), 'https://www.danfoss.com/en/about-danfoss/news/cf/rising-demand-for-green-technologies-drives-danfoss-to-open-its-largest-production-facility-in-china/'),
    ('danfoss', "Danfoss builds the world's most livable lab",
     isl('government'), 'https://www.danfoss.com/en/about-danfoss/news/cf/danfoss-builds-the-world-s-most-livable-lab/'),
    ('danfoss', "Texas sun powers all Danfoss US sites",
     isl('government'), 'https://www.danfoss.com/en/about-danfoss/news/cf/texas-sun-powers-all-danfoss-us-sites/'),
    ('danfoss', "Danfoss and Microsoft: an AI-powered sustainability alliance",
     isl('government'), 'https://www.danfoss.com/en/about-danfoss/news/cf/danfoss-and-microsoft-an-ai-powered-alliance-to-drive-sustainability-ambitions/'),
    ('danfoss', "Solid performance in a volatile market",
     isl('government'), 'https://www.danfoss.com/en/about-danfoss/news/cf/danfoss-delivered-solid-performance-in-a-volatile-market/'),
    ('danfoss', "Growth opportunities in competitive decarbonization",
     isl('government'), 'https://www.danfoss.com/en/about-danfoss/news/cf/danfoss-demonstrates-the-growth-opportunities-in-competitive-decarbonization/'),
    ('dixon', "A practical guide for maintenance, repair, and operations (MRO)",
     isl('metals'), 'https://blog.dixonvalve.com/a-practical-guide-for-maintenance-repair-and-operations-mro'),
    ('dixon', "How LNG power generation is supporting data center growth",
     isl('oil-gas'), 'https://blog.dixonvalve.com/how-lng-power-generation-is-supporting-data-center-growth'),
    ('dixon', "110 years of uncommon excellence",
     isl('government'), 'https://blog.dixonvalve.com/110-years-of-uncommon-excellence'),
    ('dodge', "Dodge opens Kansas City customer solutions center",
     isl('metals'), 'https://dodgeindustrial.com/dodge-industrial-opens-kansas-city-customer-solutions-center-for-fast-flexible-and-local-products-and-support/'),
    ('dodge', "Dodge launches 300 series mounted ball bearing",
     isl('metals'), 'https://dodgeindustrial.com/dodge-industrial-launches-300-series-mounted-ball-bearing/'),
    ('dodge', "Dodge receives distinguished industry partner of the year award",
     isl('government'), 'https://dodgeindustrial.com/dodge-industrial-receives-distinguished-industry-partner-of-the-year-award/'),
    ('dodge', "Dodge named large manufacturer of the year",
     isl('government'), 'https://dodgeindustrial.com/dodge-industrial-named-large-manufacturer-of-the-year/'),
    ('donaldson', "Donaldson named official partner of the 2026 Special Olympics",
     isl('government'), 'https://www.donaldson.com/en/resources/news/donaldson-official-partner-2026-special-olympics/'),
    ('donaldson', "Donaldson acquires Facet fuel and fluid filtration",
     isl('oil-gas'), 'https://www.donaldson.com/en/resources/news/donaldson-acquires-facet-fuel-fluid-filtration/'),
    ('donaldson', "Donaldson introduces ArmorSeal",
     isl('metals'), 'https://www.donaldson.com/en/resources/news/donaldson-introduces-armorseal/'),
    ('donaldson', "Donaldson rings the NYSE closing bell",
     isl('government'), 'https://www.donaldson.com/en/resources/news/donaldson-rings-nyse-closing-bell/'),
    ('enerpac', "Enerpac completes Hydra-Pac acquisition",
     isl('oil-gas'), 'https://www.enerpac.com/en-us/news/press-release/hydra-pac-acquisition'),
    ('garlock', "Flat roof safety: fall protection in construction vs general industry",
     isl('government'), 'https://garlocksafety.com/flat-roof-safety-challenges-when-is-fall-protection-required-in-construction-vs-general-industry/'),
    ('garlock', "Products designed to protect workers from falls in many settings",
     isl('government'), 'https://garlocksafety.com/garlock-safety-systems-products-designed-to-protect-workers-from-falling-in-a-variety-of-settings/'),
    ('graco', "Graco breaks ground on new headquarters",
     isl('government'), 'https://www.graco.com/us/en/about-graco/news/articles/2026/q2/new-dayton-headquarters-groundbreaking-ceremony.html'),
    ('graco', "Innovations that made Graco: airless spray technology",
     isl('automotive'), 'https://www.graco.com/us/en/about-graco/news/articles/2026/q1/innovations-made-graco-airless-spray-technology.html'),
    ('graco', "Celebrating Graco's 100th anniversary: what else happened in 1926",
     isl('government'), 'https://www.graco.com/us/en/about-graco/news/articles/2026/q1/100-years-graco-what-else-happened-in-1926.html'),
    ('graco', "Graco Foundation marks centennial with $1 million commitment",
     isl('government'), 'https://investors.graco.com/news-releases/news-release-details/graco-foundation-marks-companys-centennial-1-million-commitment'),
    ('graco', "Graco to acquire Valco Melton, a leader in precision adhesives",
     isl('food-beverage'), 'https://investors.graco.com/news-releases/news-release-details/graco-inc-enters-definitive-agreement-acquire-valco-melton'),
    ('graco', "Acquisitions drive sales growth",
     isl('government'), 'https://investors.graco.com/news-releases/news-release-details/acquisitions-drive-sales-growth'),
    ('graco', "Industry's first wirelessly connected, automated fluid management system",
     isl('automotive'), 'https://investors.graco.com/news-releases/news-release-details/graco-introduces-industrys-first-wirelessly-connected-and'),
    ('graco', "Graco finishes year with record quarterly and annual sales",
     isl('government'), 'https://investors.graco.com/news-releases/news-release-details/graco-finishes-year-record-quarterly-and-annual-sales'),
    ('loctite', "Technical bulletin: sealant best practices",
     isl('food-beverage'), 'https://www.loctiteproducts.com/ideas/technical-bulletins/technical-bulletin-sealant-best-practices.html'),
    ('loctite', "Sealants: everything you need to know",
     isl('food-beverage'), 'https://www.loctiteproducts.com/ideas/build-things/sealants.html'),
    ('loctite', "How to caulk: get it right and seal it tight",
     isl('food-beverage'), 'https://www.loctiteproducts.com/ideas/fix-stuff/how-to-caulk-using-sealant-and-getting-it-right.html'),
    ('loctite', "Spray glue: what it is and when to use it",
     isl('food-beverage'), 'https://www.loctiteproducts.com/ideas/fix-stuff/spray-glue.html'),
    ('pip', "Overlooked electrical hazards that escalate fast in construction",
     isl('aggregate', 'government'), 'https://us.pipglobal.com/en/about-us/news-and-events/?nID=333'),
    ('pip', "Noise you can't hear is still damaging",
     isl('aggregate', 'automotive', 'chemicals-petrochemicals', 'food-beverage', 'lubrication', 'government'), 'https://us.pipglobal.com/en/about-us/news-and-events/?nID=339'),
    ('pip', "Why PPE is now mission critical for manufacturing in 2026",
     isl('aggregate', 'government'), 'https://us.pipglobal.com/en/about-us/news-and-events/?nID=337'),
    ('pip', "When heat impacts PPE: what to adjust",
     isl('aggregate', 'automotive', 'chemicals-petrochemicals', 'food-beverage', 'lubrication', 'government'), 'https://us.pipglobal.com/en/about-us/news-and-events/?nID=332'),
    ('pip', "Steel, decking, and the edge: why standard fall protection falls short",
     isl('aggregate', 'government'), 'https://us.pipglobal.com/en/about-us/news-and-events/?nID=331'),
    ('pip', "Dust, debris, and concrete splashes: is your eyewash where the risk is?",
     isl('aggregate', 'chemicals-petrochemicals', 'food-beverage', 'government'), 'https://us.pipglobal.com/en/about-us/news-and-events/?nID=328'),
    ('pip', "Making the cut: where construction work puts hands at risk",
     isl('aggregate', 'government'), 'https://us.pipglobal.com/en/about-us/news-and-events/?nID=326'),
    ('pip', "The what and why of fall protection: from ABCs to SAFE",
     isl('aggregate', 'automotive', 'chemicals-petrochemicals', 'food-beverage', 'government'), 'https://us.pipglobal.com/en/about-us/news-and-events/?nID=321'),
    ('pip', "Workplace eye protection: why performance and comfort both matter",
     isl('aggregate', 'automotive', 'chemicals-petrochemicals', 'food-beverage'), 'https://us.pipglobal.com/en/about-us/news-and-events/?nID=320'),
    ('pip', "How OSHA's \"PPE must fit\" rule impacts women in construction",
     isl('aggregate', 'government'), 'https://us.pipglobal.com/en/about-us/news-and-events/?nID=308'),
    ('milwaukee', "Essential strategies for balancing work and life in construction",
     isl('government'), 'https://onekeyresources.milwaukeetool.com/en/essential-strategies-for-balancing-work-and-life-in-construction'),
    ('milwaukee', "What are building regulations in construction?",
     isl('government'), 'https://onekeyresources.milwaukeetool.com/en/building-construction-regulation'),
    ('milwaukee', "How extreme heat impacts construction workers",
     isl('government'), 'https://onekeyresources.milwaukeetool.com/en/jeff-goodell-on-how-extreme-heat-impacts-construction-workers'),
    ('milwaukee', "Small tool tracking: keeping track of hand tools",
     isl('government'), 'https://onekeyresources.milwaukeetool.com/en/small-tool-tracking'),
    ('milwaukee', "What is lead time and how do you calculate and control it?",
     isl('government'), 'https://onekeyresources.milwaukeetool.com/en/lead-time-supply-chain-inventory'),
    ('milwaukee', "Do roofing and scaffolding specialists need construction software?",
     isl('government'), 'https://onekeyresources.milwaukeetool.com/en/do-roofing-and-scaffolding-specialists-need-construction-software'),
    ('regal-rexnord', "How do I keep my electric motor healthy?",
     isl('metals'), 'https://www.regalrexnord.com/regal-rexnord-insights/how-to-keep-an-electric-motor-healthy'),
    ('regal-rexnord', "What you need to know about oil maintenance for gear drives",
     isl('metals'), 'https://www.regalrexnord.com/regal-rexnord-insights/oil-maintenance-for-gear-drives'),
    ('regal-rexnord', "What causes gearbox failure?",
     isl('metals'), 'https://www.regalrexnord.com/regal-rexnord-insights/what-causes-gearbox-failure'),
    ('regal-rexnord', "Top 2 causes of bearing failure",
     isl('metals'), 'https://www.regalrexnord.com/regal-rexnord-insights/top-2-causes-of-bearing-failure'),
    ('regal-rexnord', "How to select the right bearing for forestry applications",
     isl('forestry'), 'https://www.regalrexnord.com/regal-rexnord-insights/forestry-bearing-selection'),
    ('regal-rexnord', "Balancing sanitation and productivity requirements",
     isl('food-beverage'), 'https://www.regalrexnord.com/regal-rexnord-insights/ip69k-washdown-solutions/balancing-sanitation-and-productivity-requirements'),
    ('regal-rexnord', "How to install a disc coupling",
     isl('metals'), 'https://www.regalrexnord.com/regal-rexnord-insights/how-to-install-a-disc-coupling'),
    ('renold', "The right match: selecting the right chain",
     isl('metals'), 'https://www.renold.com/company/latest-news/the-right-match/'),
    ('renold', "How to tell when worn sprockets have to go",
     isl('metals'), 'https://www.renold.com/company/latest-news/replacing-worn-sprockets/'),
    ('renold', "10 simple steps for optimum gearbox performance",
     isl('metals'), 'https://www.renold.com/company/latest-news/gears/10-simple-steps/'),
    ('renold', "10 simple steps to best practice in gearbox maintenance",
     isl('metals'), 'https://www.renold.com/company/latest-news/gears/reg1130-gears/'),
    ('schaeffler', "How do I do everything right when maintaining rolling bearings?",
     isl('metals'), 'https://medias-at.schaeffler.com/en/service-tips'),
    ('schaeffler', "How do I ensure optimum running behavior?",
     isl('metals'), 'https://medias-at.schaeffler.com/en/service-tips'),
    ('trico', "Why completed PMs don't always mean reliable equipment",
     isl('lubrication'), 'https://www.tricocorp.com/lubricology/why-completed-pms-don%E2%80%99t-always-mean-reliable-equipment'),
    ('trico', "Where should you sample oil? (most people get this wrong)",
     isl('lubrication'), 'https://www.tricocorp.com/lubricology/where-should-you-sample-oil'),
    ('trico', "A practical look at improving oil cleanliness",
     isl('lubrication'), 'https://www.tricocorp.com/lubricology/a-practical-look-at-improving-oil-cleanliness'),
    ('trico', "Doing more with less",
     isl('lubrication'), 'https://www.tricocorp.com/lubricology/doing-more-with-less'),
]

# ----- articles removed (not present in the current content sheet) -------
EXCLUDED_URLS = {_nurl(u) for u in [
    'https://dodgeindustrial.com/dodge-industrial-receives-distinguished-industry-partner-of-the-year-award/',
    'https://dodgeindustrial.com/dodge-industrial-named-large-manufacturer-of-the-year/',
    'https://www.donaldson.com/en/resources/news/donaldson-official-partner-2026-special-olympics/',
    'https://www.donaldson.com/en/resources/news/donaldson-acquires-facet-fuel-fluid-filtration/',
    'https://www.donaldson.com/en/resources/news/donaldson-rings-nyse-closing-bell/',
    'https://www.graco.com/us/en/about-graco/news/articles/2026/q2/new-dayton-headquarters-groundbreaking-ceremony.html',
    'https://www.graco.com/us/en/about-graco/news/articles/2026/q1/100-years-graco-what-else-happened-in-1926.html',
    'https://investors.graco.com/news-releases/news-release-details/graco-foundation-marks-companys-centennial-1-million-commitment',
    'https://investors.graco.com/news-releases/news-release-details/graco-inc-enters-definitive-agreement-acquire-valco-melton',
    'https://investors.graco.com/news-releases/news-release-details/acquisitions-drive-sales-growth',
    'https://investors.graco.com/news-releases/news-release-details/graco-introduces-industrys-first-wirelessly-connected-and',
    'https://investors.graco.com/news-releases/news-release-details/graco-finishes-year-record-quarterly-and-annual-sales',
]}
SUCCESS  = [e for e in SUCCESS  if _nurl(e[3]) not in EXCLUDED_URLS]
FEATURED = [e for e in FEATURED if _nurl(e[3]) not in EXCLUDED_URLS]

# ----- videos / podcasts (tag, title, youtube_id_or_None, url) -----------
VIDEOS = [
    ('PIP', "Industry expert series: introduction to construction", "Yfy_CjNBGJ0",
     'https://www.youtube.com/watch?v=Yfy_CjNBGJ0'),
    ('PIP', "Industry expert series: introduction to manufacturing", "XhEaSLVPU8U",
     'https://www.youtube.com/watch?v=XhEaSLVPU8U'),
    ('PIP', "Doffing contaminated gloves: how-to", "XJJZH5we4jQ",
     'https://www.youtube.com/watch?v=XJJZH5we4jQ'),
    ('PIP', "Cut resistance guide", "21f31WX_bq0",
     'https://www.youtube.com/watch?v=21f31WX_bq0'),
    ('PIP', "Comparing safety helmets: tech talk", "omHVV056ZJU",
     'https://www.youtube.com/watch?v=omHVV056ZJU'),
    ('Milwaukee Tool', "Right-sizing power tool accessories with The Concord Carpenter", "-F3jD3Wi7o8",
     'https://www.youtube.com/watch?v=-F3jD3Wi7o8'),
    ('Milwaukee Tool', "Rethinking workflows with Odell Complete Concrete", None,
     'https://www.youtube.com/@MilwaukeeTool/videos'),
    ('Podcast', "The importance of effective dust control", None,
     'https://www.tiktok.com/@appliedindustrial/video/7620802057703787807'),
    ('Podcast', "How proper sizing reduces downtime and protects your operation", None,
     'https://www.tiktok.com/@appliedindustrial/video/7631962509473271070'),
    ('Podcast', "The deeper problems associated with spillage", None,
     'https://www.tiktok.com/@appliedindustrial/video/7652342568453229855'),
]

# hero background watermark (the Applied "A" mark)
LOGO_URL = ("https://6847819.fs1.hubspotusercontent-na1.net/hubfs/6847819/"
            "Knowledge%20Center/Untitled%20design%20-%202026-06-24T133539.761.png?width=860&t=1782323019012")
CONTACT_URL = "https://www.applied.com/contact"   # Applied contact page
RESOURCES_URL = "https://www.applied.com/"            # FLAG: placeholder destination for pending resources

def esc(s):
    return html.escape(s, quote=True)

# ----- card excerpt (honest, no fabricated stats) ------------------------
def excerpt(supplier_slug, kind):
    name = SUP_LABEL[supplier_slug]
    if kind == 'case-study':
        return ("See how %s helped a customer solve a real operational "
                "challenge. Read the success story for the approach and outcome." % name)
    return ("Practical insight from %s you can put to work on the floor. "
            "Read the full article for the details." % name)

def media_block(supplier_slug, title, url, indent="          "):
    """Render a real <img> if mapped, else the grey placeholder."""
    img = IMAGES.get(_nurl(url))
    if img:
        return ('%s<img src="%s" alt="%s" loading="lazy" width="640" height="400">\n'
                % (indent, esc(img), esc(title)))
    return ('%s<div class="aih-ph" role="img" aria-label="%s preview image, pending">%s</div>\n'
            % (indent, esc(SUP_LABEL[supplier_slug]), esc(SUP_LABEL[supplier_slug])))

def card(supplier_slug, title, inds, url, kind, idx):
    ind_attr = " ".join(inds)
    primary_ind = IND[inds[0]]
    kind_word = "Read the story" if kind == 'case-study' else "Read the article"
    return (
        '      <article class="aih-card" data-supplier="%s" data-industry="%s" data-type="%s">\n'
        '        <div class="aih-card-media">\n'
        '%s'
        '        </div>\n'
        '        <div class="aih-card-body">\n'
        '          <span class="aih-tag">%s</span>\n'
        '          <h3>%s</h3>\n'
        '          <p class="aih-card-supplier">%s</p>\n'
        '          <p class="aih-card-excerpt">%s</p>\n'
        '          <div class="aih-card-foot">\n'
        '            <a class="aih-link" href="%s" rel="noopener" target="_blank">%s %s</a>\n'
        '          </div>\n'
        '        </div>\n'
        '      </article>\n'
    ) % (supplier_slug, ind_attr, kind,
         media_block(supplier_slug, title, url),
         esc(primary_ind), esc(title),
         esc(SUP_LABEL[supplier_slug]), esc(excerpt(supplier_slug, kind)),
         esc(url), kind_word, ARROW)

def write(name, content):
    path = os.path.join(OUT, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("wrote", name, "(%d bytes)" % len(content))

# =========================================================================
# MODULE 01 — HERO
# =========================================================================
def module_01():
    return """<!-- module-01-hero.html | HubSpot: Rich Text / Custom HTML module -->
<div class="aih-lp">
  <section class="aih-hero" aria-labelledby="aih-hero-title">
    <span class="aih-hero-dots aih-hero-dots-tl" aria-hidden="true"></span>
    <span class="aih-hero-dots aih-hero-dots-bl" aria-hidden="true"></span>
    <div class="aih-hero-watermark" aria-hidden="true">
      <img class="aih-hero-watermark-img" src="%s" alt="" loading="eager">
    </div>""" % esc(LOGO_URL) + """
    <div class="aih-container aih-hero-grid">
      <div class="aih-hero-content">
        <h1 id="aih-hero-title" style="color:#ffffff;">Knowledge &amp; Solutions <span class="aih-hero-accent">Center</span></h1>
        <span class="aih-hero-rule" aria-hidden="true"></span>
        <p class="aih-hero-sub">Insights, guides, and expert solutions from Applied&reg; and the
          suppliers we trust, gathered to help your operations run safer, smarter, and more
          efficiently.</p>
        <div class="aih-hero-actions">
          <a class="aih-btn aih-btn-primary" href="#aih-library" data-aih-scroll>Browse the Knowledge Library</a>
          <a class="aih-btn aih-btn-white" href="%s" rel="noopener" target="_blank">Talk to an Applied Specialist</a>
        </div>
      </div>
    </div>
  </section>
</div>
""" % CONTACT_URL

# =========================================================================
# MODULE 02 — FEATURED SUPPLIERS STRIP
# =========================================================================
def module_02():
    chips = ""
    for slug, label, hp in SUPPLIERS:
        chips += ('        <a class="aih-supplier-chip" href="%s" rel="noopener" target="_blank">%s</a>\n'
                  % (esc(hp), esc(label)))
    return """<!-- module-02-suppliers.html | HubSpot: Rich Text / Custom HTML module -->
<div class="aih-lp">
  <section class="aih-suppliers" aria-label="Featured suppliers">
    <div class="aih-container">
      <p class="aih-suppliers-head">Featured suppliers</p>
      <div class="aih-supplier-track">
%s      </div>
    </div>
  </section>
</div>
""" % chips

# =========================================================================
# MODULE 03 — FEATURED SPOTLIGHT CAROUSEL
# =========================================================================
SPOTLIGHT = [
    ('abb', "The role of AI in predictive maintenance",
     "See how AI-driven predictive maintenance helps teams catch issues early, extend "
     "equipment life, and cut unplanned downtime.",
     'https://www.abb.com/global/en/company/stories/ai-predictive-maintenance', 'Featured article'),
    ('regal-rexnord', "What causes gearbox failure?",
     "A clear, practical breakdown of the most common causes of gearbox failure and the "
     "maintenance habits that prevent them.",
     'https://www.regalrexnord.com/regal-rexnord-insights/what-causes-gearbox-failure', 'Maintenance & reliability'),
    ('trico', "Where should you sample oil? (most people get this wrong)",
     "Oil analysis is only as good as the sample. Learn where to pull oil samples for "
     "results you can actually trust.",
     'https://www.tricocorp.com/lubricology/where-should-you-sample-oil', 'Lubrication'),
]
def module_03():
    slides = ""
    dots = ""
    for i, (sup, title, blurb, url, tag) in enumerate(SPOTLIGHT):
        active = " is-active" if i == 0 else ""
        spot_img = IMAGES.get(_nurl(url))
        if spot_img:
            spot_media = ('            <img src="%s" alt="%s" loading="lazy">\n'
                          % (esc(spot_img), esc(title)))
        else:
            spot_media = ('            <div class="aih-ph" role="img" aria-label="%s spotlight image, pending"></div>\n'
                          % esc(SUP_LABEL[sup]))
        slides += (
            '        <div class="aih-spotlight-slide%s">\n'
            '          <div class="aih-spotlight-media">\n'
            '%s'
            '          </div>\n'
            '          <div class="aih-spotlight-body">\n'
            '            <span class="aih-tag">%s</span>\n'
            '            <h2>%s</h2>\n'
            '            <p>%s</p>\n'
            '            <div><a class="aih-btn aih-btn-primary" href="%s" rel="noopener" target="_blank">Read the article</a></div>\n'
            '          </div>\n'
            '        </div>\n'
        ) % (active, spot_media, esc(tag), esc(title), esc(blurb), esc(url))
        sel = "true" if i == 0 else "false"
        dots += ('        <button class="aih-spotlight-dot" type="button" aria-selected="%s" '
                 'aria-label="Show featured item %d"></button>\n' % (sel, i + 1))
    return """<!-- module-03-spotlight.html | HubSpot: Rich Text / Custom HTML module -->
<div class="aih-lp">
  <section class="aih-section aih-bg-grey50" aria-label="Featured content">
    <div class="aih-container">
      <div class="aih-spotlight aih-reveal" data-aih-spotlight>
        <div class="aih-spotlight-card">
%s        </div>
        <div class="aih-spotlight-dots" role="tablist" aria-label="Featured content slides">
%s        </div>
      </div>
    </div>
  </section>
</div>
""" % (slides, dots)

# =========================================================================
# MODULE 04 — KNOWLEDGE LIBRARY (filter sidebar + grids)
# =========================================================================
def industry_filter():
    rows = ('          <label class="aih-check"><input type="checkbox" data-filter="industry" '
            'value="all" checked> All industries</label>\n')
    for slug in IND_ORDER:
        rows += ('          <label class="aih-check"><input type="checkbox" data-filter="industry" '
                 'value="%s"> %s</label>\n' % (slug, esc(IND[slug])))
    return rows

def supplier_filter():
    rows = ""
    for i, (slug, label, hp) in enumerate(SUPPLIERS):
        hide = "" if i < 6 else " aih-supplier-hidden"
        rows += ('          <label class="aih-check%s" data-supplier-row="%s"><input type="checkbox" '
                 'data-filter="supplier" value="%s"> %s</label>\n'
                 % (hide, esc(label), slug, esc(label)))
    return rows

def type_filter():
    # Only the two content types that exist as filterable cards in this module.
    # Videos and PDFs/Downloads have their own dedicated sections (modules 05 & 06),
    # so they are intentionally not listed here (avoids empty-result dead-ends).
    types = [('article', 'Articles'), ('case-study', 'Case studies')]
    rows = ""
    for slug, label in types:
        rows += ('          <label class="aih-check"><input type="checkbox" data-filter="type" '
                 'value="%s"> %s</label>\n' % (slug, esc(label)))
    return rows

def module_04():
    total = len(SUCCESS) + len(FEATURED)
    success_cards = "".join(card(s, t, inds, u, 'case-study', i)
                            for i, (s, t, inds, u) in enumerate(SUCCESS))
    featured_cards = "".join(card(s, t, inds, u, 'article', i)
                             for i, (s, t, inds, u) in enumerate(FEATURED))
    return """<!-- module-04-library.html | HubSpot: Rich Text / Custom HTML module -->
<div class="aih-lp">
  <section class="aih-section aih-bg-grey50" id="aih-library" aria-labelledby="aih-library-h">
    <div class="aih-container-wide aih-container">
      <div class="aih-libhead">
        <div class="aih-libhead-body">
          <h2 id="aih-library-h" class="aih-libhead-title">Knowledge Library</h2>
          <span class="aih-libhead-rule" aria-hidden="true"></span>
          <p class="aih-libhead-sub">Browse expert articles and customer success stories from
            Applied&reg; suppliers. Filter by industry, supplier, or content type to find what
            fits your operation.</p>
        </div>
      </div>
      <div class="aih-library-grid">

        <!-- FILTER SIDEBAR -->
        <aside class="aih-filters" aria-label="Refine your results">
          <p class="aih-filters-title">Refine your results</p>

          <div class="aih-filter-group">
            <button class="aih-filter-legend" type="button">Industry %s</button>
            <div class="aih-filter-options">
%s            </div>
          </div>

          <div class="aih-filter-group">
            <button class="aih-filter-legend" type="button">Supplier %s</button>
            <input class="aih-filter-search aih-supplier-search" type="search" placeholder="Search suppliers" aria-label="Search suppliers">
            <div class="aih-filter-options">
%s              <button class="aih-filter-more" type="button"><span data-label>Show more</span></button>
            </div>
          </div>

          <div class="aih-filter-group">
            <button class="aih-filter-legend" type="button">Content type %s</button>
            <div class="aih-filter-options">
%s            </div>
          </div>

          <div class="aih-filter-actions">
            <button class="aih-btn aih-btn-primary aih-btn-block aih-apply" type="button">Apply filters</button>
            <button class="aih-btn aih-btn-secondary aih-btn-block aih-clear" type="button">Clear all</button>
          </div>
        </aside>

        <!-- RESULTS -->
        <div class="aih-results">
          <div class="aih-results-bar">
            <p class="aih-results-count">Showing <strong data-result-count>%d</strong> results</p>
          </div>

          <div class="aih-results-empty">No results match those filters. Try clearing a filter or two.</div>

          <div class="aih-content-block" data-block="success">
            <div class="aih-shead">
              <h2>Customer success stories</h2>
            </div>
            <div class="aih-card-grid">
%s            </div>
            <div class="aih-showmore-wrap" hidden>
              <button class="aih-btn aih-btn-secondary aih-showmore" type="button" aria-expanded="false">Show more</button>
            </div>
          </div>

          <div class="aih-content-block" data-block="featured">
            <div class="aih-shead">
              <h2>Featured articles</h2>
            </div>
            <div class="aih-card-grid">
%s            </div>
            <div class="aih-showmore-wrap" hidden>
              <button class="aih-btn aih-btn-secondary aih-showmore" type="button" aria-expanded="false">Show more</button>
            </div>
          </div>

        </div>
      </div>
    </div>
  </section>
</div>
""" % (CHEVRON, industry_filter(), CHEVRON, supplier_filter(), CHEVRON, type_filter(),
       total, success_cards, featured_cards)

# =========================================================================
# MODULE 05 — VIDEO LIBRARY
# =========================================================================
def module_05():
    cards = ""
    for tag, title, ytid, url in VIDEOS:
        if tag == "Podcast":
            m = re.search(r'/video/(\d+)', url)
            tk = m.group(1) if m else ''
            media = (
                '        <iframe class="aih-video-frame" src="https://www.tiktok.com/player/v1/%s" '
                'title="%s" allow="autoplay; encrypted-media; fullscreen; picture-in-picture" '
                'allowfullscreen loading="lazy"></iframe>\n'
            ) % (tk, esc(title))
        elif ytid:
            thumb = "https://img.youtube.com/vi/%s/hqdefault.jpg" % ytid
            media = (
                '        <button class="aih-video-facade" type="button" data-yt="%s" '
                'data-yt-title="%s" aria-label="Play video: %s">\n'
                '          <img src="%s" alt="%s thumbnail" loading="lazy" width="480" height="360">\n'
                '          <span class="aih-video-play">%s</span>\n'
                '        </button>\n'
            ) % (ytid, esc(title), esc(title), thumb, esc(tag), PLAY)
        else:
            # no embeddable id (channel link) -> link out
            media = (
                '        <a class="aih-video-facade" href="%s" rel="noopener" target="_blank" '
                'aria-label="Watch on YouTube: %s">\n'
                '          <div class="aih-ph" role="img" aria-label="%s thumbnail, pending"></div>\n'
                '          <span class="aih-video-play">%s</span>\n'
                '        </a>\n'
            ) % (esc(url), esc(title), esc(tag), PLAY)
        cards += (
            '      <div class="aih-video-card">\n'
            '%s'
            '        <div class="aih-video-body">\n'
            '          <span class="aih-tag">%s</span>\n'
            '          <h3>%s</h3>\n'
            '        </div>\n'
            '      </div>\n'
        ) % (media, esc(tag), esc(title))

    return """<!-- module-05-videos.html | HubSpot: CUSTOM HTML module
     NOTE: contains click-to-load YouTube facades (FOOTER JS) and inline
     TikTok player iframes. Paste as a Custom HTML module so data- attributes
     and <iframe> tags are preserved. -->
<div class="aih-lp">
  <section class="aih-section aih-bg-grey50" aria-labelledby="aih-video-h">
    <div class="aih-container">
      <div class="aih-shead">
        <h2 id="aih-video-h">Video library</h2>
        <a class="aih-viewall" href="https://www.youtube.com/results?search_query=industrial+maintenance+safety" rel="noopener" target="_blank">View all videos</a>
      </div>
      <div class="aih-video-grid aih-reveal">
%s      </div>
    </div>
  </section>
</div>""" % cards

# =========================================================================
# MODULE 06 — PRODUCT & INDUSTRY RESOURCES (placeholders, flagged pending)
# =========================================================================
PDF_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
            '<path d="M14 2v6h6"/></svg>')
VIDEO_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
              'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<rect x="2" y="5" width="14" height="14" rx="2"/><path d="m22 8-6 4 6 4z"/></svg>')
CHECK_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
              'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>')
GUIDE_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
              'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>'
              '<path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>')

def module_06():
    # (icon, tag, title, desc, cta, href, pending)
    res = [
        (GUIDE_ICON, "Catalog", "Request a catalog",
         "Browse the full Applied product line and request your copy of the catalog.",
         "Request a catalog", "https://www.applied.com/catalog", False),
        (VIDEO_ICON, "Video", "Bearing installation best practices",
         "Step-by-step best practices to ensure longer bearing life.",
         "Watch video", RESOURCES_URL, True),
        (CHECK_ICON, "Checklist", "Preventive maintenance checklist",
         "Use this checklist to keep your equipment running at peak performance.",
         "View checklist", RESOURCES_URL, True),
        (GUIDE_ICON, "Guide", "Pneumatics buyer's guide",
         "Key considerations when selecting pneumatic systems and components.",
         "View guide", RESOURCES_URL, True),
    ]
    cards = ""
    for icon, tag, title, desc, cta, href, pending in res:
        cls = "aih-res-card aih-pending" if pending else "aih-res-card"
        cards += (
            '        <article class="%s">\n'
            '          <div class="aih-res-icon">%s</div>\n'
            '          <span class="aih-tag">%s</span>\n'
            '          <h3>%s</h3>\n'
            '          <p>%s</p>\n'
            '          <div><a class="aih-btn aih-btn-secondary aih-btn-sm" href="%s" rel="noopener" target="_blank">%s</a></div>\n'
            '        </article>\n'
        ) % (cls, icon, esc(tag), esc(title), esc(desc), esc(href), esc(cta))
    return """<!-- module-06-resources.html | HubSpot: Rich Text / Custom HTML module
     PENDING: real PDF/checklist/guide assets and URLs not supplied. Cards link to a
     placeholder Applied URL and are marked .aih-pending. Replace href + copy when ready. -->
<div class="aih-lp">
  <section class="aih-section aih-bg-white" aria-labelledby="aih-res-h">
    <div class="aih-container">
      <div class="aih-shead">
        <h2 id="aih-res-h">Product &amp; industry resources</h2>
        <a class="aih-viewall" href="%s" rel="noopener" target="_blank">View all</a>
      </div>
      <div class="aih-res-grid aih-reveal">
%s      </div>
    </div>
  </section>
</div>
""" % (RESOURCES_URL, cards)

# =========================================================================
# MODULE 07 — CLOSING CTA BAND
# =========================================================================
def module_07():
    return """<!-- module-07-cta.html | HubSpot: Rich Text / Custom HTML module -->
<div class="aih-lp">
  <section class="aih-cta" aria-labelledby="aih-cta-h">
    <div class="aih-container">
      <div class="aih-cta-inner aih-reveal">
        <div class="aih-cta-text">
          <h2 id="aih-cta-h" style="color:#ffffff;">Need help finding the right solution?</h2>
          <p>Connect with an Applied&reg; specialist to find the right supplier, product, or resource
            for your application.</p>
        </div>
        <div class="aih-cta-actions">
          <a class="aih-btn aih-btn-white" href="%s" rel="noopener" target="_blank">Contact an Applied specialist</a>
          <a class="aih-btn aih-btn-ghost" href="#aih-library" data-aih-scroll>Back to the library</a>
        </div>
      </div>
    </div>
  </section>
</div>
""" % CONTACT_URL

# =========================================================================
def write_manifest():
    """Emit the article->image mapping template (won't clobber a filled one)."""
    path = os.path.join(OUT, 'article-images.csv')
    if os.path.exists(path):
        print("article-images.csv already exists, leaving it as-is")
        return
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['Section', 'Supplier', 'Title', 'Article URL', 'Image URL'])
        for (s, t, inds, u) in SUCCESS:
            w.writerow(['Customer Success Stories', SUP_LABEL[s], t, u, ''])
        for (s, t, inds, u) in FEATURED:
            w.writerow(['Featured Articles', SUP_LABEL[s], t, u, ''])
    print("wrote article-images.csv template")

if __name__ == "__main__":
    write_manifest()
    write("module-01-hero.html", module_01())
    write("module-02-suppliers.html", module_02())
    write("module-03-spotlight.html", module_03())
    write("module-04-library.html", module_04())
    write("module-05-videos.html", module_05())
    write("module-06-resources.html", module_06())
    write("module-07-cta.html", module_07())
    print("done.")
