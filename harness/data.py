"""Mock data for the bootcamp: a small fictional webshop called "CoolShop".

All tools in harness/tools/ read from this file. Using mock data instead of
real APIs means: no extra accounts, no rate limits, nothing can break, and
your traces are easy to compare with your neighbour's.

Feel free to read through it. Knowing what data exists makes it easier to
come up with good test questions for your agent.
"""

# --- Products ----------------------------------------------------------------
# Products across a few categories. Each product is a plain dict.
PRODUCTS = [
    {
        "id": "P-1001",
        "name": "Aurora Book Pro 14",
        "brand": "Aurora",
        "category": "laptops",
        "price": 1299.00,
        "stock": 23,
        "rating": 4.6,
        "specs": {"screen": "14 inch", "ram": "16 GB", "storage": "512 GB SSD", "weight": "1.4 kg"},
        "highlight": "Light and powerful all-rounder for work and study.",
    },
    {
        "id": "P-1002",
        "name": "Aurora Book Air 13",
        "brand": "Aurora",
        "category": "laptops",
        "price": 949.00,
        "stock": 41,
        "rating": 4.4,
        "specs": {"screen": "13 inch", "ram": "8 GB", "storage": "256 GB SSD", "weight": "1.1 kg"},
        "highlight": "Ultra-portable laptop for browsing, mail and documents.",
    },
    {
        "id": "P-1003",
        "name": "Titan GX Gaming 17",
        "brand": "Titan",
        "category": "laptops",
        "price": 1899.00,
        "stock": 7,
        "rating": 4.7,
        "specs": {"screen": "17 inch 165Hz", "ram": "32 GB", "storage": "1 TB SSD", "weight": "2.8 kg"},
        "highlight": "Heavy-duty gaming laptop that runs every title on ultra.",
    },
    {
        "id": "P-2001",
        "name": "Pixelphone 15",
        "brand": "Pixelphone",
        "category": "smartphones",
        "price": 799.00,
        "stock": 112,
        "rating": 4.5,
        "specs": {"screen": "6.2 inch OLED", "storage": "128 GB", "battery": "4700 mAh", "camera": "50 MP"},
        "highlight": "Great camera and clean software, solid mid-range choice.",
    },
    {
        "id": "P-2002",
        "name": "Pixelphone 15 Ultra",
        "brand": "Pixelphone",
        "category": "smartphones",
        "price": 1199.00,
        "stock": 38,
        "rating": 4.8,
        "specs": {"screen": "6.8 inch OLED 120Hz", "storage": "256 GB", "battery": "5200 mAh", "camera": "200 MP"},
        "highlight": "The flagship: best display and camera in our range.",
    },
    {
        "id": "P-3001",
        "name": "SoundWave ANC 700",
        "brand": "SoundWave",
        "category": "headphones",
        "price": 279.00,
        "stock": 64,
        "rating": 4.7,
        "specs": {"type": "over-ear", "noise_cancelling": "yes", "battery": "35 hours", "weight": "254 g"},
        "highlight": "Top-tier noise cancelling for commuters and open offices.",
    },
    {
        "id": "P-3002",
        "name": "SoundWave Buds Mini",
        "brand": "SoundWave",
        "category": "headphones",
        "price": 89.00,
        "stock": 203,
        "rating": 4.2,
        "specs": {"type": "in-ear", "noise_cancelling": "no", "battery": "6 + 18 hours (case)", "weight": "4 g"},
        "highlight": "Affordable earbuds for sports and everyday listening.",
    },
    {
        "id": "P-4001",
        "name": "FreshSpin 8000 Washing Machine",
        "brand": "FreshSpin",
        "category": "washing machines",
        "price": 649.00,
        "stock": 15,
        "rating": 4.6,
        "specs": {"capacity": "8 kg", "energy_label": "A", "noise": "48 dB", "rpm": "1400"},
        "highlight": "Quiet and efficient, ideal for families of 3-4 people.",
    },
    {
        "id": "P-4002",
        "name": "FreshSpin 6000 Compact",
        "brand": "FreshSpin",
        "category": "washing machines",
        "price": 449.00,
        "stock": 0,
        "rating": 4.3,
        "specs": {"capacity": "6 kg", "energy_label": "B", "noise": "52 dB", "rpm": "1200"},
        "highlight": "Compact machine for singles or couples with less space.",
    },
    {
        "id": "P-4003",
        "name": "AquaCare EcoWash 900",
        "brand": "AquaCare",
        "category": "washing machines",
        "price": 729.00,
        "stock": 18,
        "rating": 4.7,
        "specs": {"capacity": "9 kg", "energy_label": "A", "noise": "47 dB", "rpm": "1400"},
        "highlight": "Energy-efficient family washer with a quiet night program.",
    },
    {
        "id": "P-4004",
        "name": "HomeFlow MiniWash 500",
        "brand": "HomeFlow",
        "category": "washing machines",
        "price": 389.00,
        "stock": 26,
        "rating": 4.1,
        "specs": {"capacity": "5 kg", "energy_label": "C", "noise": "55 dB", "rpm": "1000"},
        "highlight": "Space-saving washer designed for studios and small households.",
    },
    {
        "id": "P-4005",
        "name": "NordClean SteamPro 10",
        "brand": "NordClean",
        "category": "washing machines",
        "price": 899.00,
        "stock": 9,
        "rating": 4.8,
        "specs": {"capacity": "10 kg", "energy_label": "A", "noise": "46 dB", "rpm": "1600"},
        "highlight": "Large-capacity washer with steam cleaning for busy families.",
    },
    {
        "id": "P-4006",
        "name": "PureDrum Daily 700",
        "brand": "PureDrum",
        "category": "washing machines",
        "price": 519.00,
        "stock": 34,
        "rating": 4.4,
        "specs": {"capacity": "7 kg", "energy_label": "B", "noise": "50 dB", "rpm": "1400"},
        "highlight": "Reliable everyday washer with quick cycles for smaller loads.",
    },
    {
        "id": "P-4007",
        "name": "AquaCare SilentWash 800",
        "brand": "AquaCare",
        "category": "washing machines",
        "price": 679.00,
        "stock": 0,
        "rating": 4.5,
        "specs": {"capacity": "8 kg", "energy_label": "A", "noise": "44 dB", "rpm": "1400"},
        "highlight": "Extra-quiet washing for open-plan homes and nighttime cycles.",
    },
    {
        "id": "P-4008",
        "name": "MaxLoad Active 12",
        "brand": "MaxLoad",
        "category": "washing machines",
        "price": 999.00,
        "stock": 5,
        "rating": 4.6,
        "specs": {"capacity": "12 kg", "energy_label": "A", "noise": "49 dB", "rpm": "1600"},
        "highlight": "High-capacity machine for large households and bulky laundry.",
    },
    {
        "id": "P-5001",
        "name": "BeanBoss Barista Deluxe",
        "brand": "BeanBoss",
        "category": "coffee machines",
        "price": 549.00,
        "stock": 29,
        "rating": 4.8,
        "specs": {"type": "fully automatic", "grinder": "ceramic", "milk_frother": "yes", "pressure": "15 bar"},
        "highlight": "Fresh beans to cappuccino in one touch.",
    },
    {
        "id": "P-5002",
        "name": "BeanBoss Filter Classic",
        "brand": "BeanBoss",
        "category": "coffee machines",
        "price": 79.00,
        "stock": 88,
        "rating": 4.1,
        "specs": {"type": "filter", "capacity": "1.2 L", "milk_frother": "no", "timer": "yes"},
        "highlight": "Simple, reliable filter coffee for the whole table.",
    },
    {
        "id": "P-6001",
        "name": "ViewMax 27 QHD Monitor",
        "brand": "ViewMax",
        "category": "monitors",
        "price": 329.00,
        "stock": 54,
        "rating": 4.5,
        "specs": {"screen": "27 inch QHD", "refresh_rate": "144Hz", "panel": "IPS", "ports": "2x HDMI, 1x DP"},
        "highlight": "Sharp, fast monitor for both office work and gaming.",
    },
]

# --- Orders --------------------------------------------------------------------
# A few customer orders in different states, handy for testing how your agent
# handles happy paths AND problem cases (delays, returns).
ORDERS = {
    "ORD-1001": {
        "customer": "Sanne de Vries",
        "items": ["Aurora Book Pro 14"],
        "status": "delivered",
        "ordered_on": "2026-06-24",
        "delivered_on": "2026-06-26",
        "note": "Signed for at the front door.",
    },
    "ORD-1002": {
        "customer": "Mo El Idrissi",
        "items": ["SoundWave ANC 700", "ViewMax 27 QHD Monitor"],
        "status": "shipped",
        "ordered_on": "2026-06-30",
        "expected_delivery": "2026-07-03",
        "note": "Package is with the delivery partner.",
    },
    "ORD-1003": {
        "customer": "Emma Janssen",
        "items": ["FreshSpin 8000 Washing Machine"],
        "status": "delayed",
        "ordered_on": "2026-06-28",
        "expected_delivery": "2026-07-08",
        "note": "Delivery delayed: the installation team is fully booked this week.",
    },
    "ORD-1004": {
        "customer": "Luuk Bakker",
        "items": ["Pixelphone 15 Ultra"],
        "status": "processing",
        "ordered_on": "2026-07-01",
        "expected_delivery": "2026-07-04",
        "note": "Payment received, order is being picked in the warehouse.",
    },
    "ORD-1005": {
        "customer": "Fatima Yilmaz",
        "items": ["BeanBoss Barista Deluxe"],
        "status": "return received",
        "ordered_on": "2026-06-10",
        "note": "Return received on 2026-06-20. Refund will be processed within 5 working days.",
    },
    "ORD-1006": {
        "customer": "Noah de Boer",
        "items": ["AquaCare EcoWash 900"],
        "status": "delivered",
        "ordered_on": "2026-07-02",
        "delivered_on": "2026-07-05",
        "note": "Signed for at the front door.",
    },
}

# --- FAQ / store policies -------------------------------------------------------
# Each entry has keywords used by the search_faq tool for simple matching.
FAQ = [
    {
        "question": "What is the return policy?",
        "answer": "You can return any product within 30 days of delivery, free of charge. "
        "The product must be complete and undamaged. Refunds are processed within 5 working days.",
        "keywords": ["return", "returns", "refund", "money back", "send back", "policy"],
    },
    {
        "question": "How long does delivery take?",
        "answer": "Ordered before 23:59? Delivered the next day, free of charge. "
        "Large appliances (like washing machines) are delivered within 3 working days by appointment.",
        "keywords": ["delivery", "shipping", "how long", "when", "arrive", "next day"],
    },
    {
        "question": "Which payment methods are accepted?",
        "answer": "We accept iDEAL, credit card (Visa/Mastercard), PayPal, Apple Pay and gift cards. "
        "Payment in installments is available for orders above €250.",
        "keywords": ["payment", "pay", "ideal", "credit card", "paypal", "installments"],
    },
    {
        "question": "What warranty do I get?",
        "answer": "All products come with a minimum 2-year warranty. Defects within the warranty "
        "period are repaired or replaced for free. Keep your order number as proof of purchase.",
        "keywords": ["warranty", "guarantee", "broken", "defect", "repair", "replace"],
    },
    {
        "question": "Can I pick up my order at a store?",
        "answer": "Yes! Choose 'store pickup' at checkout. Your order is ready within 2 hours "
        "and is held for 7 days. Bring your order confirmation and ID.",
        "keywords": ["pickup", "pick up", "store", "collect", "collection point"],
    },
    {
        "question": "Does the washing machine delivery include installation?",
        "answer": "Yes, large appliances are installed for free: we connect the machine, test it, "
        "and take your old appliance and all packaging with us.",
        "keywords": ["installation", "install", "connect", "old appliance", "washing machine delivery"],
    },
    {
        "question": "How do I cancel an order?",
        "answer": "Orders with status 'processing' can be cancelled for free via customer service. "
        "Once an order is 'shipped' it can no longer be cancelled, but you can refuse the package "
        "at the door or return it within 30 days.",
        "keywords": ["cancel", "cancellation", "stop order", "change order"],
    },
    {
        "question": "Do prices include VAT?",
        "answer": "Yes, all prices on the website include 21% VAT. Business customers can download "
        "a VAT invoice from their account page.",
        "keywords": ["vat", "tax", "btw", "invoice", "business", "price"],
    },
]
