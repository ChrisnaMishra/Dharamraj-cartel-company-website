"""Build the Nepali pages (ne/) from the English pages, and add language links + hreflang to both.

Run from the repo root:  python tools/build_nepali.py
Every replacement must match, so the script fails loudly if the English page changed.
"""
import re, os, json

BASE = "https://www.dharamrajcartel.com.np"
PAGES = {"index.html": "/", "products.html": "/products", "legal.html": "/legal"}
NE_PATH = {"index.html": "/ne/", "products.html": "/ne/products", "legal.html": "/ne/legal"}


def sub(s, old, new, count=None, f=""):
    n = s.count(old)
    assert n >= 1, f"{f}: not found: {old[:70]!r}"
    if count is not None:
        assert n == count, f"{f}: expected {count}x, found {n}x: {old[:70]!r}"
    return s.replace(old, new)


# ---------- shared (all pages) ----------
COMMON = [
    ('<html lang="en">', '<html lang="ne">'),
    ('<a class="skip" href="#main">Skip to content</a>', '<a class="skip" href="#main">मुख्य भागमा जानुहोस्</a>'),
    ('<span>Dharamraj Cartel</span></a>', '<span>धर्मराज कार्टेल</span></a>'),
    ('<nav aria-label="Main">', '<nav aria-label="मुख्य मेनु">'),
    ('>What we trade</a>', '>के बेच्छौं</a>'),
    ('>Products</a>', '>सामानहरू</a>'),
    ('>About</a>', '>हाम्रोबारे</a>'),
    ('>Contact</a>', '>सम्पर्क</a>'),
    # footer
    ('<h2>Contact</h2>', '<h2>सम्पर्क</h2>'),
    ('<p>Complaints: ', '<p>उजुरी: '),
    ('<h2>Registered firm</h2>', '<h2>दर्ता भएको फर्म</h2>'),
    ('<p>Dharamraj Cartel<br>Firm Reg. No. 001-2880 (registered 2083-08-01 B.S.)<br>Department of Commerce, Supplies and Consumer Protection</p>',
     '<p>धर्मराज कार्टेल<br>प्रा.फ.र.नं. ००१-२८८० (दर्ता मिति २०८३-०८-०१)<br>वाणिज्य, आपूर्ति तथा उपभोक्ता संरक्षण विभाग</p>'),
    ('<p>We come to you, anywhere in Nepal.<br><span lang="ne">नेपालभरि सेवा</span></p>',
     '<p>नेपालभर जहाँ भए पनि हामी तपाईंकहाँ आउँछौं।<br><span lang="en">We come to you, anywhere in Nepal.</span></p>'),
    ('<p>We sell directly. We are not a marketplace.</p>', '<p>हामी आफैं सिधै बेच्छौं। हामी अरूको सामान बेच्ने बजार (marketplace) होइनौं।</p>'),
    ('<h2>Policies</h2>', '<h2>नीतिहरू</h2>'),
    ('>Terms</a>', '>सर्तहरू</a>'),
    ('>Privacy</a>', '>गोपनीयता</a>'),
    ('>Returns</a>', '>फिर्ता</a>'),
    ('>Complaints</a>', '>उजुरी</a>'),
    ('© 2026 Dharamraj Cartel', '© २०२६ धर्मराज कार्टेल'),
    ('aria-label="Chat with Dharamraj Cartel on WhatsApp"', 'aria-label="WhatsApp मा धर्मराज कार्टेलसँग कुरा गर्नुहोस्"'),
    ('Namaste%20Dharamraj%20Cartel%2C%20I%20would%20like%20a%20price.',
     '%E0%A4%A8%E0%A4%AE%E0%A4%B8%E0%A5%8D%E0%A4%A4%E0%A5%87%20%E0%A4%A7%E0%A4%B0%E0%A5%8D%E0%A4%AE%E0%A4%B0%E0%A4%BE%E0%A4%9C%20%E0%A4%95%E0%A4%BE%E0%A4%B0%E0%A5%8D%E0%A4%9F%E0%A5%87%E0%A4%B2%2C%20%E0%A4%AE%E0%A4%B2%E0%A4%BE%E0%A4%88%20%E0%A4%AE%E0%A5%82%E0%A4%B2%E0%A5%8D%E0%A4%AF%20%E0%A4%9A%E0%A4%BE%E0%A4%B9%E0%A4%BF%E0%A4%AF%E0%A5%8B%E0%A5%A4'),
    ('<meta property="og:site_name" content="Dharamraj Cartel">', '<meta property="og:site_name" content="धर्मराज कार्टेल">'),
    ('content="Dharamraj Cartel golden Kalash emblem with the company name and trade lines"',
     'content="धर्मराज कार्टेलको सुनौलो कलश चिन्ह, कम्पनीको नाम र व्यापारका क्षेत्रसहित"'),
]

PER_PAGE = {
    "index.html": [
        ('<title>Dharamraj Cartel | Import, export and wholesale</title>', '<title>धर्मराज कार्टेल | आयात, निर्यात र थोक बिक्री</title>'),
        ('content="Dharamraj Cartel | Import, export and wholesale"', 'content="धर्मराज कार्टेल | आयात, निर्यात र थोक बिक्री"'),
        ('content="Dharamraj Cartel, Nepal. Import, export and wholesale of electrical goods and electronics, hardware, construction materials, vehicle spare parts and machinery parts."',
         'content="धर्मराज कार्टेल, नेपाल। बिजुली तथा इलेक्ट्रोनिक सामान, हार्डवेयर, निर्माण सामग्री, सवारी साधनका स्पेयर पार्ट्स र मेसिनरी पार्ट्सको आयात, निर्यात र थोक बिक्री।"'),
        ('<p class="deva" lang="ne">धर्मराज कार्टेल</p>', '<p class="deva" lang="en">Dharamraj Cartel</p>'),
        ('<h1>Parts, hardware and building materials for Nepal.</h1>', '<h1>नेपालभरका लागि पार्ट्स, हार्डवेयर र निर्माण सामग्री।</h1>'),
        ('<p class="lead">We import, export and wholesale for shops, workshops and builders, sourcing from India and overseas.</p>',
         '<p class="lead">हामी भारत र विदेशबाट सामान ल्याएर पसल, वर्कसप र निर्माण व्यवसायीहरूलाई आयात, निर्यात र थोक बिक्री गर्छौं।</p>'),
        ('WhatsApp us</a>', 'WhatsApp गर्नुहोस्</a>'),
        ('Call 9845656595</a>', 'फोन गर्नुहोस् 9845656595</a>'),
        ('<a href="#enquiry">Or send us your full parts list &rarr;</a>', '<a href="#enquiry">वा आफ्नो पूरा पार्ट्स सूची पठाउनुहोस् &rarr;</a>'),
        ('<ul class="trust" aria-label="Why buy from us">', '<ul class="trust" aria-label="हामीबाट किन किन्ने">'),
        ('<li>Registered firm</li>', '<li>दर्ता भएको फर्म</li>'),
        ('<li>Import from India and overseas</li>', '<li>भारत र विदेशबाट आयात</li>'),
        ('<li>Wholesale for shops, workshops and builders</li>', '<li>पसल, वर्कसप र निर्माण व्यवसायीका लागि थोक</li>'),
        ('<li>We come to you, anywhere in Nepal</li>', '<li>नेपालभर जहाँ भए पनि हामी आउँछौं</li>'),
        ('<img class="hero-logo" src="./favicon.svg" alt="Dharamraj Cartel logo"', '<img class="hero-logo" src="../favicon.svg" alt="धर्मराज कार्टेलको लोगो"'),
        ('<h2>What we trade</h2>', '<h2>हामी के के बेच्छौं</h2>'),
        ('<p class="section-lead">One supplier for five trade lines. Tap a line to see what we stock.</p>',
         '<p class="section-lead">एउटै सप्लायर, पाँच किसिमका सामान। हेर्न चाहेको समूह छान्नुहोस्।</p>'),
        ('<h3>Vehicle spare parts</h3><p>Motorcycle and motor vehicle parts: engine, brake and clutch, electrical, filters and accessories.</p>',
         '<h3>सवारी साधनका स्पेयर पार्ट्स</h3><p>मोटरसाइकल र गाडीका पार्ट्स: इन्जिन, ब्रेक र क्लच, बिजुलीका पार्ट्स, फिल्टर र एक्सेसरिज।</p>'),
        ('<h3>Electrical and electronics</h3><p>Wires and cables, switches, MCBs, LED lights, batteries and electronic goods.</p>',
         '<h3>बिजुली तथा इलेक्ट्रोनिक्स</h3><p>तार र केबल, स्विच, MCB, LED बत्ती, ब्याट्री र इलेक्ट्रोनिक सामान।</p>'),
        ('<h3>Machinery parts</h3><p>Bearings, V-belts, pump and motor spares and other machine parts.</p>',
         '<h3>मेसिनरी पार्ट्स</h3><p>बेयरिङ, V-बेल्ट, पम्प र मोटरका स्पेयर तथा अन्य मेसिनका पार्ट्स।</p>'),
        ('<h3>Hardware</h3><p>Fixings, wire, welding rods, plumbing fittings, tools and general hardware.</p>',
         '<h3>हार्डवेयर</h3><p>किला-काँटी, तार, वेल्डिङ रड, प्लम्बिङ फिटिङ, औजार र अन्य हार्डवेयर।</p>'),
        ('<h3>Construction materials</h3><p>Cement, TMT and M.S. sections, pipes, G.I. and HR sheets, shutter sections.</p>',
         '<h3>निर्माण सामग्री</h3><p>सिमेन्ट, TMT र M.S. सेक्सन, पाइप, G.I. र HR सिट, सटर सेक्सन।</p>'),
        ('<span class="tile-more">See products &rarr;</span>', '<span class="tile-more">सामान हेर्नुहोस् &rarr;</span>'),
        ('<h2>How an order works</h2>', '<h2>अर्डर कसरी हुन्छ</h2>'),
        ('<li><h3>Tell us what you need</h3><p>Product, specification, quantity and where it should go.</p></li>',
         '<li><h3>तपाईंलाई के चाहिन्छ भन्नुहोस्</h3><p>सामान, स्पेसिफिकेसन, परिमाण र कहाँ पुर्‍याउनुपर्ने हो।</p></li>'),
        ('<li><h3>We check and quote</h3><p>Availability, price, duties, lead time and delivery terms.</p></li>',
         '<li><h3>हामी जाँचेर मूल्य दिन्छौं</h3><p>उपलब्धता, मूल्य, भन्सार, लाग्ने समय र डेलिभरीका सर्तहरू।</p></li>'),
        ('<li><h3>We agree in writing</h3><p>Nothing is ordered or paid for until both sides have agreed.</p></li>',
         '<li><h3>लिखित रूपमा सहमति</h3><p>दुवै पक्ष सहमत नभएसम्म केही पनि अर्डर वा भुक्तानी हुँदैन।</p></li>'),
        ('<h2>About Dharamraj Cartel</h2>', '<h2>धर्मराज कार्टेलको बारेमा</h2>'),
        ('<p class="section-lead">A Nepali trading firm that imports, exports and supplies wholesale, and comes to its customers.</p>',
         '<p class="section-lead">आयात, निर्यात र थोक बिक्री गर्ने नेपाली व्यापारिक फर्म, जुन ग्राहकसम्म आफैं पुग्छ।</p>'),
        ('<div><h3>Registered in Nepal</h3><p>Registered with the Department of Commerce, Supplies and Consumer Protection, Firm Reg. No. 001-2880.</p></div>',
         '<div><h3>नेपालमा दर्ता</h3><p>वाणिज्य, आपूर्ति तथा उपभोक्ता संरक्षण विभागमा दर्ता, प्रा.फ.र.नं. ००१-२८८०।</p></div>'),
        ('<div><h3>Sourced from India and overseas</h3><p>We import directly and supply in bulk to shops, workshops, garages and builders.</p></div>',
         '<div><h3>भारत र विदेशबाट आयात</h3><p>हामी सिधै आयात गरेर पसल, वर्कसप, ग्यारेज र निर्माण व्यवसायीलाई थोकमा उपलब्ध गराउँछौं।</p></div>'),
        ('<div><h3>We come to you</h3><p>We travel across Nepal to meet customers, so you deal with us in person, wherever you are.</p></div>',
         '<div><h3>हामी तपाईंकहाँ आउँछौं</h3><p>हामी नेपालभर ग्राहकलाई भेट्न जान्छौं, त्यसैले तपाईं जहाँ भए पनि हामीसँग आमनेसामने कुरा गर्न सक्नुहुन्छ।</p></div>'),
        ('<div><h3>Clear quotes, agreed in writing</h3><p>Send your list and we confirm price, stock and delivery. Nothing is ordered or paid for until both sides agree.</p></div>',
         '<div><h3>स्पष्ट मूल्य, लिखित सहमति</h3><p>सूची पठाउनुहोस्, हामी मूल्य, स्टक र डेलिभरी पक्का गर्छौं। दुवै पक्ष सहमत नभएसम्म केही पनि अर्डर वा भुक्तानी हुँदैन।</p></div>'),
        ('<h2>Ask for a price</h2>', '<h2>मूल्य सोध्नुहोस्</h2>'),
        ('<p>This form writes a WhatsApp message for you. It is sent only when you tap Send in WhatsApp. No payment is taken here.</p>',
         '<p>यो फारमले तपाईंका लागि WhatsApp सन्देश तयार गर्छ। WhatsApp मा Send थिचेपछि मात्र सन्देश जान्छ। यहाँ कुनै भुक्तानी लिइँदैन।</p>'),
        ('<label>Your name<input', '<label>तपाईंको नाम<input'),
        ('<label>Shop or business (optional)<input', '<label>पसल वा व्यवसाय (ऐच्छिक)<input'),
        ('<label>Product line\n', '<label>सामानको किसिम\n'),
        ('<option value="">Choose one</option>', '<option value="">छान्नुहोस्</option>'),
        ('<option>Electrical and electronics</option>', '<option>बिजुली तथा इलेक्ट्रोनिक्स</option>'),
        ('<option>Hardware</option>', '<option>हार्डवेयर</option>'),
        ('<option>Construction materials</option>', '<option>निर्माण सामग्री</option>'),
        ('<option>Vehicle spare parts</option>', '<option>सवारी साधनका स्पेयर पार्ट्स</option>'),
        ('<option>Machinery parts</option>', '<option>मेसिनरी पार्ट्स</option>'),
        ('<label>Quantity<input', '<label>परिमाण<input'),
        ('<label class="full">What do you need?<textarea', '<label class="full">तपाईंलाई के चाहिन्छ?<textarea'),
        ('<button class="btn full" type="submit">Write WhatsApp message</button>', '<button class="btn full" type="submit">WhatsApp सन्देश तयार गर्नुहोस्</button>'),
        ('<p class="full small">See our <a href="./legal.html">terms, privacy and returns</a>.</p>',
         '<p class="full small">हाम्रा <a href="./legal.html">सर्त, गोपनीयता र फिर्ता नीति</a> हेर्नुहोस्।</p>'),
    ],
    "products.html": [
        ('<title>Products | Dharamraj Cartel</title>', '<title>सामानहरू | धर्मराज कार्टेल</title>'),
        ('content="Products | Dharamraj Cartel"', 'content="सामानहरू | धर्मराज कार्टेल"'),
        ('content="Dharamraj Cartel, Nepal. Import, export and wholesale of electrical goods and electronics, hardware, construction materials, vehicle spare parts and machinery parts."',
         'content="धर्मराज कार्टेलका सामानहरू: सवारी साधनका स्पेयर पार्ट्स, बिजुली तथा इलेक्ट्रोनिक सामान, मेसिनरी पार्ट्स, हार्डवेयर र निर्माण सामग्री।"'),
        ('<h1>Products</h1>', '<h1>सामानहरू</h1>'),
        ('<p>Vehicle spare parts, electrical goods and electronics, machinery parts, hardware and construction materials. Ask us about price, specification, stock and delivery before ordering.</p>',
         '<p>सवारी साधनका स्पेयर पार्ट्स, बिजुली तथा इलेक्ट्रोनिक सामान, मेसिनरी पार्ट्स, हार्डवेयर र निर्माण सामग्री। अर्डर गर्नुअघि मूल्य, स्पेसिफिकेसन, स्टक र डेलिभरीबारे सोध्नुहोस्।</p>'),
        ('aria-label="Trade line"', 'aria-label="सामानको किसिम"'),
        ('aria-pressed="true">All</button>', 'aria-pressed="true">सबै</button>'),
        ('aria-pressed="false">Vehicle parts</button>', 'aria-pressed="false">सवारी पार्ट्स</button>'),
        ('aria-pressed="false">Electrical and electronics</button>', 'aria-pressed="false">बिजुली तथा इलेक्ट्रोनिक्स</button>'),
        ('aria-pressed="false">Machinery parts</button>', 'aria-pressed="false">मेसिनरी पार्ट्स</button>'),
        ('aria-pressed="false">Hardware</button>', 'aria-pressed="false">हार्डवेयर</button>'),
        ('aria-pressed="false">Construction materials</button>', 'aria-pressed="false">निर्माण सामग्री</button>'),
        ('<label>Search<input', '<label>खोज्नुहोस्<input'),
        ('<label>Group<select id="group"><option value="">All groups</option>', '<label>समूह<select id="group"><option value="">सबै समूह</option>'),
        ('<div><h2>Have a long parts list?</h2><p>Send the whole list on WhatsApp, as a photo or typed. We quote everything in one go.</p></div>',
         '<div><h2>लामो पार्ट्स सूची छ?</h2><p>पूरा सूची WhatsApp मा पठाउनुहोस्, फोटो खिचेर वा टाइप गरेर। हामी सबैको मूल्य एकैपटक दिन्छौं।</p></div>'),
        ('Namaste%20Dharamraj%20Cartel%2C%20here%20is%20my%20parts%20list%3A',
         '%E0%A4%A8%E0%A4%AE%E0%A4%B8%E0%A5%8D%E0%A4%A4%E0%A5%87%20%E0%A4%A7%E0%A4%B0%E0%A5%8D%E0%A4%AE%E0%A4%B0%E0%A4%BE%E0%A4%9C%20%E0%A4%95%E0%A4%BE%E0%A4%B0%E0%A5%8D%E0%A4%9F%E0%A5%87%E0%A4%B2%2C%20%E0%A4%AF%E0%A5%8B%20%E0%A4%AE%E0%A5%87%E0%A4%B0%E0%A5%8B%20%E0%A4%AA%E0%A4%BE%E0%A4%B0%E0%A5%8D%E0%A4%9F%E0%A5%8D%E0%A4%B8%20%E0%A4%B8%E0%A5%82%E0%A4%9A%E0%A5%80%20%E0%A4%B9%E0%A5%8B%3A'),
        ('>Send my list on WhatsApp</a>', '>मेरो सूची WhatsApp मा पठाउनुहोस्</a>'),
    ],
    "legal.html": [
        ('<title>Terms, privacy and returns | Dharamraj Cartel</title>', '<title>सर्त, गोपनीयता र फिर्ता | धर्मराज कार्टेल</title>'),
        ('content="Terms, privacy and returns | Dharamraj Cartel"', 'content="सर्त, गोपनीयता र फिर्ता | धर्मराज कार्टेल"'),
        ('<h1>Terms, privacy and returns</h1></div></section>',
         '<h1>सर्त, गोपनीयता र फिर्ता</h1><p>यो अंग्रेजी पृष्ठको अनुवाद हो। फरक परेमा <a href="../legal.html">अंग्रेजी संस्करण</a> मान्य हुनेछ।</p></div></section>'),
        ('<h2>Who we are</h2>', '<h2>हामी को हौं</h2>'),
        ('<p>Dharamraj Cartel is a private firm registered in Nepal, Firm Reg. No. 001-2880 (registered 2083-08-01 B.S.), Department of Commerce, Supplies and Consumer Protection. We serve customers across Nepal. We sell directly and do not run a marketplace for other sellers.</p>',
         '<p>धर्मराज कार्टेल वाणिज्य, आपूर्ति तथा उपभोक्ता संरक्षण विभागमा दर्ता भएको नेपाली प्राइभेट फर्म हो, प्रा.फ.र.नं. ००१-२८८० (दर्ता मिति २०८३-०८-०१)। हामी नेपालभरका ग्राहकलाई सेवा दिन्छौं। हामी आफैं सिधै बेच्छौं र अरू बिक्रेताका लागि बजार (marketplace) चलाउँदैनौं।</p>'),
        ('<h2>Orders and payment</h2>', '<h2>अर्डर र भुक्तानी</h2>'),
        ('<p>This website takes enquiries only. It does not take orders or payments. Price, specification, delivery and payment terms are agreed with you before an order is confirmed.</p>',
         '<p>यो वेबसाइटबाट सोधपुछ मात्र गर्न सकिन्छ। यहाँ अर्डर वा भुक्तानी लिइँदैन। अर्डर पक्का हुनुअघि मूल्य, स्पेसिफिकेसन, डेलिभरी र भुक्तानीका सर्त तपाईंसँग सहमति गरिन्छ।</p>'),
        ('<h2 id="returns">Returns</h2>', '<h2 id="returns">फिर्ता</h2>'),
        ('<p>We do not offer returns or exchanges for a change of mind. This does not limit any rights you have under Nepali law, including where goods are defective, damaged or not as agreed. In those cases, please contact us.</p>',
         '<p>मन परिवर्तन भएको कारणले हामी सामान फिर्ता वा साटफेर गर्दैनौं। यसले नेपाली कानुनअन्तर्गत तपाईंका अधिकारहरू सीमित गर्दैन, जस्तै सामान बिग्रेको, क्षति भएको वा सहमतिअनुसार नभएको अवस्थामा। त्यस्तो अवस्थामा कृपया हामीलाई सम्पर्क गर्नुहोस्।</p>'),
        ('<h2 id="privacy">Privacy</h2>', '<h2 id="privacy">गोपनीयता</h2>'),
        ('<p>The enquiry form prepares a WhatsApp message in your browser. We receive your details only if you send that message, and we use them to answer your enquiry and handle any order. Messages you send are also handled by WhatsApp. This site is hosted on Cloudflare Pages and loads fonts from Google Fonts, which may receive technical data such as your IP address. To ask about your information, please contact us.</p>',
         '<p>सोधपुछ फारमले तपाईंको ब्राउजरमै WhatsApp सन्देश तयार गर्छ। तपाईंले त्यो सन्देश पठाएपछि मात्र तपाईंको विवरण हामीसम्म आउँछ, र हामी त्यसलाई तपाईंको सोधपुछको जवाफ दिन र अर्डर मिलाउन प्रयोग गर्छौं। तपाईंले पठाएका सन्देश WhatsApp ले पनि ह्यान्डल गर्छ। यो साइट Cloudflare Pages मा राखिएको छ र Google Fonts बाट फन्ट लोड गर्छ, जसले तपाईंको IP ठेगाना जस्ता प्राविधिक विवरण पाउन सक्छ। आफ्नो जानकारीबारे सोध्न कृपया हामीलाई सम्पर्क गर्नुहोस्।</p>'),
        ('<h2 id="complaints">Complaints and contact</h2>', '<h2 id="complaints">उजुरी र सम्पर्क</h2>'),
        ('<p>Phone and WhatsApp: ', '<p>फोन र WhatsApp: '),
        ('<br>Email: <a href="mailto:', '<br>इमेल: <a href="mailto:'),
    ],
}

# Paths: ne/ pages live one folder down
ASSET_FIX = [
    ('href="./favicon.svg', 'href="../favicon.svg'),
    ('src="./favicon.svg', 'src="../favicon.svg'),
    ('href="./manifest.webmanifest"', 'href="../manifest.webmanifest"'),
    ('href="./apple-touch-icon.png"', 'href="../apple-touch-icon.png"'),
    ('href="./style.css', 'href="../style.css'),
    ('src="./goods.js', 'src="../goods.js'),
    ('src="./script.js', 'src="../script.js'),
]


def lang_link(target_href, label, lang):
    return f'<a class="lang" href="{target_href}" lang="{lang}" hreflang="{lang}">{label}</a>'


def hreflang_block(en_path, ne_path):
    return (f'<link rel="alternate" hreflang="en" href="{BASE}{en_path}">\n'
            f'<link rel="alternate" hreflang="ne" href="{BASE}{ne_path}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{BASE}{en_path}">\n')


os.makedirs("ne", exist_ok=True)
for f, en_path in PAGES.items():
    en = open(f, encoding="utf-8").read()
    ne_path = NE_PATH[f]
    # strip any earlier hreflang / lang link so the script can be re-run
    en = re.sub(r'<link rel="alternate" hreflang="[^"]+" href="[^"]+">\n', '', en)
    en = re.sub(r'\n  <a class="lang" [^\n]*</a>', '', en)

    ne = en
    for old, new in COMMON + PER_PAGE[f]:
        ne = sub(ne, old, new, f=f"ne/{f}")
    for old, new in ASSET_FIX:
        if old in ne:
            ne = ne.replace(old, new)
    # canonical, og:url, og:locale
    ne = sub(ne, f'<link rel="canonical" href="{BASE}{en_path}">', f'<link rel="canonical" href="{BASE}{ne_path}">', 1, f)
    ne = sub(ne, f'<meta property="og:url" content="{BASE}{en_path}">', f'<meta property="og:url" content="{BASE}{ne_path}">\n<meta property="og:locale" content="ne_NP">', 1, f)
    # Nepali pages: no Google verification tag / JSON-LD duplicates
    ne = re.sub(r'<meta name="google-site-verification"[^>]*>\n', '', ne)
    ne = re.sub(r'<script type="application/ld\+json">.*?</script>\n', '', ne, flags=re.S)
    # brand link + 404-safe home link
    # hreflang + language switch
    for doc, is_ne in ((en, False), (ne, True)):
        pass
    en = sub(en, '<link rel="canonical"', hreflang_block(en_path, ne_path) + '<link rel="canonical"', 1, f)
    ne = sub(ne, '<link rel="canonical"', hreflang_block(en_path, ne_path) + '<link rel="canonical"', 1, f)
    ne_href = {"index.html": "./ne/", "products.html": "./ne/products.html", "legal.html": "./ne/legal.html"}[f]
    en_href = {"index.html": "../", "products.html": "../products.html", "legal.html": "../legal.html"}[f]
    en = sub(en, '\n  </nav>', '\n  </nav>\n  ' + lang_link(ne_href, 'नेपाली', 'ne'), 1, f)
    ne = sub(ne, '\n  </nav>', '\n  </nav>\n  ' + lang_link(en_href, 'English', 'en'), 1, f)
    leftovers = [w for w in ("What we trade", "Ask for a price", "Registered firm", "Policies", "Skip to content") if w in re.sub(r'<head>.*?</head>', '', ne, flags=re.S)]
    assert not leftovers, (f, leftovers)
    open(f, "w", encoding="utf-8", newline="").write(en)
    open(os.path.join("ne", f), "w", encoding="utf-8", newline="").write(ne)
    print("ok", f, "->", "ne/" + f)
