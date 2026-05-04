from pathlib import Path
import string

OUT = Path(__file__).resolve().parent
NAME = "PHYTREE"

USED = set()

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
M2 = use("M2")
EX = use("EX")
KI = use("KI")
DY = use("DY")
EN = use("EN")
MO = use("MO")
RO = use("RO")
R2 = use("R2")
SH = use("SH")
FL = use("FL")
GR = use("GR")
QP = use("QP")
Q2 = use("Q2")
Z = use("Z")
Z0 = use("Z0")

BAD = {}
CUSTOM = {}

def page(*lines):
    return list(lines)

def pages(*ps):
    return [list(p) for p in ps]

def screen(lines, title=None):
    if not lines:
        return [["NO NOTES"]]
    if isinstance(lines[0], str):
        return [list(lines)]
    return [list(p) for p in lines]

def add_text(lines, label, title, text_pages, back):
    lines += [f"Lbl {label}"]
    for i, pg in enumerate(text_pages):
        lines += ["ClrHome"]
        if title:
            lines.append(f'Disp "{title}"')
        for item in pg:
            lines.append(f'Disp "{item}"')
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

def solver_avg_accel(lines, back):
    bad = bad_label("T CANT BE 0", back)
    lines += [
        'ClrHome',
        'Input "VI M/S",A',
        'Input "VF M/S",B',
        'Input "T S",C',
        'If C=0',
        'Then',
        f'Goto {bad}',
        'End',
        '(B-A)/C->D',
        'ClrHome',
        'Disp "AAVG=",D',
    ]
    add_solver_result_nav(lines, back)

def solver_freefall_ratio(lines, back):
    bad = bad_label("T1 CANT BE 0", back)
    lines += [
        'ClrHome',
        'Input "D1",A',
        'Input "T1",B',
        'Input "T2",C',
        'If B=0',
        'Then',
        f'Goto {bad}',
        'End',
        'A*C^2/B^2->D',
        'ClrHome',
        'Disp "D2=",D',
    ]
    add_solver_result_nav(lines, back)

def solver_projectile_time(lines, back):
    bad = bad_label("G CANT BE 0", back)
    lines += [
        'ClrHome',
        'Disp "DEG MODE"',
        'Input "V0 M/S",A',
        'Input "TH DEG",B',
        'Input "G",C',
        'If C=0',
        'Then',
        f'Goto {bad}',
        'End',
        '2*A*sin(B)/C->D',
        'ClrHome',
        'Disp "AIR TIME=",D',
    ]
    add_solver_result_nav(lines, back)

def solver_no(lines, back):
    lines += ['ClrHome', 'Disp "CONCEPT ONLY"', 'Disp "USE HELP/STEPS"']
    add_solver_result_nav(lines, back)

def solver_friction(lines, back):
    bad = bad_label("MU OR G ZERO", back)
    lines += [
        'ClrHome',
        'Input "V M/S",A',
        'Input "MU",B',
        'Input "G",C',
        'If B*C=0',
        'Then',
        f'Goto {bad}',
        'End',
        'A^2/(2*B*C)->D',
        'ClrHome',
        'Disp "STOP D=",D',
    ]
    add_solver_result_nav(lines, back)

def solver_net_force(lines, back):
    lines += [
        'ClrHome',
        'Input "FX+",A',
        'Input "FX-",B',
        'Input "FY+",C',
        'Input "FY-",D',
        'A-B->E',
        'C-D->F',
        '(E^2+F^2)^.5->G',
        'ClrHome',
        'Disp "FNETX=",E',
        'Disp "FNETY=",F',
        'Disp "MAG=",G',
    ]
    add_solver_result_nav(lines, back)

def solver_div(lines, back, prompts, expr, out, badmsg):
    bad = bad_label(badmsg, back)
    lines += ['ClrHome']
    for s, v in prompts:
        lines.append(f'Input "{s}",{v}')
    lines += [
        'If B=0',
        'Then',
        f'Goto {bad}',
        'End',
        f'{expr}->D',
        'ClrHome',
        f'Disp "{out}=",D',
    ]
    add_solver_result_nav(lines, back)

def solver_power(lines, back):
    lines += [
        'ClrHome',
        'Input "M KG",A',
        'Input "ACC",B',
        'Input "V",C',
        'A*B*C->D',
        'ClrHome',
        'Disp "P=",D',
    ]
    add_solver_result_nav(lines, back)

def solver_work(lines, back):
    lines += [
        'ClrHome',
        'Disp "DEG MODE"',
        'Input "F N",A',
        'Input "D M",B',
        'Input "TH DEG",C',
        'A*B*cos(C)->D',
        'ClrHome',
        'Disp "WORK=",D',
    ]
    add_solver_result_nav(lines, back)

def solver_stick(lines, back):
    bad = bad_label("M SUM ZERO", back)
    lines += [
        'ClrHome',
        'Input "M1",A',
        'Input "V1",B',
        'Input "M2",C',
        'Input "V2",D',
        'If A+C=0',
        'Then',
        f'Goto {bad}',
        'End',
        '(A*B+C*D)/(A+C)->E',
        'ClrHome',
        'Disp "VF=",E',
    ]
    add_solver_result_nav(lines, back)

def solver_wall(lines, back):
    ln = alloc()
    ls = alloc()
    lines += [
        f'Menu("ANGLE","FROM NORM",{ln},"FROM WALL",{ls},"BACK",{back})',
        f'Lbl {ln}',
        'ClrHome',
        'Input "M",A',
        'Input "V",B',
        'Input "TH DEG",C',
        '2*A*B*cos(C)->D',
        'ClrHome',
        'Disp "IMP=",D',
    ]
    add_solver_result_nav(lines, back)
    lines += [
        f'Lbl {ls}',
        'ClrHome',
        'Input "M",A',
        'Input "V",B',
        'Input "TH DEG",C',
        '2*A*B*sin(C)->D',
        'ClrHome',
        'Disp "IMP=",D',
    ]
    add_solver_result_nav(lines, back)

def solver_torque_eq(lines, back):
    lf = alloc()
    ld = alloc()
    badf = bad_label("D2 CANT BE 0", back)
    badd = bad_label("F2 CANT BE 0", back)
    lines += [
        f'Menu("MISS","FORCE",{lf},"DIST",{ld},"BACK",{back})',
        f'Lbl {lf}',
        'ClrHome',
        'Input "F1",A',
        'Input "D1",B',
        'Input "D2",C',
        'If C=0',
        'Then',
        f'Goto {badf}',
        'End',
        'A*B/C->D',
        'ClrHome',
        'Disp "F2=",D',
    ]
    add_solver_result_nav(lines, back)
    lines += [
        f'Lbl {ld}',
        'ClrHome',
        'Input "F1",A',
        'Input "D1",B',
        'Input "F2",C',
        'If C=0',
        'Then',
        f'Goto {badd}',
        'End',
        'A*B/C->D',
        'ClrHome',
        'Disp "D2=",D',
    ]
    add_solver_result_nav(lines, back)

def solver_alpha(lines, back):
    l1 = alloc()
    l2 = alloc()
    l3 = alloc()
    b1 = bad_label("T CANT BE 0", back)
    b2 = bad_label("T CANT BE 0", back)
    b3 = bad_label("TH CANT BE 0", back)
    lines += [
        f'Menu("ALPHA","WF WI T",{l1},"TH WI T",{l2},"WF WI TH",{l3},"BACK",{back})',
        f'Lbl {l1}',
        'ClrHome',
        'Input "WI",A',
        'Input "WF",B',
        'Input "T",C',
        'If C=0',
        'Then',
        f'Goto {b1}',
        'End',
        '(B-A)/C->D',
        'ClrHome',
        'Disp "ALPHA=",D',
    ]
    add_solver_result_nav(lines, back)
    lines += [
        f'Lbl {l2}',
        'ClrHome',
        'Input "THETA",A',
        'Input "WI",B',
        'Input "T",C',
        'If C=0',
        'Then',
        f'Goto {b2}',
        'End',
        '2*(A-B*C)/C^2->D',
        'ClrHome',
        'Disp "ALPHA=",D',
    ]
    add_solver_result_nav(lines, back)
    lines += [
        f'Lbl {l3}',
        'ClrHome',
        'Input "WI",A',
        'Input "WF",B',
        'Input "THETA",C',
        'If C=0',
        'Then',
        f'Goto {b3}',
        'End',
        '(B^2-A^2)/(2*C)->D',
        'ClrHome',
        'Disp "ALPHA=",D',
    ]
    add_solver_result_nav(lines, back)

def solver_revs(lines, back):
    bad = bad_label("A CANT BE 0", back)
    lines += [
        'ClrHome',
        'Input "WI",A',
        'Input "WF",B',
        'Input "ALPHA",C',
        'If C=0',
        'Then',
        f'Goto {bad}',
        'End',
        '(B^2-A^2)/(2*C)->D',
        'D/(2*3.14159265)->E',
        'ClrHome',
        'Disp "THETA=",D',
        'Disp "REV=",E',
    ]
    add_solver_result_nav(lines, back)

def solver_ang_disp(lines, back):
    la = alloc()
    lt = alloc()
    l0 = alloc()
    ba = bad_label("A CANT BE 0", back)
    lines += [
        f'Menu("THETA","WI WF A",{la},"WI WF T",{lt},"WI0 WF A",{l0},"BACK",{back})',
        f'Lbl {la}',
        'ClrHome',
        'Input "WI",A',
        'Input "WF",B',
        'Input "ALPHA",C',
        'If C=0',
        'Then',
        f'Goto {ba}',
        'End',
        '(B^2-A^2)/(2*C)->D',
        'D/(2*3.14159265)->E',
        'ClrHome',
        'Disp "THETA=",D',
        'Disp "REV=",E',
    ]
    add_solver_result_nav(lines, back)
    lines += [
        f'Lbl {lt}',
        'ClrHome',
        'Input "WI",A',
        'Input "WF",B',
        'Input "T",C',
        '.5*(A+B)*C->D',
        'D/(2*3.14159265)->E',
        'ClrHome',
        'Disp "THETA=",D',
        'Disp "REV=",E',
    ]
    add_solver_result_nav(lines, back)
    lines += [
        f'Lbl {l0}',
        'ClrHome',
        'Input "WF",B',
        'Input "ALPHA",C',
        'If C=0',
        'Then',
        f'Goto {ba}',
        'End',
        'B^2/(2*C)->D',
        'D/(2*3.14159265)->E',
        'ClrHome',
        'Disp "THETA=",D',
        'Disp "REV=",E',
    ]
    add_solver_result_nav(lines, back)

def solver_inertia(lines, back):
    lh = alloc()
    ld = alloc()
    ls = alloc()
    lc = alloc()
    le = alloc()
    lines += [
        f'Menu("I OBJECT","HOOP",{lh},"DISK",{ld},"SPHERE",{ls},"ROD CTR",{lc},"ROD END",{le},"BACK",{back})',
        f'Lbl {lh}',
        'ClrHome',
        'Input "M",A',
        'Input "R",B',
        'A*B^2->D',
        'ClrHome',
        'Disp "I=",D',
    ]
    add_solver_result_nav(lines, back)
    lines += [
        f'Lbl {ld}',
        'ClrHome',
        'Input "M",A',
        'Input "R",B',
        '.5*A*B^2->D',
        'ClrHome',
        'Disp "I=",D',
    ]
    add_solver_result_nav(lines, back)
    lines += [
        f'Lbl {ls}',
        'ClrHome',
        'Input "M",A',
        'Input "R",B',
        '.4*A*B^2->D',
        'ClrHome',
        'Disp "I=",D',
    ]
    add_solver_result_nav(lines, back)
    lines += [
        f'Lbl {lc}',
        'ClrHome',
        'Input "M",A',
        'Input "L",B',
        'A*B^2/12->D',
        'ClrHome',
        'Disp "I=",D',
    ]
    add_solver_result_nav(lines, back)
    lines += [
        f'Lbl {le}',
        'ClrHome',
        'Input "M",A',
        'Input "L",B',
        'A*B^2/3->D',
        'ClrHome',
        'Disp "I=",D',
    ]
    add_solver_result_nav(lines, back)

def solver_lmvr(lines, back):
    lines += [
        'ClrHome',
        'Input "M",A',
        'Input "V",B',
        'Input "RPERP",C',
        'A*B*C->D',
        'ClrHome',
        'Disp "L=",D',
    ]
    add_solver_result_nav(lines, back)

def solver_2body_l(lines, back):
    lines += [
        'ClrHome',
        'Disp "SIGN +1/-1"',
        'Input "M1",A',
        'Input "V1",B',
        'Input "R1",C',
        'Input "S1",D',
        'Input "M2",E',
        'Input "V2",F',
        'Input "R2",G',
        'Input "S2",H',
        'D*A*B*C+H*E*F*G->I',
        'ClrHome',
        'Disp "L SUM=",I',
    ]
    add_solver_result_nav(lines, back)

def solver_shm_time(lines, back):
    bad = bad_label("W CANT BE 0", back)
    lines += [
        'ClrHome',
        'Input "OMEGA",A',
        'If A=0',
        'Then',
        f'Goto {bad}',
        'End',
        '3.14159265/(2*A)->B',
        'ClrHome',
        'Disp "T EQM=",B',
    ]
    add_solver_result_nav(lines, back)

def solver_density(lines, back):
    bad = bad_label("V OR G ZERO", back)
    lines += [
        'ClrHome',
        'Input "W EMPTY",A',
        'Input "W FULL",B',
        'Input "VOL",C',
        'Input "G",D',
        'If C*D=0',
        'Then',
        f'Goto {bad}',
        'End',
        '(B-A)/D->E',
        'E/C->F',
        'ClrHome',
        'Disp "MASS=",E',
        'Disp "RHO=",F',
    ]
    add_solver_result_nav(lines, back)

def solver_pressure(lines, back):
    lines += [
        'ClrHome',
        'Input "RHO",A',
        'Input "G",B',
        'Input "H",C',
        'Input "AREA",D',
        'A*B*C*D->E',
        'ClrHome',
        'Disp "F=",E',
        'Disp "NO ATM P"',
    ]
    add_solver_result_nav(lines, back)

def solver_slope(lines, back):
    bad = bad_label("DT CANT BE 0", back)
    lines += [
        'ClrHome',
        'Input "X1",A',
        'Input "T1",B',
        'Input "X2",C',
        'Input "T2",D',
        'If D-B=0',
        'Then',
        f'Goto {bad}',
        'End',
        '(C-A)/(D-B)->E',
        'ClrHome',
        'Disp "SLOPE/V=",E',
    ]
    add_solver_result_nav(lines, back)

def solver_momentum_graph(lines, back):
    lines += [
        'ClrHome',
        'Input "MASS",A',
        'Input "VEL",B',
        'A*B->C',
        'ClrHome',
        'Disp "P=",C',
    ]
    add_solver_result_nav(lines, back)

def solver_spring_k(lines, back):
    bad = bad_label("DX CANT BE 0", back)
    lines += [
        'ClrHome',
        'Input "F1",A',
        'Input "X1",B',
        'Input "F2",C',
        'Input "X2",D',
        'If D-B=0',
        'Then',
        f'Goto {bad}',
        'End',
        '(C-A)/(D-B)->E',
        'ClrHome',
        'Disp "K=",E',
    ]
    add_solver_result_nav(lines, back)

def solve_placeholder(lines, back):
    solver_no(lines, back)

DEFINITIONS = [
    ("Z1", "EQUIL", "EQUIL", [
        ["EQUILIBRIUM", "MEANS A=0", "FNET=0"],
        ["STATIC: V=0", "DYNAMIC: V CONST", "BOTH A=0"],
        ["ROT EQ TOO:", "TAU NET=0", "NO ANG ACC"],
        ["TRAP:", "V=0 ALONE", "NOT ENOUGH"],
    ]),
    ("Z2", "SHM", "SHM", [
        ["SHM REQUIRES", "RESTORE FORCE", "TOWARD EQ"],
        ["FORCE MUST BE", "PROPORTIONAL", "TO DISPLACE"],
        ["F=-KX", "A=-W^2X", "PERIOD FIXED"],
        ["TRAP:", "REPEATS NOT", "ALWAYS SHM"],
    ]),
    ("Z3", "CONSERVED", "CONSERVED", [
        ["CONSERVED MEANS", "TOTAL SAME", "FOR SYSTEM"],
        ["P CONSERVED IF", "NO EXT IMPULSE"],
        ["L CONSERVED IF", "NO EXT TORQUE"],
        ["MECH ENERGY IF", "NO NONCONS WORK"],
    ]),
    ("Z4", "SYSTEMS", "SYSTEM", [
        ["SYSTEM CHOICE", "DECIDES INT/EXT", "FORCES"],
        ["INTERNAL FORCES", "CAN MOVE ENERGY", "INSIDE SYSTEM"],
        ["EXTERNAL WORK", "CHANGES SYSTEM", "ENERGY/MOM"],
        ["TRAP:", "DEFINE SYSTEM", "BEFORE FORMULA"],
    ]),
    ("Z5", "GRAPHS", "GRAPHS", [
        ["SLOPE MEANS", "Y CHANGE OVER", "X CHANGE"],
        ["AREA UNDER", "GRAPH CAN MEAN", "ACCUMULATION"],
        ["SHAPE CHECK:", "LINEAR VS QUAD", "VS INVERSE"],
        ["TRAP:", "READ AXES", "BEFORE EQUATION"],
    ]),
    ("Z6", "IMPULSE", "IMPULSE", [
        ["IMPULSE IS", "CHANGE IN MOM", "J=DELTA P"],
        ["FAVG=J/DT", "SAME DT MEANS", "MORE J MORE F"],
        ["BOUNCE HAS", "BIG DELTA P", "DIR REVERSES"],
        ["WALL TRAP:", "ONLY PERP MOM", "CHANGES"],
    ]),
    ("Z7", "TORQUE", "TORQUE", [
        ["TORQUE CAUSES", "ANGULAR ACCEL", "TAU=RF SINTH"],
        ["USE PERP DIST", "OR PERP FORCE", "NOT BOTH"],
        ["ABOUT CENTER:", "CENTRAL FORCE", "GIVES TAU=0"],
        ["TRAP:", "AXIS CHOICE", "MATTERS"],
    ]),
    ("Z8", "FRQ WORDS", "FRQ WORDS", [
        ["JUSTIFY:", "CLAIM PLUS", "PHYSICS REASON"],
        ["DERIVE:", "START GENERAL", "SHOW ALGEBRA"],
        ["COMPARE:", "SAME/DIFF AND", "WHY"],
        ["GRAPH:", "AXES UNITS", "SHAPE SLOPE"],
    ]),
]

TOPICS = [
    (KI, "KIN", [
        ("K1", "AVG ACCEL", "AVG A", solver_avg_accel,
         ["AVERAGE ACCEL", "IS CHANGE IN", "VELOCITY/TIME"],
         ["A=(VF-VI)/T"],
         ["CHOOSE + DIR", "DO VF-VI", "DIVIDE BY T"],
         ["TIME NOT ZERO", "SIGNS MATTER"]),
        ("K2", "FREE FALL", "T^2", solver_freefall_ratio,
         ["FROM REST:", "DISTANCE GROWS", "LIKE TIME^2"],
         ["D2=D1(T2/T1)^2"],
         ["USE RATIO", "NO MASS NEEDED", "SAME G ONLY"],
         ["NOT LINEAR IN T", "2T MEANS 4D"]),
        ("K3", "PROJ TIME", "AIR TIME", solver_projectile_time,
         ["LEVEL GROUND:", "VERT MOTION", "SETS AIR TIME"],
         ["T=2V0SIN(TH)/G"],
         ["USE VY0", "TIME UP=VY0/G", "DOUBLE IT"],
         ["DEGREES MODE", "ONLY LEVEL LAND"]),
        ("K4", "UP/DOWN KE", "KE UP", solve_placeholder,
         ["MOVING UP BUT", "ACCEL DOWN:", "SPEED DROPS"],
         ["KE=.5MV^2"],
         ["KE USES SPEED", "SPEED DOWN", "MEANS KE DOWN"],
         ["DIRECTION NOT KE", "KE USES SPEED"]),
        ("K5", "TOP PATH", "TOP PATH", solve_placeholder,
         ["AT TOP:", "VY=0 BUT", "GRAVITY ACTS"],
         ["FNET=MG DOWN", "A=G DOWN"],
         ["EQUIL NEEDS", "FNET=0", "HERE FNET DOWN"],
         ["V=0 NOT ENOUGH", "VX CAN EXIST"]),
    ]),
    (DY, "DYN", [
        ("D1", "N3 GRAPH", "N3 PAIR", solve_placeholder,
         ["N3 PAIRS ACT", "ON DIFF OBJECTS", "SAME TIME"],
         ["FAB=-FBA"],
         ["MATCH TIMES", "SAME SIZE", "OPP SIGN"],
         ["DIFF OBJECTS", "NOT CANCEL"]),
        ("D2", "FRIC STOP", "FRIC STOP", solver_friction,
         ["KINETIC FRIC", "DOES NEG WORK", "UNTIL V=0"],
         ["D=V^2/(2MU G)"],
         ["F=MU MG", "A=MU G", "THEN USE KIN"],
         ["MASS CANCELS", "MU NOT M"]),
        ("D3", "FNET VEC", "FNET VEC", solver_net_force,
         ["ADD COMPONENTS", "X AND Y SEP"],
         ["FX=F+-F-", "MAG=(FX2+FY2)^.5"],
         ["SUM X", "SUM Y", "PYTHAG MAG"],
         ["SIGNS MATTER", "DO NOT ADD MAG"]),
        ("D4", "CIRC F->A", "F TO A", lambda l,b: solver_div(l,b,[("F N","A"),("M KG","B")],"A/B","A","M CANT BE 0"), 
         ["NET FORCE", "CAUSES ACCEL", "IN ITS DIR"],
         ["A=FNET/M"],
         ["ID NET F", "DIVIDE BY M", "DIR SAME AS F"],
         ["CENTRIPETAL IS", "NET INWARD"]),
        ("D5", "POWER A", "POWER", solver_power,
         ["SAME ACCEL", "F=MA", "POWER USES V"],
         ["P=FV=MAV"],
         ["FIND F", "MULT BY V"],
         ["SAME A NOT", "SAME POWER"]),
    ]),
    (EN, "ENERGY", [
        ("E1", "WORK ANGLE", "WORK", solver_work,
         ["ONLY PARALLEL", "FORCE DOES WORK"],
         ["W=FD COS(TH)"],
         ["USE FORCE COMP", "TH FROM MOTION"],
         ["90 DEG GIVES 0", "DEG MODE"]),
        ("E2", "INEL KE", "INELASTIC", solve_placeholder,
         ["STICK COLLISION:", "P CONSERVED", "KE NOT"],
         ["KI NOT = KF"],
         ["USE MOMENTUM", "FOR VF", "KE USUALLY LOST"],
         ["FINAL KE LESS", "P STILL CONS"]),
        ("E3", "MECH SYS", "SYSTEM", solve_placeholder,
         ["DEFINE SYSTEM", "BEFORE ENERGY", "EQUATIONS"],
         ["MECH=K+U"],
         ["IF PERSON EXT", "REMOVES ENERGY", "MECH DROPS"],
         ["EARTH-BOOK", "CAN LOSE MECH"]),
        ("E4", "RAMP ROLL", "RAMP", solve_placeholder,
         ["SLIDE NO FRIC", "ALL PE TO KTRANS"],
         ["ROLL SPLITS KE"],
         ["COMPARE ENERGY", "ROLL HAS ROT KE"],
         ["SLIDER FASTER", "IF NO LOSSES"]),
        ("E5", "PE TO KE", "PE DROP", solve_placeholder,
         ["SAME PE DROP", "SAME TOTAL KE", "NO LOSSES"],
         ["DELTA U=-DELTA K"],
         ["CHECK LOSSES", "THEN TOTAL KE"],
         ["ROLL SPLITS KE", "TOTAL CAN MATCH"]),
    ]),
    (MO, "MOM", [
        ("M1", "STICK VF", "STICK VF", solver_stick,
         ["OBJECTS STICK", "USE MOMENTUM"],
         ["VF=SUM P/SUM M"],
         ["CHOOSE + DIR", "SUM P BEFORE", "DIV MASS SUM"],
         ["KE NOT CONS", "SIGNS MATTER"]),
        ("M3", "EXP COM", "EXP COM", solve_placeholder,
         ["EXPLOSION:", "INTERNAL FORCES", "MOVE PIECES"],
         ["XCOM FOLLOWS", "OLD MOTION"],
         ["NO EXT FORCE:", "COM MOTION", "UNCHANGED"],
         ["COM NOT A PIECE", "EXT F CHANGES"]),
        ("M4", "BOUNCE F", "BOUNCE F", solve_placeholder,
         ["BOUNCE REVERSES", "MOMENTUM MORE"],
         ["J=DELTA P", "FAVG=J/DT"],
         ["FIND DELTA P", "DIV CONTACT T"],
         ["SAME DT:", "BIGGER J -> F"]),
        ("M5", "WALL IMP", "WALL IMP", solver_wall,
         ["ONLY PERP", "MOMENTUM CHG"],
         ["NORM:2MVCOS", "WALL:2MVSIN"],
         ["FIND ANGLE REF", "USE PERP COMP"],
         ["PARALLEL SAME", "ANGLE REF TRAP"]),
        ("M6", "RAFT COM", "RAFT COM", solve_placeholder,
         ["NO EXT HORIZ F", "COM FIXED"],
         ["SUM MX CONST"],
         ["PERSON MOVES", "RAFT SHIFTS BACK"],
         ["DO NOT FIX RAFT", "FIX COM"]),
    ]),
    (RO, "ROT", [
        ("R1", "TORQUE EQ", "TORQUE", solver_torque_eq,
         ["ROT EQUIL:", "CLOCKWISE TAU", "BALANCES CCW"],
         ["F1D1=F2D2"],
         ["PICK PIVOT", "SET CW=CCW"],
         ["USE PERP DIST", "SIGN TORQUES"]),
        ("R3", "I FORMULAS", "I FORMULA", solver_inertia,
         ["ROT INERTIA", "DEPENDS ON MASS", "AND AXIS"],
         ["HOOP=MR^2", "DISK=.5MR^2", "SPHERE=.4MR^2"],
         ["ROD CTR=ML^2/12", "ROD END=ML^2/3"],
         ["AXIS MUST MATCH", "USE GIVEN TABLE"]),
        ("R4", "I AXES", "INERTIA", solve_placeholder,
         ["MASS FARTHER", "FROM AXIS", "MEANS BIG I"],
         ["I=SUM MR^2"],
         ["COMPARE R^2", "FAR MASS WINS"],
         ["MASS SAME?", "AXIS MATTERS"]),
        ("R5", "ROT ALPHA", "ALPHA", solver_alpha,
         ["CONST ALPHA", "LIKE KINEMATICS"],
         ["WF=WI+AT", "TH=WIT+.5AT^2"],
         ["PICK EQN", "WITH ONE UNKNOWN"],
         ["RADIANS FOR TH", "SIGNS MATTER"]),
        ("R6", "ROT REVS", "REVS", solver_revs,
         ["CONST ALPHA", "FIND THETA", "THEN REVS"],
         ["TH=(WF2-WI2)/2A", "REV=TH/(2PI)"],
         ["SOLVE TH", "DIV BY 2PI"],
         ["A=0 BAD", "TH IN RADIANS"]),
        ("R7", "ANG MOM", "ANG MOM", solve_placeholder,
         ["NO EXT TORQUE", "ANG MOM CONS"],
         ["L=I OMEGA"],
         ["SET LI=LF", "I UP -> W DOWN"],
         ["NEEDS NO EXT TAU"]),
        ("R8", "ANG DISP", "ANG DISP", solver_ang_disp,
         ["ROT DISTANCE", "IS ANGULAR", "DISPLACEMENT"],
         ["TH=.5(WI+WF)T", "OR WF2-WI2", "OVER 2ALPHA"],
         ["WI=0 EXAMPLE:", "WF=50 NEED", "A OR TIME"],
         ["USE RADIANS", "REV=TH/2PI"]),
        ("R9", "L=MVR", "L MVR", solver_lmvr,
         ["POINT MASS", "USE R PERP"],
         ["L=M V RPERP"],
         ["COMPARE MVR", "BIGGER PRODUCT"],
         ["USE PERP R", "NOT FULL R"]),
        ("RA", "2BODY L", "2 BODY L", solver_2body_l,
         ["ADD SIGNED", "ANG MOM"],
         ["LTOT=SUM MVR"],
         ["SET + DIR", "SUM EACH BODY"],
         ["OPP SIGNS", "CAN CANCEL"]),
    ]),
    (SH, "OSC", [
        ("S1", "COUNTS SHM", "SHM?", solve_placeholder,
         ["SHM NEEDS", "RESTORING F", "TOWARD EQ"],
         ["F=-KX", "A=-W^2X"],
         ["CHECK FORCE", "LINEAR IN X", "OPP SIGN"],
         ["NOT ALL OSC", "IS SHM"]),
        ("S2", "TIME EQM", "TIME EQM", solver_shm_time,
         ["X=ACOS(WT)", "START AT MAX"],
         ["T=PI/(2W)"],
         ["FIRST EQM", "WHEN COS=0"],
         ["USES RAD W", "PHASE CHANGES"]),
        ("S3", "SHM ENERGY", "SHM ENERGY", solve_placeholder,
         ["SAME SPRING", "SAME AMP", "SAME MAX KE"],
         ["EMAX=.5KA^2"],
         ["ENERGY SAME", "LOW M -> HIGH V"],
         ["M AFFECTS V", "NOT MAX KE"]),
        ("S4", "MATCH T", "PERIODS", solve_placeholder,
         ["PENDULUM", "SPRING MASS"],
         ["TP=2PI(L/G)^.5", "TS=2PI(M/K)^.5"],
         ["MATCH T^2", "COMPARE RATIOS"],
         ["AMP SMALL ONLY", "M NOT IN PEND"]),
        ("S5", "MAX/EQM", "SHM POINTS", solve_placeholder,
         ["AT EQM:", "SPEED MAX", "ACCEL ZERO"],
         ["AT X=A:", "SPEED ZERO", "ACCEL MAX"],
         ["USE ENERGY:", "K MAX AT EQM", "U MAX AT ENDS"],
         ["FORCE ZERO", "ONLY AT EQM"]),
    ]),
    (FL, "FLUID", [
        ("F1", "DENS W/V", "DENSITY", solver_density,
         ["LIQ WEIGHT", "FROM FULL-EMPTY"],
         ["RHO=M/V", "M=W/G"],
         ["SUB WEIGHTS", "DIV G", "DIV VOL"],
         ["USE LIQ ONLY", "UNITS MATTER"]),
        ("F2", "PRESS F", "P FORCE", solver_pressure,
         ["GAUGE PRESS", "AT DEPTH H"],
         ["F=RHO G H A"],
         ["FIND P", "MULT BY AREA"],
         ["ATM IGNORED", "IF GAUGE ONLY"]),
        ("F3", "BUOY RATIO", "BUOY", solve_placeholder,
         ["FLOATING:", "FB=WEIGHT"],
         ["RHOBJ/RHOFL", "EQUALS SUB FRAC"],
         ["USE SUB VOL", "COMPARE DENSITY"],
         ["MORE DENSE", "SINKS"]),
        ("F4", "CONT/BERN", "BERN", solve_placeholder,
         ["FLOW SPEED", "AREA AND PRESS"],
         ["A1V1=A2V2", "P+.5RV^2+RGH"],
         ["NARROW -> FAST", "BERN FOR PRESS"],
         ["SAME STREAM", "IDEAL FLUID"]),
    ]),
    (GR, "GRAPHS", [
        ("G1", "SLOPE V", "SLOPE", solver_slope,
         ["X-T GRAPH", "SLOPE IS V"],
         ["V=DX/DT"],
         ["PICK TWO PTS", "RISE/RUN"],
         ["CURVE: TANGENT", "NOT AREA"]),
        ("G2", "MASS V P", "P GRAPH", solver_momentum_graph,
         ["READ MASS", "READ VELOCITY", "THEN P"],
         ["P=MV"],
         ["GET V SLOPE", "MULT BY M"],
         ["SIGNS MATTER", "UNITS"]),
        ("G3", "SPRING K", "SPRING K", solver_spring_k,
         ["F VS EXT", "SLOPE IS K"],
         ["F=KX"],
         ["USE EXTENSION", "SLOPE DELF/DELX"],
         ["TOTAL LENGTH?", "SUB NAT LENGTH"]),
        ("G4", "EXP GRAPH", "LAB GRAPH", solve_placeholder,
         ["REAL LABS HAVE", "FRICTION/LOSS"],
         ["SLOPE/INTERCEPT", "TELL MODEL"],
         ["CHECK AXES", "CHECK UNITS", "CHECK INTERCEPT"],
         ["NONIDEAL SHIFT", "INTERCEPT"]),
    ]),
]

QUICK = [
    ("STICK VF", "M1"),
    ("KE CONS?", "E2"),
    ("ROT AXIS", "R4"),
    ("FNET ZERO?", "K5"),
    ("GRAPH SHAPE", "G4"),
    ("BOUNCE", "M5"),
    ("ANG DISP", "R8"),
    ("SPRING T", "S4"),
    ("PIPE FLUID", "F4"),
]

def reserve_subtype_labels():
    for _, _, items in TOPICS:
        for lab, *_ in items:
            if lab not in USED:
                use(lab)
    for lab, *_ in DEFINITIONS:
        if lab not in USED:
            use(lab)

def build():
    reserve_subtype_labels()
    lines = []
    lines += [
        "Degree",
        "ClrHome",
        'Disp "PHYTREE"',
        'Disp "AP PHYS 1"',
        'Disp "DECISION TREE"',
        "Pause",
        f"Lbl {H}",
        "ClrHome",
        f'Menu("PHYTREE","KINEMATICS",{KI},"FORCES/DYN",{DY},"ENERGY/WORK",{EN},"MOMENTUM",{MO},"ROTATION",{RO},"MORE",{M2},"EXIT",{EX})',
        f"Lbl {M2}",
        "ClrHome",
        f'Menu("PHYTREE 2","OSCILLATIONS",{SH},"FLUIDS",{FL},"GRAPHS/LABS",{GR},"QUICK PICK",{QP},"DEFINITIONS",{Z},"BACK",{H},"EXIT",{EX})',
    ]

    for topic_label, topic_title, items in TOPICS:
        if topic_label == RO:
            first = items[:5]
            rest = items[5:]
            lines += [f"Lbl {RO}", "ClrHome",
                      f'Menu("ROTATION","TORQUE EQ",R1,"I FORMULAS",R3,"I AXES",R4,"ROT ALPHA",R5,"ROT REVS",R6,"MORE",{R2},"BACK",{H})',
                      f"Lbl {R2}", "ClrHome",
                      f'Menu("ROTATION 2","ANG MOM",R7,"ANG DISP",R8,"L=MVR",R9,"2BODY L",RA,"BACK",{RO},"HOME",{H})']
        else:
            pairs = []
            for lab, _, menu, *_ in items:
                pairs.append(f'"{menu}",{lab}')
            lines += [f"Lbl {topic_label}", "ClrHome",
                      f'Menu("{topic_title}",' + ",".join(pairs + [f'"BACK",{H}']) + ")"]

    lines += [
        f"Lbl {QP}", "ClrHome",
        f'Menu("QUICK PICK","STICK VF",M1,"KE CONS?",E2,"ROT AXIS",R4,"FNET ZERO?",K5,"GRAPH SHAPE",G4,"MORE",{Q2},"BACK",{H})',
        f"Lbl {Q2}", "ClrHome",
        f'Menu("QUICK 2","BOUNCE",M5,"ANG DISP",R8,"SPRING T",S4,"PIPE FLUID",F4,"BACK",{QP},"HOME",{H})',
        f"Lbl {Z}", "ClrHome",
        f'Menu("DEFINITIONS","EQUIL",Z1,"SHM",Z2,"CONSERVED",Z3,"SYSTEMS",Z4,"GRAPHS",Z5,"MORE",{Z0},"BACK",{M2})',
        f"Lbl {Z0}", "ClrHome",
        f'Menu("DEFIN 2","IMPULSE",Z6,"TORQUE",Z7,"FRQ WORDS",Z8,"BACK",{Z},"HOME",{H},"EXIT",{EX})',
    ]

    for lab, long_title, short_title, text_pages in DEFINITIONS:
        back = Z0 if lab in {"Z6", "Z7", "Z8"} else Z
        add_text(lines, lab, short_title, text_pages, back)

    for _, _, items in TOPICS:
        for lab, long_title, short_title, solver, help_lines, eqn_lines, steps_lines, traps_lines in items:
            lh, le, ls, lv, lt = alloc(), alloc(), alloc(), alloc(), alloc()
            lines += [
                f"Lbl {lab}",
                "ClrHome",
                f'Menu("{long_title}","HELP",{lh},"EQN",{le},"STEPS",{ls},"SOLVE",{lv},"TRAPS",{lt},"BACK",{topic_back(lab)})',
            ]
            add_text(lines, lh, short_title, screen(help_lines), lab)
            add_text(lines, le, "EQN", screen(eqn_lines), lab)
            add_text(lines, ls, "STEPS", screen(steps_lines), lab)
            lines += [f"Lbl {lv}"]
            solver(lines, lab)
            add_text(lines, lt, "TRAPS", screen(traps_lines), lab)

    for label, (msg, back) in BAD.items():
        lines += [f"Lbl {label}", "ClrHome", f'Disp "{msg}"']
        add_solver_result_nav(lines, back)

    lines += [
        f"Lbl {EX}",
        "ClrHome",
        'Disp "PHYTREE END"',
        "Stop",
    ]
    return lines

def topic_back(label):
    if label.startswith("K"):
        return KI
    if label.startswith("D"):
        return DY
    if label.startswith("E"):
        return EN
    if label.startswith("M"):
        return MO
    if label in {"R1", "R3", "R4", "R5", "R6"}:
        return RO
    if label in {"R7", "R8", "R9", "RA"}:
        return R2
    if label.startswith("S"):
        return SH
    if label.startswith("F"):
        return FL
    if label.startswith("G"):
        return GR
    return H

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
    " ": 0x29, '"': 0x2A, ",": 0x2B, ".": 0x3A, ":": 0x3F,
    "0": 0x30, "1": 0x31, "2": 0x32, "3": 0x33, "4": 0x34,
    "5": 0x35, "6": 0x36, "7": 0x37, "8": 0x38, "9": 0x39,
    "=": 0x6A, "<": 0x6B, ">": 0x6C,
    "+": 0x70, "-": 0x71, "*": 0x82, "/": 0x83, "(": 0x10, ")": 0x11,
    "^": 0xF0, "?": 0xAF,
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
    comment = b"PHYTREE AP PHYSICS 1".ljust(42, b" ")
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
    (OUT / "PHYTREE.8xp.txt").write_text(source, encoding="ascii")
    (OUT / "PHYTREE.8xp").write_bytes(blob)
    print(f"Wrote PHYTREE.8xp.txt ({len(lines)} lines)")
    print(f"Wrote PHYTREE.8xp ({len(blob)} bytes, {tok_len} token bytes, section {section_len})")
