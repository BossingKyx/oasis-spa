"""Official Oasis on the Go Spa service catalogue.

Each priced variant (duration tier / Full Body vs Deep Tissue / Female vs Male)
is one bookable Service, so booking totals and sales use the real prices.
load_services() upserts the whole menu and deactivates anything not in it.
"""
from decimal import Decimal

from .models import Service

# Indulgence massages with 60 / 90 / 120-minute tiers.
INDULGENCE_TIERS = {
    'Swedish':                            {60: 450, 90: 650, 120: 850},
    'Combination':                        {60: 500, 90: 700, 120: 900},
    'Shiatsu':                            {60: 550, 90: 750, 120: 950},
    'Thai':                               {60: 750, 90: 1000, 120: 1200},
    'Deep Tissue':                        {60: 600, 90: 800, 120: 1000},
    'Aromatherapy':                       {60: 500, 90: 700, 120: 900},
    'Hot Stone':                          {60: 550, 90: 750, 120: 950},
    'Ventosa (Traditional)':              {60: 600, 90: 800, 120: 1000},
    'Ventosa (Running)':                  {60: 850, 90: 1100, 120: 1350},
    'Lymphatic':                          {60: 700, 90: 950, 120: 1200},
    'Pre Natal / Lactation / Post Natal': {60: 500, 90: 700, 120: 900},
}
INDULGENCE_SINGLE = [   # (name, duration, price)
    ('Foot Reflexology', 60, 500),
    ('Kiddie Massage', 30, 300),
    ('Oasis Signature Bliss (Therapeutic)', 60, 650),
]

# 90-minute Enhanced Body Massage: (Full Body, Deep Tissue)
ENHANCED = {
    'Foot Massage':                  (700, 900),
    'Hot Pack':                      (700, 900),
    'Hot Stones':                    (750, 950),
    'Ventosa':                       (750, 950),
    'Body Scrub':                    (800, 1000),
    'Body Bleaching and Body Scrub': (1300, 1500),
    'Herbal Ball':                   (750, 950),
}

BOOSTERS = [   # (name, duration, price)
    ('Body Scrub', 45, 500),
    ('Body Whitening - Whole Body', 60, 500),
    ('Body Whitening - Groin/Elbow/Knee', 30, 200),
    ('Body Whitening - Underarm', 20, 250),
    ('Body Whitening - Foot', 20, 150),
    ('Foot Spa', 45, 300),
    ('Foot Scrub', 30, 150),
    ('Ear Candling', 30, 200),
]

# Waxing: (Female, Male)
WAXING = {
    'Upper/Lower Lip': (250, 300),
    'Eyebrow':         (300, 350),
    'Underarm':        (250, 300),
    'Half Legs':       (400, 800),
    'Full Legs':       (800, 1000),
    'Brazilian':       (800, 800),
    'Bikini':          (650, 700),
    'Back':            (400, 600),
    'Whole Body':      (2000, 2500),
}

SPECIALTY = [   # (name, duration, price)
    ('Healing Haplos w/ Luya + Foot Reflex (Full Body, 90 min)', 90, 900),
    ('Healing Haplos w/ Luya + Foot Reflex (Deep Tissue, 90 min)', 90, 1100),
    ('Focus Massage (per area, 30 min)', 30, 250),
]


def build_catalog():
    """Return a flat list of (category, name, duration, price)."""
    items = []
    for base, tiers in INDULGENCE_TIERS.items():
        for dur, price in tiers.items():
            items.append(('Indulgence Massage', f'{base} ({dur} min)', dur, price))
    for name, dur, price in INDULGENCE_SINGLE:
        items.append(('Indulgence Massage', f'{name} ({dur} min)', dur, price))
    for item, (fb, dt) in ENHANCED.items():
        items.append(('Enhanced Body Massage (90 min)',
                      f'Enhanced: {item} (Full Body, 90 min)', 90, fb))
        items.append(('Enhanced Body Massage (90 min)',
                      f'Enhanced: {item} (Deep Tissue, 90 min)', 90, dt))
    for name, dur, price in BOOSTERS:
        items.append(('Renewal Boosters', name, dur, price))
    for item, (female, male) in WAXING.items():
        items.append(('Hair-Free Solutions', f'{item} Wax (Female)', 30, female))
        items.append(('Hair-Free Solutions', f'{item} Wax (Male)', 30, male))
    for name, dur, price in SPECIALTY:
        items.append(('Specialty Massage', name, dur, price))
    return items


def load_services():
    """Upsert the full catalogue; deactivate anything not on it. Returns {name: Service}."""
    names = []
    for category, name, duration, price in build_catalog():
        Service.objects.update_or_create(
            name=name,
            defaults={'category': category, 'duration_minutes': duration,
                      'price': Decimal(str(price)), 'is_active': True})
        names.append(name)
    # Retire demo/old services that aren't on the real menu (keep for history).
    Service.objects.exclude(name__in=names).update(is_active=False)
    return {s.name: s for s in Service.objects.filter(name__in=names)}
