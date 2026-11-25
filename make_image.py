#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Render the 25 November 2026 world-news front page.

Editorial layout: three lead stories with summaries and icons, twelve mid-size
regional stories, a wire-style briefs column, a schematic world map, a
'day in numbers' panel and a date-check box. All stories are from reporting
published on 25 Nov 2026; see SOURCES.txt. No clock, no network, no randomness.
"""
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = "#f5f1e6"
INK = "#14171c"
MUTED = "#5d636c"
RULE = "#bcb7a9"
WHITE = "#ffffff"

REG = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
)
BOLD = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
)


@lru_cache(maxsize=None)
def _path(bold):
    for p in (BOLD if bold else REG):
        try:
            with open(p, "rb"):
                return p
        except OSError:
            continue
    return None


@lru_cache(maxsize=128)
def font(size, bold=False):
    p = _path(bold)
    return ImageFont.truetype(p, size) if p else ImageFont.load_default(size=size)


def fit(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textbbox((0, 0), trial, font=fnt)[2] <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def writes(draw, xy, text, fnt, fill, width, lh=None):
    x, y = xy
    lh = lh or (fnt.size + 3)
    for i, line in enumerate(fit(draw, text, fnt, width)[:4]):
        draw.text((x, y + i * lh), line, font=fnt, fill=fill)
    return y + len(fit(draw, text, fnt, width)[:4]) * lh


def badge(draw, x, y, label, color):
    f = font(10, True)
    w = draw.textbbox((0, 0), label, font=f)[2] + 10
    draw.rectangle([x, y, x + w, y + 16], fill=color)
    draw.text((x + 5, y + 2), label, font=f, fill=WHITE)
    return w


LEADS = [
    {
        "kicker": "US JUSTICE", "color": "#1d4ed8", "tag": "VERDICT",
        "title": "Huawei guilty in New York fraud trial",
        "summary": "A jury finds bank fraud, money laundering and trade-secret theft in a case running since 2018.",
        "source": "Reuters · The World.fyi", "icon": "gavel",
    },
    {
        "kicker": "GULF / IRAN", "color": "#b45309", "tag": "ONGOING",
        "title": "Fourth tanker hits Hormuz mine",
        "summary": "Iran sets seven conditions for talks; Qatar urges restraint as the standoff shifts to maritime closure.",
        "source": "Reuters · World Watch", "icon": "ship",
    },
    {
        "kicker": "CHINA / SPACE", "color": "#047857", "tag": "CONFIRMED",
        "title": "Shenzhou-24 carries first foreign crewmate",
        "summary": "A Pakistani pilot joins two Chinese astronauts bound for Tiangong; launch called a complete success.",
        "source": "Xinhua", "icon": "rocket",
    },
]

MID = [
    ("EUROPE / WAR", "#b91c1c", [
        ("Russian war deaths near 500,000", "Leaked Russian figures reshape the war's mortality picture."),
        ("Ukraine confirms Baltic ship strike", "Norway urges caution after the Gulf of Finland attack."),
    ]),
    ("EUROPE / POLITICS", "#b91c1c", [
        ("Berlin poll: 53% oppose Ukraine aid", "Up from 39% a year ago, a Koerber Stiftung survey finds."),
        ("France sends Sarkozy case to trial", "Pre-trial hearing is set for 1 April 2027."),
    ]),
    ("MIDDLE EAST", "#b45309", [
        ("Houthi strike wounds 11 in Riyadh", "Second attack in six days on the PIF tower."),
        ("Israeli strikes kill six in Gaza", "Medics report two police among the dead."),
    ]),
    ("AFRICA", "#047857", [
        ("Nigeria okays 29.2tn-naira plan", "The senate approves borrowing as the 2026 budget is revised."),
        ("Senegal restored as AFCON winners", "An appeal succeeds at the sport's highest court."),
    ]),
    ("ASIA", "#6d28d9", [
        ("ICJ rules Myanmar genocide on Rohingya", "The court holds a state directly responsible for the first time."),
        ("Korea births up 12.2% in September", "25,113 babies, the fastest nine-month gain on record."),
    ]),
    ("AMERICAS", "#1d4ed8", [
        ("Colombia bomb wounds 23", "Prosecutors examine whether FARC-EMC was behind it."),
        ("Trump threatens to double Mexico tariffs", "A migrant caravan of more than 1,000 is cited."),
    ]),
]

BRIEFS = [
    "Cartagena gunmen hold supermarket hostages",
    "WHO asks US to lift Cuba fuel blockade",
    "Iowa to detonate unstable bomb chemicals",
    "Two arrested at William and Kate's home",
    "Sweden votes on Kristersson's future",
    "Houthis 60 km from Aden; government holds",
    "Trump's $3.8bn Israel aid cut in doubt",
    "Turkish party founder quits in fund probe",
    "South Sudan summons four ambassadors",
    "JNIM jihadists threaten Mali's Tonka",
    "Ruto adds 5bn shillings to Hustler Fund",
    "Ethiopia offers Sudan dialogue venue",
    "Xi probes Shanghai boss Chen Jining",
    "China extends minerals pause to Jan 2027",
    "Indonesia factory fire death toll hits 26",
    "Australia and Solomon Islands sign pact",
]

NUMBERS = [
    ("~500,000", "war deaths, Russian data"),
    ("29.2tn", "naira in Nigeria's plan"),
    ("25,113", "Korean births in September"),
    ("11", "hurt in Riyadh strike"),
]

MAP_PINS = [
    ("AMERICAS", 1, "#1d4ed8", 120, 300),
    ("EUROPE", 2, "#b91c1c", 430, 210),
    ("M. EAST", 3, "#b45309", 600, 400),
    ("AFRICA", 4, "#047857", 470, 560),
    ("ASIA", 5, "#6d28d9", 740, 300),
    ("OCEANIA", 6, "#0891b2", 700, 620),
]


def icon(draw, kind, x, y, color):
    if kind == "gavel":
        draw.polygon([(x, y + 12), (x + 30, y), (x + 42, y + 8), (x + 12, y + 20)], fill=color)
        draw.rectangle([x + 6, y + 22, x + 12, y + 52], fill=color)
        draw.rectangle([x, y + 52, x + 22, y + 58], fill=color)
    elif kind == "ship":
        draw.polygon([(x, y + 24), (x + 56, y + 24), (x + 46, y + 42), (x + 10, y + 42)], fill=color)
        draw.rectangle([x + 22, y + 8, x + 28, y + 24], fill=color)
        draw.rectangle([x + 30, y + 14, x + 48, y + 24], fill=color)
        for dx in (0, 18, 36):
            draw.line([(x + dx, y + 50), (x + dx + 12, y + 50)], fill=color, width=2)
    elif kind == "rocket":
        draw.polygon([(x + 16, y), (x + 28, y + 20), (x + 28, y + 44), (x + 4, y + 44), (x + 4, y + 20)], fill=color)
        draw.ellipse([x + 10, y + 18, x + 22, y + 30], fill="#f5f1e6")
        draw.polygon([(x + 8, y + 44), (x + 24, y + 44), (x + 16, y + 62)], fill="#fbbf24")


def lead_card(draw, x, y, w, h, story):
    draw.rectangle([x, y, x + w, y + h], fill=WHITE, outline=RULE, width=1)
    draw.rectangle([x + 1, y + 1, x + w - 1, y + 25], fill=story["color"])
    draw.text((x + 9, y + 5), story["kicker"], font=font(13, True), fill=WHITE)
    bw = badge(draw, x + w - 8 - (draw.textbbox((0, 0), story["tag"], font=font(10, True))[2] + 10), y + 5, story["tag"], INK)
    icon(draw, story["icon"], x + 14, y + 36, story["color"])
    ty = writes(draw, (x + 92, y + 36), story["title"], font(19, True), INK, w - 104, 22)
    ty = writes(draw, (x + 14, max(ty + 8, y + 104)), story["summary"], font(13), "#3d434c", w - 28, 16)
    draw.line([x + 14, y + h - 28, x + w - 14, y + h - 28], fill=RULE)
    draw.text((x + 14, y + h - 23), story["source"], font=font(11, True), fill=MUTED)


def mid_card(draw, x, y, w, h, region, color, items):
    draw.rectangle([x, y, x + w, y + h], fill=WHITE, outline=RULE, width=1)
    draw.rectangle([x + 1, y + 1, x + w - 1, y + 23], fill=color)
    draw.text((x + 8, y + 4), region, font=font(13, True), fill=WHITE)
    yy = y + 29
    for i, (head, sub) in enumerate(items):
        draw.ellipse([x + 8, yy + 4, x + 14, yy + 10], fill=color)
        yy = writes(draw, (x + 20, yy), head, font(14, True), INK, w - 28, 16) + 1
        yy = writes(draw, (x + 20, yy), sub, font(11), MUTED, w - 28, 13) + 4


def draw_map(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill="#e9e5d9", outline=RULE)
    # deliberately schematic continents, not a geographic claim
    land = [
        [(20, 20), (80, 16), (92, 52), (70, 88), (38, 74)],
        [(130, 18), (194, 14), (216, 46), (180, 66), (142, 54)],
        [(164, 60), (200, 56), (194, 100), (168, 96)],
        [(214, 32), (296, 26), (324, 70), (274, 104), (226, 86)],
        [(288, 74), (322, 70), (330, 100), (296, 102)],
    ]
    for poly in land:
        draw.polygon([(x + px, y + py) for px, py in poly], fill="#d4cfbf")
    draw.text((x + 8, y + 6), "WHERE IT HAPPENED", font=font(11, True), fill=INK)
    for label, n, color, px, py in MAP_PINS:
        cx, cy = x + px * w // 1000, y + py * h // 1000
        draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=color, outline=WHITE, width=2)
        draw.text((cx + 9, cy - 6), label, font=font(10, True), fill=INK)


def draw_numbers(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=INK)
    draw.text((x + 10, y + 6), "THE DAY IN NUMBERS", font=font(14, True), fill=PAPER)
    cw = (w - 16) // 2
    for i, (big, label) in enumerate(NUMBERS):
        col, row = i % 2, i // 2
        bx, by = x + 8 + col * cw, y + 26 + row * 36
        draw.text((bx, by), big, font=font(20, True), fill="#fbbf24")
        draw.text((bx, by + 21), label, font=font(10), fill="#d4d4d8")


def render(path="entry.png"):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 8], fill=INK)

    d.text((22, 18), "Wednesday 25 November 2026", font=font(45, True), fill=INK)
    d.text((24, 69), "THE WORLD ON ONE PAGE  ·  3 LEADS  ·  12 REGIONAL  ·  16 BRIEFS", font=font(15, True), fill=MUTED)
    timeline = "AS REPORTED (UTC): 00:00 Kyodo  ·  00:17 Xinhua  ·  04:30 Yonhap  ·  05:15 World.fyi (46 newsrooms)"
    d.text((24, 90), timeline, font=font(12), fill=MUTED)
    d.line([22, 108, W - 22, 108], fill=INK, width=2)

    gap, cw = 10, (W - 44 - 20) // 3
    for i, story in enumerate(LEADS):
        lead_card(d, 22 + i * (cw + gap), 116, cw, 216, story)

    for i, (region, color, items) in enumerate(MID):
        col, row = i % 3, i // 3
        mid_card(d, 22 + col * (cw + gap), 342 + row * 146, cw, 140, region, color, items)

    d.rectangle([22, 642, 654, 862], fill=WHITE, outline=RULE)
    d.rectangle([23, 643, 653, 667], fill=INK)
    d.text((30, 646), "THE WIRE  ·  16 MORE STORIES", font=font(13, True), fill=PAPER)
    for i, item in enumerate(BRIEFS):
        col, row = i % 2, i // 2
        x, y = 30 + col * 310, 676 + row * 23
        d.text((x, y), f"{i+1:02d}", font=font(11, True), fill="#a03a2b")
        d.text((x + 22, y), item, font=font(12), fill=INK)

    draw_map(d, 666, 642, 336, 108)
    draw_numbers(d, 666, 758, 336, 104)

    d.rectangle([22, 884, W - 22, 928], fill="#fff8f0", outline="#a03a2b", width=2)
    d.text((30, 899), "DATE CHECK", font=font(13, True), fill="#a03a2b")
    d.text((120, 899), "All 31 stories verified from 25 Nov 2026 reporting; earlier-day items excluded.",
           font=font(12), fill=INK)
    d.text((22, 946), "Reuters · AFP · Xinhua · Kyodo · Yonhap · World Watch · The World.fyi · AfricaFrontPage · Naija News",
           font=font(11), fill=MUTED)
    d.text((22, 966), "Compiled for make.fun — a careful picture editor's page for one day", font=font(11), fill=MUTED)
    im.save(path, "PNG", optimize=True)
    return path


if __name__ == "__main__":
    render("entry.png")
