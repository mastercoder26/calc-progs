from pathlib import Path
import string

OUT = Path(__file__).resolve().parent
NAME = "PHYFRQ25"

USED = set()
BAD = {}


def use(label):
    if len(label) > 2:
        raise ValueError(f"TI-BASIC labels should be 1-2 chars: {label}")
    if label in USED:
        raise ValueError(f"duplicate label {label}")
    USED.add(label)
    return label


def alloc():
    for a in string.ascii_uppercase + string.digits:
        for b in string.ascii_uppercase + string.digits:
            label = a + b
            if label not in USED:
                USED.add(label)
                return label
    raise RuntimeError("out of labels")


H = use("H")
Q1 = use("Q1")
Q2 = use("Q2")
Q3 = use("Q3")
Q4 = use("Q4")
FS = use("FS")
EF = use("EF")
EX = use("EX")


def screen(*pages):
    return [list(pg) for pg in pages]


def _safe_text(s):
    return s.replace(":", "")


def _disp_wrapped(lines, text):
    text = _safe_text(text)
    if not text:
        lines.append('Disp " "')
        return
    while len(text) > 16:
        lines.append(f'Disp "{text[:16]}"')
        text = text[16:]
    lines.append(f'Disp "{text}"')


def add_text(lines, label, title, text_pages, back):
    lines += [f"Lbl {label}"]
    for pg in text_pages:
        lines += ["ClrHome"]
        _disp_wrapped(lines, title)
        for item in pg:
            _disp_wrapped(lines, item)
        lines.append("Pause")
    lines.append(f'Menu("NEXT","BACK",{back},"HOME",{H},"EXIT",{EX})')


def add_solver_result_nav(lines, back):
    lines.append("Pause")
    lines.append(f'Menu("NEXT","BACK",{back},"HOME",{H},"EXIT",{EX})')


def add_bad(label, msg, back):
    BAD[label] = (msg, back)


def bad_label(msg, back):
    label = alloc()
    add_bad(label, msg, back)
    return label


def add_topic(lines, label, menu_title, items, back):
    sub = [(alloc(), item) for item in items]
    pairs = []
    for sublabel, item in sub:
        pairs.append(f'"{item["menu"]}",{sublabel}')
    lines += [
        f"Lbl {label}",
        "ClrHome",
        f'Menu("{menu_title}",' + ",".join(pairs + [f'"BACK",{back}']) + ")",
    ]
    for sublabel, item in sub:
        if "pages" in item:
            add_text(lines, sublabel, item["title"], item["pages"], label)
        else:
            lines.append(f"Lbl {sublabel}")
            item["solver"](lines, sublabel, label)


def solver_q1(lines, menu_label, back):
    lvf = alloc()
    ldk = alloc()
    lpc = alloc()
    badm = bad_label("M SUM CANT 0", menu_label)
    lines += [
        "ClrHome",
        f'Menu("Q1 SOLVE","VF STICK",{lvf},"DK STICK",{ldk},"P CHECK",{lpc},"BACK",{back})',
        f"Lbl {lvf}",
        "ClrHome",
        'Input "M1",A',
        'Input "V1X",B',
        'Input "M2",C',
        'Input "V2X",D',
        "If A+C=0",
        "Then",
        f"Goto {badm}",
        "End",
        "(A*B+C*D)/(A+C)->E",
        "ClrHome",
        'Disp "VF=",E',
    ]
    add_solver_result_nav(lines, menu_label)
    lines += [
        f"Lbl {ldk}",
        "ClrHome",
        'Input "M1",A',
        'Input "V1X",B',
        'Input "M2",C',
        'Input "V2X",D',
        "If A+C=0",
        "Then",
        f"Goto {badm}",
        "End",
        "A*B+C*D->E",
        "A+C->F",
        "E/F->G",
        ".5*A*B^2+.5*C*D^2->H",
        ".5*F*G^2->I",
        "I-H->J",
        "ClrHome",
        'Disp "VF=",G',
        'Disp "KI=",H',
        'Disp "KF=",I',
        'Disp "DK=",J',
    ]
    add_solver_result_nav(lines, menu_label)
    lines += [
        f"Lbl {lpc}",
        "ClrHome",
        'Input "M1",A',
        'Input "V1X",B',
        'Input "M2",C',
        'Input "V2X",D',
        'Input "VF",E',
        "A*B+C*D->F",
        "(A+C)*E->G",
        "G-F->H",
        "ClrHome",
        'Disp "PI=",F',
        'Disp "PF=",G',
        'Disp "DP=",H',
    ]
    add_solver_result_nav(lines, menu_label)


def solver_q2(lines, menu_label, back):
    lh = alloc()
    lx = alloc()
    lk = alloc()
    lv = alloc()
    badk = bad_label("K CANT BE 0", menu_label)
    badx = bad_label("X CANT BE 0", menu_label)
    badm = bad_label("M CANT BE 0", menu_label)
    badr = bad_label("NEG UNDER ROOT", menu_label)
    lines += [
        "ClrHome",
        'Disp "DEG MODE"',
        f'Menu("Q2 SOLVE","H LTH",{lh},"X FROM E",{lx},"K FROM X",{lk},"V AT X",{lv},"BACK",{back})',
        f"Lbl {lh}",
        "ClrHome",
        'Input "L",A',
        'Input "TH DEG",B',
        "A*sin(B)->C",
        "ClrHome",
        'Disp "H=",C',
    ]
    add_solver_result_nav(lines, menu_label)
    lines += [
        f"Lbl {lx}",
        "ClrHome",
        'Input "M",A',
        'Input "H",B',
        'Input "G",C',
        'Input "K",D',
        "If D=0",
        "Then",
        f"Goto {badk}",
        "End",
        "2*A*B*C/D->E",
        "If E<0",
        "Then",
        f"Goto {badr}",
        "End",
        "E^.5->F",
        "ClrHome",
        'Disp "X=",F',
    ]
    add_solver_result_nav(lines, menu_label)
    lines += [
        f"Lbl {lk}",
        "ClrHome",
        'Input "M",A',
        'Input "H",B',
        'Input "G",C',
        'Input "X",D',
        "If D=0",
        "Then",
        f"Goto {badx}",
        "End",
        "2*A*B*C/(D^2)->E",
        "ClrHome",
        'Disp "K=",E',
    ]
    add_solver_result_nav(lines, menu_label)
    lines += [
        f"Lbl {lv}",
        "ClrHome",
        'Input "M",A',
        'Input "H",B',
        'Input "G",C',
        'Input "K",D',
        'Input "X",E',
        "If A=0",
        "Then",
        f"Goto {badm}",
        "End",
        "A*B*C-.5*D*E^2->F",
        "2*F/A->G",
        "If G<0",
        "Then",
        f"Goto {badr}",
        "End",
        "G^.5->H",
        "ClrHome",
        'Disp "V=",H',
    ]
    add_solver_result_nav(lines, menu_label)


def solver_q3(lines, menu_label, back):
    lft = alloc()
    lm = alloc()
    lms = alloc()
    lx = alloc()
    bads = bad_label("SIN TH CANT 0", menu_label)
    badg = bad_label("G CANT BE 0", menu_label)
    lines += [
        "ClrHome",
        'Disp "DEG MODE"',
        f'Menu("Q3 SOLVE","FT FROM M",{lft},"M FROM FT",{lm},"M FROM SLP",{lms},"XVAR",{lx},"BACK",{back})',
        f"Lbl {lft}",
        "ClrHome",
        'Input "M",A',
        'Input "G",B',
        'Input "TH DEG",C',
        "sin(C)->D",
        "If D=0",
        "Then",
        f"Goto {bads}",
        "End",
        "5*A*B/(6*D)->E",
        "ClrHome",
        'Disp "FT=",E',
    ]
    add_solver_result_nav(lines, menu_label)
    lines += [
        f"Lbl {lm}",
        "ClrHome",
        'Input "FT",A',
        'Input "G",B',
        'Input "TH DEG",C',
        "sin(C)->D",
        "If B=0",
        "Then",
        f"Goto {badg}",
        "End",
        "If D=0",
        "Then",
        f"Goto {bads}",
        "End",
        "6*A*D/(5*B)->E",
        "ClrHome",
        'Disp "M=",E',
    ]
    add_solver_result_nav(lines, menu_label)
    lines += [
        f"Lbl {lms}",
        "ClrHome",
        'Input "SLOPE",A',
        'Input "G",B',
        "If B=0",
        "Then",
        f"Goto {badg}",
        "End",
        "6*A/(5*B)->C",
        "ClrHome",
        'Disp "M=",C',
    ]
    add_solver_result_nav(lines, menu_label)
    lines += [
        f"Lbl {lx}",
        "ClrHome",
        'Input "TH DEG",A',
        "sin(A)->B",
        "If B=0",
        "Then",
        f"Goto {bads}",
        "End",
        "1/B->C",
        "ClrHome",
        'Disp "X=1/SIN=",C',
    ]
    add_solver_result_nav(lines, menu_label)


def solver_q4(lines, menu_label, back):
    la = alloc()
    lr = alloc()
    lc = alloc()
    badm = bad_label("M CANT BE 0", menu_label)
    badv = bad_label("V CANT BE 0", menu_label)
    lines += [
        "ClrHome",
        f'Menu("Q4 SOLVE","A FROM RHO",{la},"RHO NEUT",{lr},"A COMP",{lc},"BACK",{back})',
        f"Lbl {la}",
        "ClrHome",
        'Input "RHO",A',
        'Input "V",B',
        'Input "M",C',
        'Input "G",D',
        "If C=0",
        "Then",
        f"Goto {badm}",
        "End",
        "(A*B*D-C*D)/C->E",
        "ClrHome",
        'Disp "A=",E',
    ]
    add_solver_result_nav(lines, menu_label)
    lines += [
        f"Lbl {lr}",
        "ClrHome",
        'Input "M",A',
        'Input "V",B',
        "If B=0",
        "Then",
        f"Goto {badv}",
        "End",
        "A/B->C",
        "ClrHome",
        'Disp "RHO=",C',
    ]
    add_solver_result_nav(lines, menu_label)
    lines += [
        f"Lbl {lc}",
        "ClrHome",
        'Input "RHO1",A',
        'Input "RHO2",B',
        'Input "V",C',
        'Input "M",D',
        'Input "G",E',
        "If D=0",
        "Then",
        f"Goto {badm}",
        "End",
        "(A*C*E-D*E)/D->F",
        "(B*C*E-D*E)/D->G",
        "G-F->H",
        "ClrHome",
        'Disp "A1=",F',
        'Disp "A2=",G',
        'Disp "DA=",H',
    ]
    add_solver_result_nav(lines, menu_label)


Q1_ITEMS = [
    {
        "menu": "SCENARIO",
        "title": "Q1 SCENE",
        "pages": screen(
            ["CART M1 MOVES", "BLOCK M2 DROPS", "THEY STICK"],
            ["DUR COLLISION", "EXT HORIZ IMP", "IS TINY"],
            ["USE X AXIS FOR", "MOMENTUM EQ", "DUR IMPACT"],
            ["AFTER CONTACT", "BOTH SHARE", "ONE VF"],
            ["MOMENTUM CAN", "STAY SAME WHEN", "KE DOES NOT"],
            ["EXPLAIN KE LOSS", "THERMAL SOUND", "DEFORMATION"],
        ),
    },
    {
        "menu": "RULES",
        "title": "Q1 RULES",
        "pages": screen(
            ["SYSTEM: BOTH", "OBJECTS TOGETHER", "FOR COLLISION"],
            ["ONLY COMP WITH", "NO EXT IMPULSE", "IS CONSERVED"],
            ["PICK + DIRECTION", "KEEP SIGNS", "CONSISTENT"],
            ["INELASTIC: VF", "SAME FOR BOTH", "AFTER HIT"],
            ["DO NOT FORCE KE", "TO BE CONSERVED", "IT IS NOT"],
            ["SEPARATE PHASES", "COLLISION VS", "POST MOTION"],
            ["JUSTIFY CLAIMS", "WITH LAW + WHY", "NOT JUST EQN"],
        ),
    },
    {
        "menu": "EQS",
        "title": "Q1 EQS",
        "pages": screen(
            ["P=MV"],
            ["SUM PXI=SUM PXF"],
            ["M1V1X+M2V2X=", "(M1+M2)VF"],
            ["IF V2X=0 THEN", "VF=M1V1X/(M1+M2)"],
            ["KI=.5M1V1^2+", ".5M2V2^2"],
            ["KF=.5(M1+M2)VF^2"],
            ["DK=KF-KI", "INELASTIC DK<0"],
        ),
    },
    {
        "menu": "FLOW",
        "title": "Q1 FLOW",
        "pages": screen(
            ["DRAW BEFORE AND", "AFTER STATES", "WITH AXIS"],
            ["MARK KNOWNS AND", "ONE UNKNOWN", "USUALLY VF"],
            ["WRITE MOM EQ IN", "COMPONENT FORM", "THEN SOLVE"],
            ["COMPUTE KI THEN", "KF USING VF", "KEEP UNITS"],
            ["FIND DK=KF-KI", "STATE SIGN AND", "PHYS MEANING"],
            ["IF GRAPH ASKED", "LABEL AXES", "SLOPE/AREA"],
            ["FOR JUSTIFY", "CLAIM + LAW +", "CONTEXT REASON"],
        ),
    },
    {"menu": "SOLVE", "solver": solver_q1},
    {
        "menu": "TIPS",
        "title": "Q1 TIPS",
        "pages": screen(
            ["DROPPED BLOCK MAY", "HAVE VY BUT X", "CAN BE ZERO"],
            ["FINAL MASS IS", "M1+M2 IN VF", "AND KF"],
            ["VECTOR SIGNS", "MATTER MORE", "THAN SPEED"],
            ["CHECK LIMITS:", "M2 BIG -> VF", "SHOULD SHRINK"],
            ["UNITS CHECK:", "P IN KG M/S", "E IN J"],
            ["COMMON TRAP:", "MOM CONS YES", "KE CONS NO"],
        ),
    },
]


Q2_ITEMS = [
    {
        "menu": "SCENARIO",
        "title": "Q2 SCENE",
        "pages": screen(
            ["BLOCK SLIDES ON", "FRICTIONLESS", "RAMP"],
            ["LOSING UG WHILE", "GAINING K OR", "SPRING ENERGY"],
            ["AT MAX COMP", "BLOCK SPEED", "CAN BE ZERO"],
            ["MODEL WITH ONE", "CONSISTENT ZERO", "FOR UG"],
            ["ENERGY BAR CHART", "HELPS TRACK", "STATE CHANGES"],
        ),
    },
    {
        "menu": "RULES",
        "title": "Q2 RULES",
        "pages": screen(
            ["IF NO NONCONS", "WORK THEN MECH", "ENERGY CONS"],
            ["UG DEPENDS ON", "HEIGHT CHOICE", "BE CONSISTENT"],
            ["US USES X FROM", "NATURAL LENGTH", "NOT TOTAL LEN"],
            ["RAMP HEIGHT USE", "H=L SIN(TH)", "TH FROM HORIZ"],
            ["IF FRICTION OR", "PUSH EXISTS", "ADD WNC TERM"],
            ["STATE INITIAL", "AND FINAL", "BEFORE EQUATION"],
            ["GRAPH/BAR MUST", "MATCH YOUR", "EQUATION MODEL"],
        ),
    },
    {
        "menu": "EQS",
        "title": "Q2 EQS",
        "pages": screen(
            ["UG=MGH"],
            ["US=.5KX^2"],
            ["K=.5MV^2"],
            ["MECH:I + WNC=", "MECH:F"],
            ["REST TO REST:", "MGH=.5KX^2"],
            ["H=L SIN(TH)"],
            ["V^2=2(MGH-.5KX^2)/M"],
        ),
    },
    {
        "menu": "FLOW",
        "title": "Q2 FLOW",
        "pages": screen(
            ["DEFINE SYSTEM", "BLOCK+EARTH+", "SPRING AS NEEDED"],
            ["PICK TWO STATES", "TOP AND MAX X", "OR ANY POINT"],
            ["WRITE ENERGY EQ", "WITH TERMS AT", "EACH STATE"],
            ["SUB H=L SIN TH", "IF HEIGHT IS", "GEOMETRIC"],
            ["SOLVE ALGEBRA", "THEN CHECK", "PHYSICAL SIGN"],
            ["FOR BAR CHART", "SHOW TOTAL SAME", "IF CONSERVED"],
            ["IN JUSTIFICATION", "NAME LAW AND", "WHY VALID"],
        ),
    },
    {"menu": "SOLVE", "solver": solver_q2},
    {
        "menu": "TIPS",
        "title": "Q2 TIPS",
        "pages": screen(
            ["DO NOT MIX UP", "SPRING X WITH", "RAMP DISTANCE"],
            ["KX IS FORCE", "BUT US NEEDS", ".5KX^2"],
            ["NEGATIVE UNDER", "ROOT MEANS", "BAD ASSUMPTION"],
            ["AT MAX X SPEED", "IS ZERO NOT", "ACCEL ZERO"],
            ["IF MASS CANCELS", "SAY IT FROM", "THE EQUATION"],
            ["LABEL UNITS:", "K N/M X M", "ENERGY J"],
        ),
    },
]


Q3_ITEMS = [
    {
        "menu": "SCENARIO",
        "title": "Q3 SCENE",
        "pages": screen(
            ["METERSTICK HELD", "AT ANGLE THETA", "WITH TENSION"],
            ["USE TORQUE EQ", "TO LINK FORCE", "AND MASS"],
            ["PART A OFTEN", "ASKS FOR DESIGN", "AND PROCEDURE"],
            ["PART B OFTEN", "ASKS GRAPH +", "BEST FIT SLOPE"],
            ["LINEARIZE DATA", "TO EXTRACT", "UNKNOWN M"],
        ),
    },
    {
        "menu": "RULES",
        "title": "Q3 RULES",
        "pages": screen(
            ["CHOOSE A PIVOT", "TO REMOVE ONE", "UNKNOWN TORQUE"],
            ["TAU=R F SINTH", "USE PERP PART", "ONLY"],
            ["SET CW NEG AND", "CCW POS OR", "VICE VERSA"],
            ["STATIC EQUIL:", "SUM TAU=0 AND", "SUM F=0"],
            ["VARY ONE INPUT", "PER TRIAL KEEP", "OTHERS FIXED"],
            ["REPEAT TRIALS", "AND USE AVG", "TO CUT NOISE"],
            ["GRAPH AXES MUST", "MATCH LINEAR", "MODEL FORM"],
        ),
    },
    {
        "menu": "EQS",
        "title": "Q3 EQS",
        "pages": screen(
            ["TAU=RFSIN(TH)"],
            ["SUM TAU ABOUT", "PIVOT = 0"],
            ["AP 2025 FORM:", "FT=5MG/(6SINTH)"],
            ["LET Y=FT"],
            ["LET X=1/SINTH"],
            ["SLOPE=5MG/6"],
            ["M=6*SLOPE/(5G)"],
        ),
    },
    {
        "menu": "FLOW",
        "title": "Q3 FLOW",
        "pages": screen(
            ["DESIGN: LIST", "EQUIP + WHAT", "YOU MEASURE"],
            ["SET APPARATUS", "SO THETA CAN", "BE CHANGED"],
            ["FOR EACH TRIAL", "MEASURE THETA", "AND FT"],
            ["COMPUTE X=1/SIN", "FOR EACH POINT", "IN TABLE"],
            ["PLOT Y=FT VS X", "DRAW BEST FIT", "NOT DOT CONNECT"],
            ["READ SLOPE WITH", "UNITS THEN", "SOLVE FOR M"],
            ["DISCUSS ERROR:", "ANGLE READ", "SCALE CALIB"],
        ),
    },
    {"menu": "SOLVE", "solver": solver_q3},
    {
        "menu": "TIPS",
        "title": "Q3 TIPS",
        "pages": screen(
            ["DEGREES MODE", "MATTERS FOR", "SIN THETA"],
            ["SINTH=0 IS BAD", "AT 0 OR 180", "MODEL FAILS"],
            ["SLOPE UNITS HELP", "CHECK MASS", "DIMENSIONS"],
            ["DO NOT FORCE", "INTERCEPT 0", "UNLESS DERIVED"],
            ["SHOW WHY LINEAR", "WITH Y=MX+B", "MAPPING"],
            ["CLEAR FREE BODY", "AND PIVOT MARK", "EARNS POINTS"],
        ),
    },
]


Q4_ITEMS = [
    {
        "menu": "SCENARIO",
        "title": "Q4 SCENE",
        "pages": screen(
            ["BLOCK SUBMERGED", "IN FLUID THEN", "RELEASED"],
            ["UP FORCE IS", "BUOYANCY", "DOWN IS WEIGHT"],
            ["COMPARE MOTION", "IN FLUIDS WITH", "DIFF DENSITY"],
            ["HIGHER RHO FLUID", "MEANS BIGGER FB", "SAME V"],
            ["THAT CHANGES NET", "FORCE AND THUS", "ACCELERATION"],
        ),
    },
    {
        "menu": "RULES",
        "title": "Q4 RULES",
        "pages": screen(
            ["DRAW FBD FIRST", "FB UP MG DOWN", "SET + UP"],
            ["USE N2L: SUM F", "= M A ALONG", "ONE AXIS"],
            ["FOR FULL SUBMERGE", "DISPLACED V IS", "BLOCK V"],
            ["FB=RHO V G USE", "FLUID RHO NOT", "BLOCK RHO"],
            ["SAME BLOCK MEANS", "M AND V FIXED", "BETWEEN FLUIDS"],
            ["COMPARE SIGNS:", "A POS UP WHEN", "FB > MG"],
            ["JUSTIFY WITH", "CAUSE CHAIN", "RHO->FB->A"],
        ),
    },
    {
        "menu": "EQS",
        "title": "Q4 EQS",
        "pages": screen(
            ["FB=RHO V G"],
            ["FG=MG"],
            ["SUM F=FB-FG=MA"],
            ["A=(RHO V G-MG)/M"],
            ["NEUTRAL WHEN", "RHO=M/V"],
            ["DA=G V(R2-R1)/M", "SAME BLOCK CASE"],
            ["IF RHO V < M", "A IS NEGATIVE", "DOWNWARD"],
        ),
    },
    {
        "menu": "FLOW",
        "title": "Q4 FLOW",
        "pages": screen(
            ["STATE SYSTEM AND", "SIGN DIRECTION", "AT START"],
            ["WRITE FB AND FG", "THEN NET FORCE", "SYMBOLICALLY"],
            ["SOLVE FOR A", "BEFORE NUMBERS", "TO SHOW LOGIC"],
            ["FOR COMPARISON", "HOLD M V G FIX", "CHANGE RHO"],
            ["EXPLAIN WORDS:", "BIGGER RHO ->", "BIGGER FB"],
            ["THEN BIGGER", "FB-MG -> BIGGER", "UPWARD A"],
            ["CHECK LIMIT:", "RHO=0 GIVES", "A=-G"],
        ),
    },
    {"menu": "SOLVE", "solver": solver_q4},
    {
        "menu": "TIPS",
        "title": "Q4 TIPS",
        "pages": screen(
            ["DO NOT USE", "PRESSURE EQ ALONE", "WITHOUT FB STEP"],
            ["DENSITY OF FLUID", "IS CONTROL KNOB", "IN COMPARISON"],
            ["UNITS CHECK:", "RHO KG/M^3", "FB IN N"],
            ["IF PARTIAL SUB", "USE DISPLACED V", "NOT TOTAL V"],
            ["A CAN CHANGE", "SIGN WITH FLUID", "DENSITY"],
            ["EXPLAIN WITH FBD", "NOT JUST FINAL", "NUMBER"],
        ),
    },
]


FS_ITEMS = [
    {
        "menu": "COMMANDS",
        "title": "CMD WORDS",
        "pages": screen(
            ["DESCRIBE: WHAT", "HAPPENS + TREND", "NO MATH NEEDED"],
            ["EXPLAIN: WHAT +", "WHY USING LAW", "AND CONTEXT"],
            ["JUSTIFY: CLAIM", "EVIDENCE FROM", "MODEL OR DATA"],
            ["DERIVE: START", "GENERAL EQN", "SHOW ALGEBRA"],
            ["COMPARE: SAME OR", "DIFF THEN WHY", "WITH PHYSICS"],
        ),
    },
    {
        "menu": "CER",
        "title": "CER",
        "pages": screen(
            ["CLAIM: DIRECT", "ANSWER TO ASK", "IN ONE LINE"],
            ["EVIDENCE: EQN", "DATA OR GRAPH", "VALUE"],
            ["REASONING:", "CONNECT EVIDENCE", "TO CLAIM"],
            ["USE BECAUSE", "SO THAT LOGIC", "IN SENTENCES"],
            ["FINISH WITH", "UNITS AND SIGN", "INTERPRETATION"],
        ),
    },
    {
        "menu": "GRAPHS",
        "title": "GRAPH",
        "pages": screen(
            ["LABEL AXES WITH", "SYMBOL + UNITS", "BEFORE PLOT"],
            ["CHOOSE SCALE", "THAT USES MOST", "OF GRID"],
            ["PLOT POINTS", "CLEARLY THEN", "BEST FIT LINE"],
            ["SLOPE USE TWO", "FAR APART PTS", "ON BEST FIT"],
            ["INTERCEPT MUST", "MATCH MODEL", "OR EXPLAIN"],
        ),
    },
    {
        "menu": "LAB DESIGN",
        "title": "LAB",
        "pages": screen(
            ["NAME WHAT YOU", "CONTROL CHANGE", "MEASURE"],
            ["CHANGE ONE IV", "KEEP OTHERS", "CONSTANT"],
            ["MULTIPLE TRIALS", "AVERAGE RESULT", "CUT RANDOM ERR"],
            ["STATE TOOLS AND", "HOW VALUES ARE", "READ"],
            ["MENTION MAIN", "UNCERTAINTY AND", "ITS EFFECT"],
        ),
    },
    {
        "menu": "UNIT CHECK",
        "title": "UNITS",
        "pages": screen(
            ["MKS DEFAULT:", "M KG S N J", "PA"],
            ["WRITE UNITS IN", "EACH FINAL", "NUMERIC ANSWER"],
            ["CHECK SLOPE UNIT", "TO IDENTIFY", "PHYS QUANTITY"],
            ["DIMENSION FAIL", "MEANS ALGEBRA", "OR MODEL ERROR"],
        ),
    },
    {
        "menu": "COMMON ERR",
        "title": "TRAPS",
        "pages": screen(
            ["USING SPEED WHEN", "VECTOR SIGN", "IS REQUIRED"],
            ["ASSUMING CONS LAW", "WITHOUT SYSTEM", "AND CONDITIONS"],
            ["SKIPPING FREE", "BODY OR ENERGY", "STATE DIAGRAM"],
            ["FINAL NUMBER", "WITHOUT EXPLAIN", "LOSES REASONING"],
            ["FORGETTING LIMIT", "CHECK FOR", "PHYS SENSE"],
        ),
    },
]


EF_ITEMS = [
    {
        "menu": "START",
        "title": "EXAM FLOW",
        "pages": screen(
            ["SCAN ALL PARTS", "MARK EASY POINTS", "FIRST"],
            ["SET AXES SIGN", "AND SYSTEM EARLY", "AVOID REWORK"],
            ["WRITE TARGET EQN", "SYMBOLIC FIRST", "THEN NUMBERS"],
            ["BOX FINAL WITH", "UNITS SIGN", "AND DIRECTION"],
        ),
    },
    {
        "menu": "MID PASS",
        "title": "EXAM FLOW",
        "pages": screen(
            ["AFTER EACH PART", "ASK: DID I USE", "RIGHT LAW"],
            ["IF STUCK SWITCH", "TO NEXT PART", "COME BACK"],
            ["USE GIVEN INFO", "GRAPH OR TABLE", "AS EVIDENCE"],
            ["KEEP WORK CLEAN", "SO PARTIAL", "CREDIT IS CLEAR"],
        ),
    },
    {
        "menu": "FINAL CHECK",
        "title": "EXAM FLOW",
        "pages": screen(
            ["CHECK SIGNS", "UP OR DOWN", "LEFT OR RIGHT"],
            ["CHECK LIMITS", "EXTREME VALUES", "MAKE SENSE"],
            ["CHECK DECIMAL", "AND ROUNDING", "AT THE END"],
            ["CHECK WORD ASK", "COMPARE EXPLAIN", "JUSTIFY MATCH"],
        ),
    },
    {
        "menu": "MENTAL MAP",
        "title": "RULE MAP",
        "pages": screen(
            ["MOTION CHANGE?", "LOOK AT NET F", "OR IMPULSE"],
            ["ROTATION STATIC?", "SUM TAU=0", "AND SUM F=0"],
            ["ENERGY STATE?", "TRACK K UG US", "PLUS LOSSES"],
            ["FLUID FORCE?", "FB=RHO V G", "THEN N2L"],
            ["COLLISION?", "MOMENTUM FIRST", "KE SECOND"],
        ),
    },
]


def build():
    lines = [
        "Degree",
        "ClrHome",
        'Disp "PHYFRQ25"',
        'Disp "AP PHYS 1"',
        'Disp "FRQ COACH"',
        "Pause",
        f"Lbl {H}",
        "ClrHome",
        f'Menu("FRQ HOME","Q1 MOM+ENER",{Q1},"Q2 EN+SPR",{Q2},"Q3 TORQUE",{Q3},"Q4 FLUID",{Q4},"FRQ SKILLS",{FS},"EXAM FLOW",{EF},"EXIT",{EX})',
    ]

    add_topic(lines, Q1, "Q1 MOM+KE", Q1_ITEMS, H)
    add_topic(lines, Q2, "Q2 EN+SPRING", Q2_ITEMS, H)
    add_topic(lines, Q3, "Q3 TORQUE", Q3_ITEMS, H)
    add_topic(lines, Q4, "Q4 BUOYANCY", Q4_ITEMS, H)
    add_topic(lines, FS, "FRQ SKILLS", FS_ITEMS, H)
    add_topic(lines, EF, "EXAM FLOW", EF_ITEMS, H)

    for label, (msg, back) in BAD.items():
        lines += [f"Lbl {label}", "ClrHome", f'Disp "{msg}"']
        add_solver_result_nav(lines, back)

    lines += [f"Lbl {EX}", "ClrHome", 'Disp "PHYFRQ25 END"', "Stop"]
    return lines


TOKENS = {
    "->": bytes([0x04]),
    "sin(": bytes([0xC2]),
    "cos(": bytes([0xC4]),
    "Degree": bytes([0x65]),
    "Menu(": bytes([0xE6]),
    "ClrHome": bytes([0xE1]),
    "Disp": bytes([0xDE]),
    "Input": bytes([0xDC]),
    "Lbl": bytes([0xD6]),
    "Goto": bytes([0xD7]),
    "Pause": bytes([0xD8]),
    "Stop": bytes([0xD9]),
    "If": bytes([0xCE]),
    "Then": bytes([0xCF]),
    "Else": bytes([0xD0]),
    "End": bytes([0xD4]),
}

CHAR = {
    " ": 0x29,
    '"': 0x2A,
    ",": 0x2B,
    ".": 0x3A,
    ":": 0x3F,
    "0": 0x30,
    "1": 0x31,
    "2": 0x32,
    "3": 0x33,
    "4": 0x34,
    "5": 0x35,
    "6": 0x36,
    "7": 0x37,
    "8": 0x38,
    "9": 0x39,
    "=": 0x6A,
    "<": 0x6B,
    ">": 0x6C,
    "+": 0x70,
    "-": 0x71,
    "*": 0x82,
    "/": 0x83,
    "(": 0x10,
    ")": 0x11,
    "^": 0xF0,
    "?": 0xAF,
}
for i, ch in enumerate(string.ascii_uppercase):
    CHAR[ch] = 0x41 + i

ORDERED = sorted(TOKENS.items(), key=lambda kv: len(kv[0]), reverse=True)


def tokenize_line(line):
    out = bytearray()
    i = 0
    in_quote = False
    while i < len(line):
        ch = line[i]
        if ch == '"':
            out.append(CHAR[ch])
            in_quote = not in_quote
            i += 1
            continue
        if not in_quote:
            if ch == " ":
                i += 1
                continue
            matched = False
            for text, tok in ORDERED:
                if line.startswith(text, i):
                    out.extend(tok)
                    i += len(text)
                    matched = True
                    break
            if matched:
                continue
        if ch in CHAR:
            out.append(CHAR[ch])
            i += 1
            continue
        raise ValueError(f"Cannot tokenize {ch!r} in line: {line}")
    return bytes(out)


def tokenize(lines):
    out = bytearray()
    for idx, line in enumerate(lines):
        out.extend(tokenize_line(line))
        if idx != len(lines) - 1:
            out.append(0x3F)
    return bytes(out)


def make_8xp(tokens):
    data = len(tokens).to_bytes(2, "little") + tokens
    data_len = len(data)
    name = NAME.encode("ascii").ljust(8, b"\x00")
    entry = (
        b"\x0D\x00"
        + data_len.to_bytes(2, "little")
        + b"\x05"
        + name
        + b"\x00\x00"
        + data_len.to_bytes(2, "little")
        + data
    )
    comment = b"PHYFRQ25 AP PHYSICS 1 FRQ".ljust(42, b" ")
    header = b"**TI83F*" + b"\x1A\x0A\x00" + comment + len(entry).to_bytes(2, "little")
    checksum = (sum(entry) & 0xFFFF).to_bytes(2, "little")
    return header + entry + checksum


def validate_8xp(blob):
    if blob[:8] != b"**TI83F*":
        raise ValueError("bad signature")
    section_len = int.from_bytes(blob[53:55], "little")
    entry = blob[55:55 + section_len]
    got = int.from_bytes(blob[55 + section_len:57 + section_len], "little")
    calc = sum(entry) & 0xFFFF
    if got != calc:
        raise ValueError(f"bad checksum {got} != {calc}")
    var = entry[5:13].rstrip(b"\x00").decode("ascii")
    if var != NAME:
        raise ValueError(f"bad name {var}")
    prog_len = int.from_bytes(entry[15:17], "little")
    tok_len = int.from_bytes(entry[17:19], "little")
    if prog_len != tok_len + 2:
        raise ValueError("program length mismatch")
    return section_len, tok_len


if __name__ == "__main__":
    lines = build()
    source = "\n".join(lines) + "\n"
    tokens = tokenize(lines)
    blob = make_8xp(tokens)
    section_len, tok_len = validate_8xp(blob)
    (OUT / f"{NAME}.8xp.txt").write_text(source, encoding="ascii")
    (OUT / f"{NAME}.8xp").write_bytes(blob)
    print(f"Wrote {NAME}.8xp.txt ({len(lines)} lines)")
    print(f"Wrote {NAME}.8xp ({len(blob)} bytes, {tok_len} token bytes, section {section_len})")
