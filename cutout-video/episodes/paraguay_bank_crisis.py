"""Episode: Dom Talks Politics - Paraguay's Bank Crisis (narration 11:00)."""
from kit import *

def build():
    S = []
    dom_talk = [(0.0, 3.0), (3.8, 6.74)]
    # --- intro
    S.append(Scene(0.0, "studio", [
        P(art.desk_mic(), 1180, 760, t=0.0, enter="none"),
        C("dom", W / 2, 830, t=0.0, talk=dom_talk, scale=1.45, a={"enter": "none"}),
        P(art.desk(), W / 2, 1090, t=0.0, enter="none"),
        L("DOM TALKS POLITICS", W / 2, 130, t=0.6, size=84, rot=-2, bgc=(255, 230, 120)),
    ]))
    # --- title card: words land on the beat, matching assets arrive, gavel closes it
    S.append(Scene(3.8, "title", [
        L("TODAY'S EPISODE", W / 2, 110, t=3.85, size=54, rot=-2, bgc=(255, 255, 255)),
        L("PARAGUAY'S", W / 2, 270, t=5.14, size=118, rot=-3, bgc=(255, 252, 235), enter="slam"),
        P(art.flag_py(420, 266), 330, 480, t=5.2, anchor="c", enter="slideL", idle="sway"),
        L("BANK", W / 2, 475, t=5.92, size=128, rot=2, bgc=(255, 220, 90), enter="slam"),
        P(art.building("bank", 480, 420, label="ueno"), 1680, 930, t=5.96, enter="slideR", out=6.18),
        P(art.building("bank", 480, 420, label="ueno"), 1680, 930, t=6.18, enter="none", idle="shake"),
        L("CRISIS", W / 2 - 60, 690, t=6.18, size=138, rot=-2, bgc=(225, 45, 45), fg=(255, 255, 255), enter="slam"),
        P(art.sound_block(), 1230, 990, t=6.4, anchor="c", enter="pop"),
        gavel_actor(1230, 960, 7.05),
    ], zoom=0.05))
    # --- cold open
    S.append(Scene(7.75, "street", [
        P(art.vault(380, 380), 560, 1000, t=7.5),
        P(art.ice_block(500, 460), 560, 1040, t=8.2, enter="drop"),
        L("FROZEN!", 560, 360, t=8.4, size=90, rot=-6, bgc=(200, 235, 255)),
        *crowd(800, 1100, GROUND, 5, scale=0.62, t=9.0, eyes="worried", mouth="frown"),
        L("3 MILLION PEOPLE", 1080, 240, t=10.0, size=70, rot=2),
        C("pena", 1380, GROUND, t=12.0, scale=0.95, eyes="worried",
          a={"fall": 13.0, "idle": "none"}),
        L("...AND A PRESIDENT", 1650, 330, t=12.6, size=52, rot=-3, bgc=(255, 140, 120)),
    ]))
    S.append(Scene(14.4, "street_far", [
        P(art.tv(art.char("pena", mouth="closed")), 620, 560, t=14.5, anchor="c"),
        L("PRESIDENT PEÑA RESIGNS\n(BY VIDEO)", 620, 160, t=15.5, size=58, rot=-2),
        P(art.hand_stop(), 1450, 440, t=20.6, anchor="c", idle="shake"),
        P(art.building("congress", 620, 480, label="CONGRESS"), 1450, 1000, t=19.8),
        L("NOT SO FAST!", 1450, 130, t=21.0, size=70, rot=4, bgc=(255, 120, 100)),
    ]))
    S.append(Scene(23.2, "washington", [
        P(art.building("capitol", 900, 420), W / 2, 700, t=23.2, enter="none"),
        C("pena", 760, GROUND, t=23.3, arms="point"),
        C("trump", 1160, GROUND, t=23.5, flip=True, arms="point", mouth="smile"),
        L("TRUMP'S CLOSE PARTNER", W / 2, 140, t=24.2, size=66, rot=-2),
        L("2 WEEKS EARLIER:\nMEETING THE US TREASURY", 420, 400, t=27.5, size=48, rot=3, bgc=(220, 240, 255)),
    ]))
    S.append(Scene(31.9, "paper_green", [
        P(art.phone(1.1), 420, 960, t=32.0),
        *[P(art.coin(1.2), 260 + i * 90, 380 - (i % 2) * 60, t=32.6 + i * 0.12, anchor="c", idle="bob",
            phase=i * 0.3) for i in range(5)],
        P(art.arrow(360, 140), 900, 600, t=33.6, anchor="c"),
        P(art.building("congress", 620, 480, label="GOVERNMENT"), 1450, 920, t=34.0,
          fall=35.4),
        P(art.question(220), 1450, 300, t=35.8, anchor="c", idle="bob"),
    ]))
    S.append(Scene(37.1, "studio", [
        C("dom", 760, 960, t=37.1, talk=[(37.1, 38.84)], scale=1.35, hold="magnifier",
          a={"enter": "none"}),
        L("LET'S FOLLOW\nTHE FOOTNOTES", 1350, 400, t=37.6, size=80, rot=3, bgc=(255, 230, 120)),
    ]))
    # --- part 1
    S.append(part_card(39.0, 1, "THE BANK", "paper_red"))
    S.append(Scene(40.0, "map", [
        P(art.map_sprite(), W / 2 - 100, 1060, t=40.0, enter="none"),
        P(art.paraguay_sprite(), W / 2 - 100, 1060, t=40.6, enter="pop", idle="pulse"),
        L("LANDLOCKED", 1650, 300, t=41.5, size=56, rot=4),
        L("6.5 MILLION\nPEOPLE", 1690, 760, t=43.4, size=60, rot=-3, bgc=(255, 230, 120)),
    ]))
    S.append(Scene(48.5, "street_py_far", [
        P(art.building("bank", 760, 560, label="ueno"), 720, 1000, t=48.6),
        L("SPELT WITH A\nLOWERCASE 'u'", 1420, 330, t=50.8, size=56, rot=3),
        L("ROOTS: A FINANCE\nCOMPANY, FOUNDED 1976", 1420, 640, t=53.8, size=52, rot=-2, bgc=(240, 220, 180)),
    ]))
    S.append(Scene(57.9, "office_in", [
        C("exec", 520, GROUND, t=58.0, hold="briefcase"),
        C("exec", 800, GROUND, t=58.2, glasses=True, col=(60, 40, 40), hair="receding", hair_col=(120, 120, 120), build=1.25),
        L("GRUPO VÁZQUEZ BUYS IT (2021)", 960, 150, t=58.4, size=62, rot=-2),
        L("ONE OF PARAGUAY'S BIGGEST\nBUSINESS CONGLOMERATES", 960, 320, t=60.5, size=44, rot=1, out=64.6,
          bgc=(255, 255, 255)),
        P(art.phone(0.8), 1440, 960, t=64.6),
        L("REBRANDED: ueno", 1440, 360, t=65.2, size=56, rot=4, bgc=(160, 230, 210)),
        L("ALL IN ON AN APP", 1440, 530, t=66.6, size=48, rot=-3, bgc=(255, 230, 120)),
    ]))
    S.append(Scene(69.0, "paper_blue", [
        P(art.phone(0.8, screen="app"), 960, 760, t=69.1),
        L("COMPARED TO NUBANK,\nMONZO & REVOLUT", 960, 200, t=70.0, size=56, rot=-2),
        P(art.phone(0.6, screen="brand", txt="NUBANK"), 520, 840, t=70.6, idle="bob"),
        P(art.phone(0.6, screen="brand", txt="MONZO"), 1400, 840, t=71.0, idle="bob"),
        P(art.phone(0.6, screen="brand", txt="REVOLUT"), 1660, 900, t=71.4, idle="bob"),
    ]))
    S.append(Scene(73.8, "street_far", [
        P(art.building("central", 600, 470, label="CENTRAL BANK"), 420, 1000, t=73.8),
        L("END OF 2023", W / 2, 170, t=74.3, size=64, rot=3),
        P(art.arrow(220, 100, (40, 120, 200)), 830, 720, t=76.0, anchor="c"),
        P(art.document("BANKING LICENCE", 4, 280, 340), 1060, 960, t=76.6, id="licence"),
        P(art.arrow(220, 100, (40, 120, 200)), 1290, 720, t=77.6, anchor="c"),
        P(art.building("bank", 520, 460, label="ueno"), 1640, 1000, t=78.0, id="ueno"),
        P(art.stamp("APPROVED", col=(30, 140, 60), size=56), 1060, 800, t=79.4, anchor="c", enter="slam",
          target="licence"),
        L("A FULL BANK LICENCE", W / 2, 345, t=79.9, size=56, rot=-2, bgc=(200, 240, 200)),
    ]))
    S.append(Scene(81.7, "office_in", [
        C("cbchief", 620, GROUND, t=81.8, a={"move": (88.6, 91.0, 1700, GROUND)}),
        L("CENTRAL BANK CHIEF", 620, 380, t=82.0, size=54, rot=-2, out=88.4),
        L("PREVIOUSLY PRESIDENT OF\nueno's FINANCE COMPANY", 1320, 300, t=84.4, size=50, rot=2,
          bgc=(255, 230, 120), out=88.4),
        L("\"RECUSED HIMSELF\nFROM EVERY DECISION\"", 1100, 260, t=88.6, size=54, rot=-2, out=93.0),
        *crowd(360, 1100, GROUND, 4, scale=0.66, t=93.2, eyes="angry", seed=40),
        *[P(art.question(130), 360 + i * 246, 420, t=93.6 + i * 0.15, anchor="c", idle="bob", phase=i * .4)
          for i in range(4)],
        L("CRITICS AREN'T\nCONVINCED", 1500, 300, t=93.8, size=58, rot=3),
    ]))
    # --- part 2
    S.append(part_card(95.9, 2, "THE BOOM", "paper_yellow"))
    S.append(Scene(98.1, "paper_green", [
        P(art.rocket_chart(), 640, 820, t=98.2, enter="slideL"),
        L("ASTONISHING SPEED", 640, 220, t=98.8, size=60, rot=-3),
        P(art.cart(), 1300, 950, t=100.6),
        P(art.gas_pump(), 1700, 950, t=101.0),
        L("UP TO 40% CASHBACK", 1500, 300, t=103.0, size=66, rot=3, bgc=(255, 230, 120)),
        *[P(art.coin(1.1), 1160 + i * 100, 500 + (i % 3) * 40, t=101.6 + i * 0.1, anchor="c", idle="bob",
            phase=i * .25) for i in range(7)],
    ]))
    S.append(Scene(107.0, "map", [
        P(art.fish((20, 150, 125), "ueno", 640, mouth=True), 640, 760, t=107.1, anchor="c",
          move=(110.0, 112.3, 900, 760)),
        P(art.fish((230, 140, 60), "VISIÓN", 340), 1360, 760, t=107.6, anchor="c", out=112.4, idle="bob"),
        L("2024: SWALLOWS ANOTHER LENDER", 960, 180, t=107.8, size=60, rot=-2),
        L("+1 MILLION CUSTOMERS", 1300, 960, t=112.4, size=68, rot=3, bgc=(255, 230, 120)),
    ]))
    S.append(Scene(113.9, "locker", [
        *[C("player", 380 + i * 300, GROUND, t=114.0 + i * 0.15, scale=1.0, vary=10 + i, hair_col=[(30, 20, 15), (90, 55, 25), (20, 20, 20), (60, 40, 20)][i],
            skin=["tan", "brown", "light", "tan"][i]) for i in range(4)],
        L("SPONSOR OF THE\nNATIONAL TEAM", 960, 200, t=114.4, size=62, rot=-2),
        C("exec", 1650, GROUND, t=118.6, scale=1.0, mouth="smile"),
        L("THE BOSS IN THE LOCKER ROOM", 1200, 420, t=119.4, size=46, rot=3, bgc=(255, 255, 255)),
    ]))
    S.append(Scene(121.4, "wallst", [
        P(art.bull(), 520, 960, t=121.5),
        L("WALL STREET", 520, 380, t=121.8, size=64, rot=-3, bgc=(255, 255, 255)),
        P(art.money_bag("$350M", 1.4), 1300, 940, t=123.4),
        L("$350 MILLION BOND", 1300, 300, t=124.0, size=66, rot=2, bgc=(255, 230, 120)),
        L("LED BY JPMORGAN &\nBANK OF AMERICA", 1300, 470, t=127.0, size=44, rot=-2),
    ]))
    S.append(Scene(129.5, "street_py", [
        *crowd(200, 1720, GROUND, 9, scale=0.6, t=129.6, hold="phone", seed=70, mouth="smile"),
        L("≈3 MILLION CUSTOMERS".replace("≈", "~"), 960, 180, t=130.4, size=70, rot=-2),
        L("~60% OF PARAGUAY'S ADULTS", 960, 370, t=133.0, size=60, rot=2, bgc=(255, 230, 120)),
    ]))
    S.append(Scene(136.7, "paper_purple", [
        P(art.phone(1.6, screen="icons"), 700, 1010, t=136.8),
        L("FIRST REAL BANK\nACCOUNT FOR MANY", 1400, 300, t=137.4, size=60, rot=3),
        L("ALL ON ONE\nPHONE APP", 1400, 620, t=141.6, size=66, rot=-3, bgc=(255, 230, 120)),
    ]))
    # --- part 3
    S.append(part_card(144.9, 3, "THE PUBLIC MONEY", "paper_blue"))
    S.append(Scene(147.2, "street_far", [
        P(art.building("congress", 560, 460, label="GOVERNMENT"), 380, 1000, t=147.3),
        P(art.building("bank", 560, 460, label="ueno"), 1540, 1000, t=147.5),
        P(art.arrow(300, 110, (240, 190, 60)), 960, 700, t=149.6, anchor="c"),
        *[P(art.cash_stack(0.8), 780 + i * 125, 560 + abs(i - 1.5) * 30, t=149.9 + i * 0.2, anchor="c",
            idle="bob", phase=i * .3, ok="cash") for i in range(4)],
        L("NOT JUST ORDINARY PEOPLE'S MONEY", 960, 140, t=148.0, size=56, rot=-2, out=150.0),
        L("THE GOVERNMENT'S TOO", 960, 140, t=150.0, size=64, rot=2, bgc=(255, 230, 120)),
    ]))
    S.append(Scene(152.7, "paper_yellow", [
        P(art.radio(), 520, 900, t=152.8, idle="shake"),
        L("ON THE RADIO: \"$800M+\nIN PUBLIC DEPOSITS\"", 520, 300, t=155.6, size=52, rot=-2),
        P(art.dam(), 1380, 920, t=161.2),
        L("ECONOMY MINISTRY: ~$850M", 1380, 230, t=161.6, size=54, rot=2, bgc=(255, 255, 255)),
        L("INCL. ITAIPÚ & YACYRETÁ DAMS", 1380, 400, t=166.0, size=44, rot=-2, bgc=(200, 235, 255)),
    ]))
    S.append(Scene(170.3, "street_py_far", [
        P(art.building("ips", 640, 480, label="IPS"), 560, 1000, t=170.3),
        L("SOCIAL SECURITY INSTITUTE", 560, 250, t=171.6, size=50, rot=-2),
        P(art.money_bag("$355M", 1.4), 1180, 960, t=176.4),
        L("RETIREMENT MONEY", 1300, 420, t=180.4, size=60, rot=3, bgc=(255, 230, 120)),
        C("pensioner", 1480, GROUND, t=180.6, scale=1.0, eyes="worried", a={"ok": "pair"}),
        C("granny", 1660, GROUND, t=180.9, scale=1.0, eyes="worried", flip=True, a={"ok": "pair"}),
    ]))
    S.append(Scene(182.5, "office_in", [
        C("finchief", 560, GROUND - 30, t=182.6),
        P(art.podium(), 560, 1010, t=182.6, enter="none"),
        L("IPS FINANCE CHIEF", 560, 330, t=183.0, size=50, rot=-2),
        L("~9% OF ITS\nWHOLE PORTFOLIO", 1350, 230, t=185.4, size=56, rot=2),
        L("\"AUDITS FOUND\nNO VIOLATIONS\"", 1350, 470, t=189.4, size=54, rot=-2, bgc=(200, 240, 200),
          out=192.5),
        P(art.risk_meter(), 1350, 760, t=192.6, anchor="c"),
        Actor(art.needle(150), 1350, 760 + 64, t=192.6, anchor="c", enter="pop", idle="none",
              spin=(193.4, 195.8, 30, 150)),
        L("MINIMUM RISK SCORE LOWERED", 1350, 450, t=193.4, size=50, rot=-2, bgc=(255, 140, 120)),
        L("\"TO DIVERSIFY\"", 900, 640, t=196.6, size=50, rot=4, bgc=(255, 255, 255)),
    ]))
    S.append(Scene(199.3, "chamber", [
        C("senator", 560, GROUND, t=199.3, talk=[(199.32, 205.44)], eyes="angry", mouth="shout",
          arms="up"),
        SAY("\"The biggest swindle\nfrom political power of\nParaguay's democratic era!\"", "senator", t=199.6,
            size=50, id="swindle"),
        L("OPPOSITION\nSENATOR", 215, 560, t=199.8, size=40, rot=-3),
        L("ALLEGATION - NOT PROVEN", 1200, 800, t=206.2, size=56, rot=-4, bgc=(255, 140, 120), enter="slam"),
    ]))
    # --- part 4
    S.append(part_card(209.7, 4, "THE PRESIDENT'S SHARES", "paper_purple"))
    S.append(Scene(212.9, "cork", [
        C("pena", 520, GROUND, t=213.0),
        L("SANTIAGO PEÑA", 520, 330, t=215.4, size=58, rot=-2),
        L("47 · ECONOMIST", 1250, 220, t=216.6, size=58, rot=2, bgc=(255, 255, 255)),
        L("EX CENTRAL BANK & IMF", 1250, 380, t=219.4, size=52, rot=-2, bgc=(220, 240, 255), out=225.5),
        C("cartes", 1250, GROUND + 40, t=222.6, scale=0.95, mouth="smile"),
        SAY("\"A bright\nyoung man!\"", "cartes", t=225.6, size=46),
        L("FINANCE MINISTER UNDER CARTES", 1250, 520, t=223.4, size=40, rot=1, out=225.5),
    ]))
    S.append(Scene(228.8, "street_py", [
        P(art.ballot_box(), 600, 940, t=228.9),
        C("pena", 1150, GROUND, t=229.2, arms="up", mouth="smile"),
        L("2023: WINS THE PRESIDENCY", 960, 170, t=229.6, size=64, rot=-2),
        L("43% OF THE VOTE", 600, 400, t=231.4, size=60, rot=3, bgc=(255, 230, 120)),
        *[P(art.coin(0.0001) if False else art.label("★", 40, bg=(255, 230, 120)), 300 + i * 180,
            520 + (i % 2) * 90, t=231.0 + i * 0.08, anchor="c", idle="bob", phase=i * .3) for i in range(0)],
    ]))
    S.append(Scene(234.4, "paper_green", [
        P(art.document("CREDIT HOUSE", 5), 400, 900, t=234.5),
        L("PEÑA INVESTED HERE", 400, 300, t=235.0, size=48, rot=-3),
        P(art.arrow(300, 120), 800, 700, t=238.8, anchor="c"),
        P(art.document("GRUPO VÁZQUEZ", 5), 1200, 900, t=239.2),
        L("ueno's PARENT COMPANY", 1200, 300, t=239.8, size=48, rot=2, out=247.3),
        P(art.calendar("MARCH", "2025"), 1640, 820, t=243.0),
        L("HELD SHARES UNTIL HERE\n(WHILE PRESIDENT)", 1500, 380, t=247.4, size=40, rot=-2,
          bgc=(255, 230, 120)),
    ]))
    S.append(Scene(250.5, "office_in", [
        C("pena", 560, GROUND - 30, t=250.6, talk=[(251.58, 253.44)]),
        P(art.podium("PRESIDENCY"), 560, 1010, t=250.6, enter="none"),
        L("HIS DEFENCE:", 1500, 110, t=250.6, size=58, rot=-2),
        SAY("\"I was an investor.\nI'm an economist.\"", "pena", t=251.6, size=56),
        L("\"NO LINK TO ueno BANK ITSELF\"", 1250, 760, t=254.6, size=50, rot=2, bgc=(255, 255, 255)),
    ]))
    S.append(Scene(258.2, "street", [
        C("pena", W / 2, GROUND, t=258.2, talk=[(263.0, 265.36)], eyes="angry"),
        C("reporter", 400, GROUND, t=258.4, scale=1.0, vary=80, flip=True),
        C("reporter", 700, GROUND, t=258.6, scale=0.95, vary=81, skin="brown", hair="short", hair_col=(20, 20, 20),
          col=(200, 120, 60)),
        C("reporter", 1500, GROUND, t=258.8, scale=1.0, vary=82, skin="pale", col=(90, 90, 170)),
        L("STATE & PENSION MONEY\nSTEERED TO ueno?", 640, 200, t=259.2, size=50, rot=-2, out=263.0),
        SAY("\"A false media\ncampaign!\"", "pena", t=263.0, size=56, out=266.1),
        L("ueno: \"NO DIRECT RELATIONSHIP\"", 960, 120, t=266.2, size=50, rot=2, bgc=(160, 230, 210)),
    ]))
    # --- part 5
    S.append(part_card(273.2, 5, "THE COLLAPSE", "paper_red"))
    S.append(Scene(275.9, "office_in", [
        C("regulator", 520, GROUND, t=276.0, hold="magnifier"),
        P(art.document("LOANS", 6), 1150, 930, t=276.6),
        P(art.document("LOANS", 6), 1450, 950, t=276.9),
        L("REGULATORS LOOK AT\nueno's LENDING", 960, 200, t=276.4, size=54, rot=-2),
        P(art.arrow(260, 110, (40, 120, 200)), 1300, 470, t=281.0, anchor="c"),
        L("COMPANIES TIED TO\nITS OWNER", 1650, 330, t=281.4, size=46, rot=3, bgc=(255, 230, 120)),
    ]))
    S.append(Scene(284.3, "night_far", [
        P(art.clock(3), 250, 260, t=284.4, anchor="c"),
        L("TUESDAY, NOV 3\nEARLY HOURS", 250, 480, t=285.0, size=46, rot=-3),
        P(art.building("central", 560, 440, label="CENTRAL BANK"), 760, 1000, t=284.6),
        P(art.arrow(220, 100, (240, 190, 60)), 1150, 740, t=287.4, anchor="c"),
        P(art.building("bank", 560, 440, label="ueno"), 1560, 1000, t=287.0, id="ueno"),
        P(art.stamp("IN RESOLUTION", size=58), 1560, 780, t=289.0, anchor="c", enter="slam", target="ueno"),
        L("SOLVENCY BELOW HALF\nTHE LEGAL MINIMUM", 1560, 300, t=291.2, size=46, rot=2, bgc=(255, 140, 120)),
    ]))
    S.append(Scene(294.4, "street_far", [
        P(art.building("bank", 640, 500, label="ueno"), W / 2, 1000, t=294.4, enter="none"),
        P(art.ice_block(700, 560), W / 2, 1040, t=294.6, enter="drop"),
        L("EVERY ACCOUNT FROZEN", W / 2, 170, t=294.9, size=76, rot=-2, bgc=(200, 235, 255)),
    ]))
    S.append(Scene(296.6, "street_py_far", [
        P(art.building("bank", 520, 440, label="ueno"), 1640, 1000, t=296.6, enter="none"),
        *crowd(160, 1300, GROUND, 8, scale=0.6, t=296.8, eyes="worried", mouth="frown", seed=120),
        L("~3 MILLION LOCKED OUT", 700, 170, t=297.4, size=66, rot=-2),
        C("pensioner", 1050, GROUND, t=300.8, scale=0.8, eyes="worried", mouth="frown", a={"ok": "crowd"}),
        L("PENSIONERS CUT OFF", 700, 330, t=301.0, size=52, rot=2, bgc=(255, 230, 120)),
        L("\"WHERE ARE OUR SAVINGS?\"", 700, 470, t=305.0, size=46, rot=-2, bgc=(255, 255, 255)),
    ]))
    S.append(Scene(309.0, "paper_red", [
        *[P(art.phone(0.8, screen="error"), 300 + i * 440, 900, t=310.0 + i * 0.4, idle="shake") for i in range(4)],
        L("BANKING APPS GO DOWN", W / 2, 200, t=312.4, size=74, rot=-2),
    ]))
    S.append(Scene(315.6, "street_far", [
        P(art.building("central", 620, 470, label="CENTRAL BANK"), W / 2, 1000, t=315.6, enter="none"),
        C("cbchief", 760, GROUND, t=315.7, eyes="worried", hold="briefcase",
          a={"move": (316.4, 319.0, -300, GROUND)}),
        L("CENTRAL BANK CHIEF RESIGNS", W / 2, 160, t=316.0, size=60, rot=-2),
        C("newchief", 1300, GROUND, t=319.3),
        L("NEW CHIEF", 1300, 380, t=319.6, size=50, rot=3, bgc=(255, 230, 120)),
    ]))
    S.append(Scene(321.1, "locker", [
        *[C("player", 240 + i * 205, GROUND, t=321.2 + i * 0.1, scale=0.95, vary=20 + i, eyes="angry", a={"ok": "team"},
            skin=["tan", "brown", "light", "tan", "brown"][i]) for i in range(5)],
        C("lawyer", 1380, GROUND, t=323.7),
        L("10 PLAYERS HIRE A LAWYER", 520, 170, t=323.9, size=58, rot=-2),
        SAY("\"The bank lied\nto footballers!\"", "lawyer", t=325.2, size=46, out=329.5, side="left"),
        P(art.document("TEAM LETTER", 4, 260, 320), 1700, 960, t=328.0),
        L("\"A FORCEFUL RESPONSE\"", 1300, 320, t=329.6, size=46, rot=3, bgc=(255, 230, 120)),
    ]))
    # --- part 6
    S.append(part_card(333.3, 6, "THE ARRESTS", "paper_purple"))
    S.append(Scene(335.7, "office_in", [
        P(art.paper_stack(10), 560, 960, t=336.4, enter="drop"),
        L("CRIMINAL COMPLAINT", 560, 330, t=338.0, size=56, rot=-2),
        L("POSSIBLE FRAUD?\nBREACH OF TRUST?", 1350, 300, t=341.2, size=54, rot=2, bgc=(255, 230, 120)),
        *[P(art.document("WARRANT", 3, 200, 250), 1060 + i * 125, 900 + (i % 2) * 20, t=344.4 + i * 0.12, ok="docs")
          for i in range(7)],
        L("8 ARREST WARRANTS", 1420, 560, t=345.6, size=56, rot=-3, bgc=(255, 140, 120)),
    ]))
    S.append(Scene(352.1, "paper_blue", [
        P(art.building("bank", 480, 420, label="ueno"), 420, 900, t=352.2),
        *[P(art.building("office", 280, 260, col=c), 1250 + (i % 2) * 330, 500 + (i // 2) * 360, t=353.2 + i * .2)
          for i, c in enumerate([(200, 170, 120), (170, 150, 200), (200, 130, 130), (150, 190, 150)])],
        P(art.arrow(340, 120, (240, 190, 60)), 850, 560, t=354.0, anchor="c"),
        L("RISKY LOANS & OVERDRAFTS\nTO LINKED COMPANIES?", 860, 160, t=352.6, size=50, rot=-2),
        L("CASE NOW COVERS 27 PEOPLE", 860, 975, t=358.8, size=54, rot=2, bgc=(255, 230, 120)),
    ]))
    S.append(Scene(361.8, "jail", [
        *[x for i in range(3) for x in (C("exec", 360 + i * 600, GROUND, t=362.0 + i * 0.3, scale=0.95, vary=30 + i,
                                            eyes="worried", mouth="frown", glasses=i == 1),
                                          P(art.jail_bars(380, 470), 360 + i * 600, GROUND + 10, t=362.2 + i * 0.3,
                                            enter="drop"))],
        L("6 EXECUTIVES DETAINED", W / 2, 140, t=362.4, size=64, rot=-2),
        L("NO SHARING A CELL!", W / 2, 300, t=366.0, size=54, rot=2, bgc=(255, 230, 120)),
    ]))
    S.append(Scene(368.9, "paper_blue", [
        P(art.yacht(), 560, 820, t=369.0, idle="bob", id="yacht"),
        P(art.plane(), 1420, 560, t=370.2, idle="bob", id="plane"),
        P(art.stamp("SEIZED", size=80), 560, 690, t=371.4, anchor="c", enter="slam", target="yacht"),
        P(art.stamp("SEIZED", size=80, rot=8), 1420, 420, t=372.4, anchor="c", enter="slam", target="plane"),
        L("ALL PRESUMED INNOCENT", W / 2, 990, t=374.8, size=60, rot=-1, bgc=(255, 255, 255)),
    ]))
    S.append(Scene(377.1, "chamber", [
        *crowd(250, 1000, GROUND, 4, scale=0.75, t=377.2, seed=200, mouth="smile"),
        L("EMERGENCY LAW: PAY DEPOSITORS BACK", W / 2, 140, t=377.4, size=52, rot=-2),
        L("UP TO 40 MONTHLY\nMINIMUM WAGES EACH", 1400, 360, t=379.8, size=50, rot=2, bgc=(255, 230, 120)),
        *[P(art.cash_stack(0.7), 1200 + (i % 3) * 200, 760 + (i // 3) * 120, t=382.6 + i * .12, ok="cash") for i in range(6)],
        L("800,000+ PAID BACK BY FRIDAY", 640, 330, t=387.6, size=48, rot=-2, bgc=(200, 240, 200)),
        L("MILLIONS STILL WAITING", 640, 495, t=391.1, size=52, rot=2, bgc=(255, 140, 120)),
    ]))
    # --- part 7
    S.append(part_card(393.3, 7, "THE STREETS", "paper_red"))
    signs = [("sign", "WHERE'S\nOUR MONEY?"), ("sign", "PEÑA\nANSWER!"), ("sign", "GIVE IT\nBACK!"),
             ("sign", "JUSTICE!")]
    S.append(Scene(395.0, "dusk_far", [
        P(art.building("congress", 760, 560, label="CONGRESS"), W / 2, 1000, t=395.0, enter="none"),
        *crowd(160, 1760, GROUND + 40, 8, scale=0.62, t=395.4, mouth="shout", eyes="angry", seed=300,
               hold=signs + [None, None, None, None], rows=2),
        L("ANGER EXPLODES", W / 2, 150, t=395.6, out=397.6, size=72, rot=-2, bgc=(255, 140, 120)),
        L("THOUSANDS OUTSIDE CONGRESS", W / 2, 150, t=397.6, size=52, rot=2),
    ]))
    S.append(Scene(403.6, "night", [
        *[C("riot", 1100 + i * 190, GROUND, t=403.7 + i * 0.08, scale=0.85, vary=40 + i, flip=True, a={"ok": "police"}) for i in range(4)],
        *crowd(140, 900, GROUND, 5, scale=0.62, t=403.8, mouth="shout", eyes="angry", seed=340,
               hold=signs + [None]),
        L("PROTESTERS PUSH POLICE LINES", W / 2, 160, t=404.2, size=58, rot=-2),
    ]))
    S.append(Scene(411.3, "night_far", [
        P(art.building("office", 760, 600, label="ueno", col=(90, 110, 130)), W / 2, 1000, t=411.3, enter="none"),
        P(art.window_pane(False, 420, 300), W / 2, 760, t=411.3, enter="none", out=414.4, anchor="c", ok=True),
        P(art.window_pane(True, 420, 300), W / 2, 760, t=414.4, enter="none", anchor="c", ok=True),
        Actor(art.rock(), 200, 900, t=413.4, anchor="c", enter="none", idle="none",
              move=(413.5, 414.4, W / 2, 760)),
        L("A ueno OFFICE IS SMASHED", W / 2, 140, t=412.0, size=60, rot=-2),
        L("1 OFFICER HURT · 7 DETAINED", W / 2, 300, t=417.0, size=54, rot=2, bgc=(255, 230, 120)),
    ]))
    S.append(Scene(421.1, "chamber", [
        P(art.document("IMPEACHMENT", 7, 380, 470), 520, 980, t=421.2),
        L("IMPEACHMENT MOTION", 520, 300, t=422.6, size=56, rot=-2, out=436.1),
        L("GRAVE FAILURE TO DO HIS JOB", 1330, 300, t=428.4, size=44, rot=2, bgc=(255, 255, 255)),
        L("CONFLICT OF INTEREST", 1330, 440, t=432.6, size=44, rot=-2, bgc=(255, 255, 255)),
        L("MISUSE OF PENSION FUNDS", 1330, 580, t=434.0, size=44, rot=2, bgc=(255, 255, 255)),
        L("PEÑA DENIES ALL OF IT", 1330, 760, t=436.2, size=56, rot=-2, bgc=(255, 230, 120)),
    ]))
    S.append(Scene(438.3, "office_in", [
        P(art.newspaper("WARNINGS ABOUT\nTHE BANK IGNORED", "as reported by The Guardian"), 620, 800, t=438.4),
        C("regulator", 1400, GROUND, t=444.4, hold="magnifier", hair="receding", hair_col=(140, 140, 140), skin="tan", col=(30, 30, 40), build=1.15),
        L("PROSECUTORS NOW\nINVESTIGATING PEÑA", 1400, 300, t=444.6, size=52, rot=2, bgc=(255, 140, 120)),
    ]))
    # --- part 8
    S.append(part_card(447.6, 8, "THE GODFATHER", "paper_green"))
    S.append(Scene(449.8, "chamber", [
        C("cartes", 700, GROUND, t=453.8, talk=[(462.66, 470.64)], a={"idle": "bob"}),
        L("HORACIO\nCARTES", 300, 560, t=454.0, size=48, rot=-2),
        L("THE BLOW CAME FROM\nINSIDE HIS OWN PARTY", W / 2, 160, t=449.9, size=56, rot=2, out=453.8),
        L("COLORADO PARTY LEADER\n& PEÑA'S MENTOR", 1350, 330, t=455.0, size=50, rot=2, out=462.5),
        SAY("\"We will not stand on the\nside of the theft of public,\nprivate and pensioners' funds.\"", "cartes",
            t=462.7, size=44, out=468.6),
        SAY("\"We support the\nimpeachment of\nthe president.\"", "cartes", t=468.6, size=50),
    ]))
    S.append(Scene(471.5, "chamber", [
        C("pena", 520, GROUND, t=471.5, eyes="worried", mouth="frown"),
        *[C("senator", 1000 + i * 240, GROUND, t=471.6, scale=0.95, vary=50 + i, flip=True,
            skin=["light", "tan", "brown"][i], col=[(40, 40, 50), (110, 40, 40), (60, 60, 90)][i], mustache=i == 1,
            a={"move": (472.0, 474.5, 2300 + i * 200, GROUND)}) for i in range(3)],
        L("HIS PARTY ABANDONS HIM", 1000, 170, t=472.2, size=60, rot=-2, out=474.6),
        P(art.board([("IMPEACH?", (255, 255, 255)), ("YES 78", (120, 230, 120)), ("NO  0", (255, 120, 120))],
                    640, 460), 1300, 600, t=475.0, anchor="c"),
        P(art.sound_block(), 1760, 980, t=476.4, anchor="c"),
        gavel_actor(1760, 950, 478.4),
    ]))
    S.append(Scene(483.0, "studio", [
        P(art.tv(art.char("pena", mouth="closed", eyes="worried")), 600, 560, t=483.1, anchor="c", id="tv"),
        L("MEANWHILE... A VIDEO", 470, 170, t=483.2, size=56, rot=-2),
        SAY("\"I have decided to\nsubmit my resignation.\"", "tv", t=486.0, size=48, out=490.3),
        SAY("\"I want to apologise to\nthe people if at any\npoint I failed.\"", "tv", t=490.3, size=46, out=494.4),
        SAY("\"It was never my\nintention to betray\nyour trust.\"", "tv", t=494.4, size=48),
    ]))
    # --- part 9
    S.append(part_card(498.2, 9, "TRUMP'S MAN", "paper_blue"))
    S.append(Scene(500.1, "washington", [
        P(art.building("capitol", 900, 420), W / 2, 700, t=500.1, enter="none"),
        P(art.flag_py(), 380, 300, t=501.0, anchor="c", idle="sway"),
        P(art.flag_us(), 1540, 300, t=501.0, anchor="c", idle="sway"),
        L("WHY WASHINGTON CARES", W / 2, 140, t=500.4, size=60, rot=-2),
        C("pena", 760, GROUND, t=503.4, arms="point"),
        C("trump", 1160, GROUND, t=503.6, flip=True, arms="point", mouth="smile"),
    ]))
    S.append(Scene(506.6, "us_hall", [
        L("JAN 2025: TRUMP'S 2ND INAUGURATION", W / 2, 140, t=506.7, size=54, rot=-2),
        *[P(art.chair(), 300 + i * 260, GROUND, t=507.0 + i * 0.1) for i in range(5)],
        C("pena", 1650, GROUND, t=511.9, eyes="worried"),
        L("MOVED INDOORS - NO SEAT", 1100, 360, t=512.4, size=52, rot=2, bgc=(255, 230, 120)),
        L("...BUT HE KEPT SHOWING UP", 1100, 500, t=514.4, size=46, rot=-2, bgc=(255, 255, 255)),
    ]))
    S.append(Scene(516.4, "paper_yellow", [
        C("pena", 960, GROUND, t=516.5, mouth="smile"),
        P(art.badge("BOARD OF\nPEACE"), 420, 560, t=517.6, anchor="c", idle="sway"),
        L("FOUNDING MEMBER", 420, 820, t=518.4, size=44, rot=-2),
        P(art.badge("SHIELD\nOF THE\nAMERICAS", (150, 190, 240)), 1500, 560, t=520.8, anchor="c", idle="sway"),
    ]))
    S.append(Scene(523.5, "washington", [
        C("pena", 760, GROUND, t=523.5, arms="point"),
        C("rubio", 1160, GROUND, t=523.6, flip=True, arms="point", mouth="smile"),
        L("JUNE: SECRETARY OF STATE MARCO RUBIO", W / 2, 140, t=523.8, size=50, rot=-2),
        L("\"STRATEGIC PARTNERSHIP\"", W / 2, 310, t=527.6, size=56, rot=2, bgc=(255, 230, 120)),
    ]))
    S.append(Scene(530.4, "office_in", [
        C("pena", 760, GROUND, t=530.4, arms="point"),
        C("bessent", 1160, GROUND, t=530.5, flip=True, arms="point", mouth="smile"),
        L("OCT 22: TREASURY SECRETARY SCOTT BESSENT", W / 2, 140, t=530.6, size=48, rot=-2),
        L("\"GROWING ECONOMIC PARTNERSHIP\"", W / 2, 290, t=535.2, size=50, rot=2, bgc=(255, 230, 120)),
    ]))
    S.append(Scene(539.5, "paper_red", [
        L("12 DAYS LATER...", W / 2, 160, t=539.5, size=76, rot=-2),
        C("pena", 420, GROUND, t=539.6, eyes="worried", a={"fall": 540.8, "idle": "none"}),
        P(art.newspaper("\"ONE OF THE STRONGEST\nBASTIONS OF TRUMP'S\nNETWORK\"", "Colombia's El Tiempo"),
          1320, 860, t=542.7),
    ]))
    # --- part 10
    S.append(part_card(549.4, 10, "THE TRIAL", "paper_purple"))
    S.append(Scene(551.0, "chamber", [
        L("HERE'S THE TWIST", W / 2, 140, t=551.1, size=72, rot=-2, bgc=(255, 230, 120)),
        P(art.document("RESIGNATION", 5), 620, 950, t=552.4, id="resignation"),
        P(art.stamp("REJECTED", size=72), 620, 700, t=554.6, anchor="c", enter="slam", target="resignation"),
        L("CONGRESS REFUSES IT", 1350, 420, t=553.6, size=56, rot=2),
        P(art.question(180), 1350, 720, t=556.4, anchor="c", idle="bob"),
    ]))
    S.append(Scene(557.7, "paper_blue", [
        P(art.scroll("CONSTITUTION:\nRESIGN = SENATOR\nFOR LIFE"), 560, 900, t=557.8),
        P(art.shield("IMMUNITY"), 1350, 860, t=562.8, out=565.8),
        P(art.shield("IMMUNITY", cracked=True), 1350, 860, t=565.8, enter="none", idle="shake"),
        L("IMPEACHED = NO SHIELD", 1350, 330, t=566.0, size=56, rot=2, bgc=(255, 140, 120)),
    ]))
    S.append(Scene(570.1, "chamber", [
        *[C("senator", 500 + i * 260, GROUND, t=570.2, scale=0.95, vary=60 + i, flip=False,
            skin=["light", "tan", "brown", "tan"][i], col=[(40, 40, 50), (110, 40, 40), (60, 60, 90), (50, 80, 50)][i],
            mustache=i % 2 == 0, a={"move": (572.6 + i * 0.2, 575.0 + i * 0.2, 2400, GROUND)}) for i in range(4)],
        L("HIS PARTY'S DEPUTIES WALK OUT", W / 2, 150, t=572.6, size=56, rot=-2),
        L("NO QUORUM!", W / 2, 420, t=575.6, size=90, rot=3, bgc=(255, 230, 120)),
    ]))
    S.append(Scene(577.3, "senate", [
        L("THE SENATE BECOMES A COURT", W / 2, 360, t=577.4, size=60, rot=-2),
        *[C("senator", 300 + i * 220, GROUND, t=577.6 + i * 0.05, scale=0.7, vary=70 + i, skin=["light", "tan", "brown", "tan"][i % 4],
            col=[(40, 40, 50), (110, 40, 40), (60, 60, 90), (50, 80, 50)][i % 4], mustache=i % 3 == 0,
            a={"ok": "senate", "id": f"sen{i}"}) for i in range(7)],
        L("TO REMOVE HIM: 30 OF 45", W / 2, 520, t=580.8, size=56, rot=2, bgc=(255, 230, 120)),
    ]))
    S.append(Scene(585.8, "senate", [
        C("lawyer", 560, GROUND, t=585.9, talk=[(592.76, 594.22)], arms="up"),
        SAY("\"72 more hours\nto prepare?\"", "lawyer", t=586.6, size=50, out=592.7),
        SAY("\"This is not\ndue process!\"", "lawyer", t=592.8, size=56),
        L("PEÑA'S\nSIDE", 240, 560, t=586.2, size=46, rot=-2),
    ]))
    S.append(Scene(594.9, "senate", [
        P(art.board([("SENATE SAYS NO", (255, 255, 255)), ("39 - 3", (255, 230, 120))], 760, 380), 760, 460,
          t=595.0, anchor="c"),
        P(art.sound_block(), 1520, 980, t=595.0, anchor="c"),
        gavel_actor(1520, 950, 596.5),
        P(art.chair(), 1500, 700, t=598.6),
        L("PEÑA DOESN'T SHOW UP", 1500, 330, t=598.8, size=50, rot=2, bgc=(255, 230, 120)),
    ]))
    S.append(Scene(600.5, "street_far", [
        C("lawyer", 520, GROUND, t=600.6, arms="point"),
        P(art.building("court", 700, 520, label="INTER-AMERICAN COURT"), 1300, 1000, t=601.6),
        L("HUMAN RIGHTS CASE?", 1300, 200, t=603.0, size=56, rot=-2),
    ]))
    S.append(Scene(605.1, "sepia", [
        L("PARAGUAY HAS DONE THIS BEFORE", W / 2, 140, t=605.2, size=56, rot=-2),
        C("lugo", 620, GROUND, t=607.1, eyes="worried"),
        L("2012: PRESIDENT FERNANDO LUGO\nREMOVED IN ABOUT 2 DAYS", 1300, 380, t=607.6, size=46, rot=2,
          bgc=(240, 225, 190)),
        L("\"A PARLIAMENTARY COUP\"", 1300, 640, t=611.4, size=52, rot=-2, bgc=(255, 255, 255)),
    ]))
    S.append(Scene(614.5, "chamber", [
        C("alliana", 620, GROUND, t=614.6),
        L("VICE PRESIDENT PEDRO ALLIANA", 620, 330, t=615.4, size=46, rot=-2),
        L("NEXT IN LINE", 1350, 220, t=616.6, size=60, rot=2, bgc=(255, 230, 120)),
        *[P(art.question(120), 1150 + i * 160, 480, t=618.6 + i * 0.1, anchor="c", idle="bob", phase=i * .3)
          for i in range(4)],
        L("HE DENIES IT", 1350, 640, t=621.4, size=52, rot=-2, bgc=(255, 255, 255)),
        L("LOWER HOUSE: 48-30\nNOT TO IMPEACH HIM", 1350, 850, t=622.6, size=46, rot=2),
    ]))
    S.append(Scene(626.0, "senate", [
        P(art.scales(), W / 2, 960, t=626.1),
        L("FRIDAY AFTERNOON:\nTHE SENATE WEIGHS THE EVIDENCE", W / 2, 150, t=626.4, size=50, rot=-2),
        L("PREDICTION: UNANIMOUS", 400, 600, t=631.5, size=48, rot=-3, bgc=(255, 230, 120)),
        L("IF REMOVED: ALLIANA\nSERVES UNTIL AUG 2028", 1440, 600, t=634.9, size=46, rot=3, bgc=(255, 255, 255)),
    ]))
    # --- outro
    S.append(Scene(641.1, "studio", [
        C("dom", 560, 830, t=641.1, talk=[(641.14, 660.0)], scale=1.45, a={"enter": "none"}),
        P(art.desk(), 560, 1090, t=641.1, enter="none"),
        L("HERE'S THE FOOTNOTE", 1350, 170, t=641.4, size=62, rot=2, bgc=(255, 230, 120)),
        P(art.phone(1.0, screen="locked"), 1350, 760, t=645.4, out=649.3),
        P(art.scales(), 1350, 860, t=649.4),
        L("SOMEONE HAS TO ANSWER", 1350, 380, t=656.6, size=60, rot=-2, bgc=(255, 140, 120)),
    ]))
    S.append(Scene(660.0, "studio", [
        L("DOM TALKS POLITICS", W / 2, 380, t=660.0, size=110, rot=-2, bgc=(255, 230, 120), enter="slam"),
        L("SUBSCRIBE FOR MORE FOOTNOTES", W / 2, 600, t=660.6, size=56, rot=2, bgc=(255, 255, 255)),
        P(art.sound_block(), 1500, 960, t=660.0, anchor="c"),
        gavel_actor(1500, 930, 660.15),
    ]))
    return S


END = 663.0
# impacts for camera shake + matching sfx: (time, kind)
SFX = [
    (5.14, "pop"), (5.92, "pop"), (6.18, "thud"), (7.05, "gavel"), (8.25, "thud"), (13.25, "thud"), (20.6, "pop"), (35.5, "crash"),
    (79.45, "stamp"), (102.0, "cash"), (112.3, "gulp"), (124.0, "cash"), (206.25, "stamp"),
    (289.05, "stamp"), (294.75, "thud"), (336.6, "thud"), (371.45, "stamp"), (372.45, "stamp"),
    (395.4, "crowd"), (403.8, "crowd_short"), (414.4, "glass"), (478.4, "gavel"), (540.95, "thud"),
    (554.65, "stamp"), (565.8, "crack"), (596.5, "gavel"), (660.15, "gavel"),
]
WHOOSH = [39.0, 95.9, 144.9, 209.7, 273.2, 333.3, 393.3, 447.6, 498.2, 549.4]
SHAKE = {t: (14 if k == "gavel" else 8) for t, k in SFX if k in ("gavel", "stamp", "thud", "crash", "glass", "crack")}


def thumbnails():
    import thumbnails as th
    out = []
    # A - the face: shocked president, bank crumbling, the core hook
    im = th.canvas(col=(214, 52, 48, 255), rays=(1350, 600, (236, 84, 64, 255)))
    th.put(im, art.building("bank", 760, 600, label="ueno"), 1460, 1130, rot=-8)
    th.put(im, art.char("pena", mouth="shout", eyes="worried", arms="up"), 520, 1180, scale=2.1)
    th.big_text(im, ["ONE BANK", ("TOOK DOWN", (255, 225, 80)), "A PRESIDENT"], 1340, 330, size=150, rot=-3)
    out.append(("A_face", im))
    # B - the stakes: 3 million people's money frozen
    im = th.canvas(col=(40, 110, 190, 255), rays=(960, 640, (60, 135, 215, 255)))
    th.put(im, art.vault(520, 520), 1380, 1020)
    th.put(im, art.ice_block(700, 660), 1380, 1080)
    for i, x in enumerate((140, 360, 580)):
        th.put(im, art.crowd_person((7, 15, 30)[i], scale=1.25, mouth="shout", eyes="angry"), x, 1150)
    th.big_text(im, [("3 MILLION", (255, 225, 80)), "LOCKED OUT"], 640, 250, size=170, rot=-4)
    th.big_text(im, ["FROZEN!"], 1380, 470, size=130, fill=(190, 235, 255), rot=6)
    out.append(("B_stakes", im))
    # C - the power angle: Trump's ally, impeached
    im = th.canvas(bgk="washington")
    th.put(im, art.building("capitol", 900, 420), 960, 800, scale=1.2)
    th.put(im, art.char("trump", mouth="open", eyes="worried", flip=True), 1560, 1150, scale=1.9)
    th.put(im, art.char("pena", mouth="frown", eyes="worried"), 560, 1150, scale=1.9)
    th.big_text(im, [("IMPEACHED", (235, 45, 45))], 600, 900, size=120, rot=-12, stroke=12)
    th.big_text(im, ["TRUMP'S MAN", ("IN PARAGUAY", (255, 225, 80))], 960, 190, size=140, rot=-2)
    out.append(("C_power", im))
    return out
