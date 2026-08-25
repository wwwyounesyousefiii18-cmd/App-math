"""
MATH TOOLS - single-file Kivy app with switchable Dark / Light theme.
Run with: python math_tools_app.py
"""

import os
import math
import random
import calendar
from datetime import date

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.clock import Clock


# ---------------------------------------------------------------------------
# THEME PALETTES
# ---------------------------------------------------------------------------
# TEXT_PRIMARY = strong headings/titles that sit directly on BG/CARD
# TEXT         = secondary body text on BG/CARD
# MUTED        = subtitles, hints, chevrons
# ON_ACCENT    = text that sits on top of a colored fill (buttons, badges)

def _hex(d):
    return {k: get_color_from_hex(v) for k, v in d.items()}


DARK_THEME = _hex({
    "BG": "#0B0714",
    "CARD": "#171027",
    "CARD_2": "#211538",
    "CARD_BORDER": "#3A2657",

    "PURPLE": "#7B35D6",
    "PURPLE_LIGHT": "#9B4DFF",
    "PURPLE_DARK": "#32165A",
    "ICON_BG": "#8A57C8",

    "TEXT_PRIMARY": "#F7F3FF",
    "TEXT": "#DDD4EA",
    "MUTED": "#9E91B2",
    "ON_ACCENT": "#FFFFFF",

    "YELLOW": "#FFD34E",
    "GREEN": "#39D98A",
    "RED": "#FF5577",

    "PILL_BG": "#241640",

    "INPUT_BG": "#1C1330",
    "INPUT_BORDER": "#3A2657",

    "GREEN_BG": "#123324",
    "RED_BG": "#3A1620",
    "SELECTED_GREEN": "#2E9E5B",
})

LIGHT_THEME = _hex({
    "BG": "#F6F3FC",
    "CARD": "#FFFFFF",
    "CARD_2": "#F1ECFB",
    "CARD_BORDER": "#E3D9F5",

    "PURPLE": "#7B35D6",
    "PURPLE_LIGHT": "#6C2BB8",
    "PURPLE_DARK": "#9C7BC9",
    "ICON_BG": "#8A57C8",

    "TEXT_PRIMARY": "#241A3B",
    "TEXT": "#4A3F63",
    "MUTED": "#8A7FA0",
    "ON_ACCENT": "#FFFFFF",

    "YELLOW": "#C9860A",
    "GREEN": "#1F9D57",
    "RED": "#D6304A",

    "PILL_BG": "#EDE3FA",

    "INPUT_BG": "#F1ECFB",
    "INPUT_BORDER": "#D9CCF0",

    "GREEN_BG": "#E6F7ED",
    "RED_BG": "#FCE8EC",
    "SELECTED_GREEN": "#2E9E5B",
})

PALETTES = {"dark": DARK_THEME, "light": LIGHT_THEME}

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "theme_pref.txt")

# On Android, keep preferences in the app's writable data directory.
# Fall back to the script directory when running on desktop.
def _get_config_path():
    try:
        from kivy.app import App
        if App.get_running_app():
            return os.path.join(App.get_running_app().user_data_dir, "theme_pref.txt")
    except Exception:
        pass
    return CONFIG_PATH


def load_theme_pref():
    try:
        with open(_get_config_path(), "r") as f:
            v = f.read().strip()
            if v in PALETTES:
                return v
    except Exception:
        pass
    return "dark"


def save_theme_pref(name):
    try:
        path = _get_config_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(name)
    except Exception:
        pass


CURRENT_THEME = load_theme_pref()
T = dict(PALETTES[CURRENT_THEME])  # live/mutable theme dict read by all widgets


# ---------------------------------------------------------------------------
# MATH FUNCTIONS
# ---------------------------------------------------------------------------

def parse_numbers(text):
    cleaned = text.replace(",", " ").replace(";", " ")
    parts = cleaned.split()
    result = []
    for p in parts:
        result.append(float(p) if "." in p else int(p))
    return result


def f_gcd(a, b):
    a, b = abs(int(a)), abs(int(b))
    while b != 0:
        a, b = b, a % b
    return a


def f_lcm(a, b):
    a, b = int(a), int(b)
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // f_gcd(a, b)


def f_is_prime(n):
    n = int(n)
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def f_factorial(n):
    n = int(n)
    if n < 0:
        return None
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result


def f_fibonacci(n):
    n = int(n)
    if n <= 0:
        return []
    numbers = []
    a, b = 0, 1
    for _ in range(n):
        numbers.append(a)
        a, b = b, a + b
    return numbers


def f_prime_factors(n):
    n = abs(int(n))
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


def f_divisors(n):
    n = abs(int(n))
    if n == 0:
        return []
    result = []
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            result.append(i)
            if i != n // i:
                result.append(n // i)
    return sorted(result)


def f_even_odd(n):
    return "Even" if int(n) % 2 == 0 else "Odd"


def f_perfect_number(n):
    n = int(n)
    if n <= 1:
        return False
    return sum(f_divisors(n)[:-1]) == n


def f_average(numbers):
    if not numbers:
        return None
    return sum(numbers) / len(numbers)


def f_sum(numbers):
    if not numbers:
        return None
    return sum(numbers)


def f_power(base, exponent):
    return base ** exponent


def f_sqrt(n):
    if n < 0:
        return None
    return math.sqrt(n)


def f_mult_table(n):
    n = int(n)
    return [f"{n} \u00d7 {i} = {n * i}" for i in range(1, 11)]


def f_reverse(n):
    n = int(n)
    sign = -1 if n < 0 else 1
    reversed_number = int(str(abs(n))[::-1])
    return sign * reversed_number


# --- new tools: health -----------------------------------------------------

def f_bmi(weight_kg, height_cm):
    h_m = height_cm / 100
    return weight_kg / (h_m ** 2)


def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    return "Obese"


def f_bmr(weight_kg, height_cm, age, gender):
    if gender.lower().startswith("m"):
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def f_body_fat(waist, neck, height, gender, hip=None):
    gender = gender.lower()
    if gender.startswith("m"):
        return 495 / (1.0324 - 0.19077 * math.log10(waist - neck) + 0.15456 * math.log10(height)) - 450
    return 495 / (1.29579 - 0.35004 * math.log10(waist + hip - neck) + 0.22100 * math.log10(height)) - 450


# --- new tools: everyday ----------------------------------------------------

def f_percentage_of(x, y):
    return x / 100 * y


LENGTH_TO_M = {"km": 1000, "m": 1, "cm": 0.01, "mm": 0.001,
               "mi": 1609.34, "ft": 0.3048, "in": 0.0254, "yd": 0.9144}
WEIGHT_TO_KG = {"kg": 1, "g": 0.001, "mg": 0.000001, "lb": 0.453592, "oz": 0.0283495}
TEMP_UNITS = {"c", "f", "k"}


def _to_celsius(v, u):
    if u == "c":
        return v
    if u == "f":
        return (v - 32) * 5 / 9
    return v - 273.15  # kelvin


def _from_celsius(v, u):
    if u == "c":
        return v
    if u == "f":
        return v * 9 / 5 + 32
    return v + 273.15  # kelvin


def convert_unit(value, frm, to):
    frm, to = frm.lower(), to.lower()
    if frm in TEMP_UNITS and to in TEMP_UNITS:
        return _from_celsius(_to_celsius(value, frm), to)
    if frm in LENGTH_TO_M and to in LENGTH_TO_M:
        return value * LENGTH_TO_M[frm] / LENGTH_TO_M[to]
    if frm in WEIGHT_TO_KG and to in WEIGHT_TO_KG:
        return value * WEIGHT_TO_KG[frm] / WEIGHT_TO_KG[to]
    raise ValueError("unsupported units")


def f_interest(principal, rate, time, kind):
    if kind.lower().startswith("c"):
        total = principal * ((1 + rate / 100) ** time)
        interest = total - principal
    else:
        interest = principal * rate * time / 100
        total = principal + interest
    return interest, total


def f_bill_split(total, people, tip_percent=0):
    total_with_tip = total * (1 + tip_percent / 100)
    return total_with_tip, total_with_tip / people


# --- new tools: more math ----------------------------------------------------

def f_quadratic(a, b, c):
    if a == 0:
        raise ValueError("a must not be 0")
    d = b * b - 4 * a * c
    if d > 0:
        x1 = (-b + math.sqrt(d)) / (2 * a)
        x2 = (-b - math.sqrt(d)) / (2 * a)
        return "real2", (x1, x2)
    elif d == 0:
        x = -b / (2 * a)
        return "real1", (x,)
    real = -b / (2 * a)
    imag = math.sqrt(-d) / (2 * a)
    return "complex", (real, imag)


def f_shape_area(shape, dims):
    shape = shape.lower()
    if shape == "circle":
        return math.pi * dims[0] ** 2
    if shape == "square":
        return dims[0] ** 2
    if shape == "rectangle":
        return dims[0] * dims[1]
    if shape == "triangle":
        return 0.5 * dims[0] * dims[1]
    raise ValueError("unknown shape")


def convert_base(num_str, from_base, to_base):
    value = int(num_str, from_base)
    if to_base == 10:
        return str(value)
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if value == 0:
        return "0"
    result = ""
    n = value
    while n > 0:
        result = digits[n % to_base] + result
        n //= to_base
    return result


def f_weighted_average(pairs):
    total_w = sum(w for _, w in pairs)
    if total_w == 0:
        return None
    return sum(s * w for s, w in pairs) / total_w


# --- new tools: fun & tools ---------------------------------------------------

def roll_dice(n, sides):
    rolls = [random.randint(1, sides) for _ in range(n)]
    return rolls, sum(rolls)


def calculate_age(birth_date_str):
    y, m, d = map(int, birth_date_str.split("-"))
    birth = date(y, m, d)
    today = date.today()
    years = today.year - birth.year
    months = today.month - birth.month
    days = today.day - birth.day
    if days < 0:
        months -= 1
        prev_month = today.month - 1 or 12
        prev_year = today.year if today.month > 1 else today.year - 1
        days += calendar.monthrange(prev_year, prev_month)[1]
    if months < 0:
        years -= 1
        months += 12
    return years, months, days


# ---------------------------------------------------------------------------
# TOOL DATA
# id, icon_text, title, subtitle, input_hint, lesson, example,
# quiz_question, quiz_options(4), correct_index
# ---------------------------------------------------------------------------

TOOLS = [
    ("gcd", "GCD", "GCD", "Greatest Common Divisor",
     "Enter two numbers, e.g. 24 36",
     "GCD is the largest number that divides both numbers exactly.",
     "GCD(24, 36) = 12.",
     "What is GCD(18, 24)?", ["3", "6", "9", "12"], 1),

    ("lcm", "LCM", "LCM", "Least Common Multiple",
     "Enter two numbers, e.g. 6 8",
     "LCM is the smallest positive number that is a multiple of both numbers.",
     "LCM(6, 8) = 24.",
     "What is LCM(4, 6)?", ["8", "10", "12", "24"], 2),

    ("sum", "SUM", "SUM", "Calculate the sum",
     "Enter numbers: 5 8 2",
     "Sum means adding all the numbers together.",
     "5 + 8 + 2 = 15.",
     "What is 7 + 5 + 3?", ["12", "15", "16", "18"], 1),

    ("average", "AVG", "AVERAGE", "Calculate the average",
     "Enter numbers: 10 20 30",
     "Average is the sum divided by how many numbers there are.",
     "average(10, 20, 30) = 20.",
     "Average of 4, 8, 12?", ["6", "8", "10", "12"], 1),

    ("power", "PWR", "POWER", "Calculate a power",
     "Enter base and exponent: 2 5",
     "A power tells how many times the base is multiplied by itself.",
     "2^5 = 32.",
     "What is 3^3?", ["9", "18", "27", "36"], 2),

    ("square_root", "SQRT", "SQUARE ROOT", "Calculate square root",
     "Enter one number: 81",
     "Square root is the number that multiplied by itself gives the original number.",
     "sqrt(81) = 9.",
     "What is sqrt(64)?", ["6", "7", "8", "9"], 2),

    ("prime", "P", "PRIME NUMBER", "Check if a number is prime",
     "Enter one number: 17",
     "A prime number has exactly two positive divisors: 1 and itself.",
     "7 is prime.",
     "Which number is prime?", ["9", "15", "17", "21"], 2),

    ("even_odd", "21", "EVEN OR ODD", "Check even or odd",
     "Enter one number: 42",
     "Even numbers divide by 2 with no remainder; otherwise the number is odd.",
     "42 is even, 43 is odd.",
     "Which number is even?", ["17", "21", "34", "45"], 2),

    ("perfect_number", "PFN", "PERFECT NUMBER", "Check perfect number",
     "Enter one number: 28",
     "A perfect number equals the sum of its positive divisors except itself.",
     "28 = 1 + 2 + 4 + 7 + 14.",
     "Which is perfect?", ["12", "18", "24", "28"], 3),

    ("prime_factors", "PF", "PRIME FACTORS", "Find prime factors",
     "Enter one number: 60",
     "Prime factorization writes a number as a product of prime numbers.",
     "60 = 2 x 2 x 3 x 5.",
     "Prime factors of 12?", ["2x6", "3x4", "2x2x3", "1x12"], 2),

    ("divisors", "DIV", "DIVISORS", "Find all divisors",
     "Enter one number: 12",
     "A divisor divides a number with no remainder.",
     "divisors of 12 are 1, 2, 3, 4, 6, 12.",
     "Which is NOT a divisor of 12?", ["2", "3", "4", "5"], 3),

    ("reverse_number", "REV", "REVERSE NUMBER", "Reverse a number",
     "Enter one number: 12345",
     "Reverse a number means writing its digits in the opposite order.",
     "123 becomes 321.",
     "Reverse of 450?", ["45", "54", "405", "504"], 0),

    ("factorial", "n!", "FACTORIAL", "Calculate n!",
     "Enter a non-negative integer: 5",
     "Factorial multiplies all positive integers from 1 up to n.",
     "5! = 120.",
     "What is 4!?", ["8", "12", "24", "36"], 2),

    ("fibonacci", "FIB", "FIBONACCI", "Fibonacci sequence",
     "Enter number of terms: 8",
     "Each Fibonacci term is the sum of the two previous terms.",
     "0, 1, 1, 2, 3, 5, ...",
     "What comes next: 1, 1, 2, 3, 5, ?", ["6", "7", "8", "10"], 2),

    ("multiplication_table", "TBL", "MULTIPLICATION TABLE", "Show multiplication table",
     "Enter one number: 7",
     "A multiplication table shows products from x1 to x10.",
     "7 x 3 = 21.",
     "What is 8 x 7?", ["48", "54", "56", "64"], 2),

    # --- HEALTH ---
    ("bmi", "BMI", "BMI", "Body Mass Index",
     "Enter weight(kg) and height(cm): 70 175",
     "BMI = weight(kg) / height(m)^2. It gives a rough sense of whether your weight is healthy for your height.",
     "BMI(70, 175) = 22.9 (Normal).",
     "Roughly what is the BMI of a 70kg, 175cm person?", ["18", "20", "23", "30"], 2),

    ("bmr", "BMR", "DAILY CALORIES", "Estimate resting calories (BMR)",
     "Enter weight(kg) height(cm) age gender(m/f): 70 175 25 m",
     "BMR estimates the calories your body burns at rest, using the Mifflin-St Jeor formula.",
     "BMR(70kg, 175cm, 25y, male) is about 1674 kcal/day.",
     "Which of these is NOT used in the BMR formula?", ["Weight", "Height", "Age", "Blood type"], 3),

    ("body_fat", "BF%", "BODY FAT %", "Estimate body fat percentage",
     "Enter waist neck height gender(m/f) [hip if f]: 85 38 175 m",
     "The US Navy method estimates body fat from waist, neck, and height (plus hip, for women).",
     "waist 85cm, neck 38cm, height 175cm, male: body fat is about 17%.",
     "Which measurements does the US Navy method use for men?",
     ["Waist, neck, height", "Waist, hip, height", "Weight, height, age", "Chest, waist, hip"], 0),

    # --- EVERYDAY ---
    ("percentage", "PCT", "PERCENTAGE", "Find X% of Y",
     "Enter X and Y: 20 150",
     "To find X% of Y, multiply Y by X divided by 100.",
     "20% of 150 = 30.",
     "What is 25% of 80?", ["15", "20", "25", "30"], 1),

    ("unit_converter", "UNIT", "UNIT CONVERTER", "Convert length, weight, or temperature",
     "Enter: value from to, e.g. 10 km mi",
     "Converts between common length units (km, m, cm, mi, ft, in, yd), weight units (kg, g, lb, oz), and temperature (c, f, k).",
     "10 km = 6.21 mi.",
     "How many meters are in 1 km?", ["10", "100", "1000", "10000"], 2),

    ("interest", "INT", "INTEREST", "Simple vs compound interest",
     "Enter: principal rate time type(s/c), e.g. 1000 5 3 c",
     "Simple interest grows by the same amount each year; compound interest also earns interest on top of previous interest.",
     "1000 at 5% for 3 years: simple = 150, compound is about 157.6.",
     "Which grows faster over time?",
     ["Simple interest", "Compound interest", "They're always equal", "Depends on currency"], 1),

    ("bill_split", "BILL", "BILL SPLIT", "Split a bill with tip",
     "Enter: total people tip%, e.g. 120 4 15",
     "Add the tip to the total first, then divide evenly among everyone.",
     "$120 for 4 people with 15% tip = $34.50 each.",
     "Total $100, 4 people, 10% tip. Amount per person?",
     ["25.00", "27.50", "30.00", "32.50"], 1),

    # --- MORE MATH ---
    ("quadratic", "QUAD", "QUADRATIC EQUATION", "Solve ax^2 + bx + c = 0",
     "Enter a b c: 1 -3 2",
     "For ax^2+bx+c=0, the discriminant b^2-4ac tells you how many real roots the equation has.",
     "x^2 - 3x + 2 = 0 gives x = 1 or x = 2.",
     "How many real roots does x^2 + 1 = 0 have?", ["0", "1", "2", "Infinite"], 0),

    ("shapes", "AREA", "SHAPE AREA", "Area of common shapes",
     "Enter shape and size: circle 5 / square 4 / rectangle 4 6 / triangle 6 4",
     "Each shape has its own area formula: circle is pi*r^2, rectangle is w*h, triangle is 0.5*base*height.",
     "A rectangle 4 x 6 has an area of 24.",
     "Area of a rectangle 4 x 6?", ["10", "20", "24", "48"], 2),

    ("base_converter", "BASE", "BASE CONVERTER", "Convert between number bases",
     "Enter: number from_base to_base, e.g. FF 16 10",
     "Numbers can be written in different bases: binary (2), octal (8), decimal (10), hex (16).",
     "FF in base 16 equals 255 in base 10.",
     "What is binary 1010 in decimal?", ["8", "9", "10", "12"], 2),

    ("weighted_average", "WAVG", "WEIGHTED AVERAGE", "Grades with different weights",
     "Enter score-weight pairs: 90 30 80 30 70 40",
     "Multiply each score by its weight, add them up, then divide by the total weight.",
     "90(30%) + 80(30%) + 70(40%) gives a weighted average of 79.",
     "Weighted average of 100(50%) and 60(50%)?", ["70", "75", "80", "85"], 2),

    # --- FUN & TOOLS ---
    ("random_tool", "RND", "RANDOM / DICE", "Random number or dice roll",
     "Enter min max (e.g. 1 100) or dice like 2d6",
     "Generates a random number in your range, or rolls dice using NdM notation (N dice with M sides).",
     "2d6 might roll [4, 6] for a total of 10.",
     "In dice notation, what does '2d6' mean?",
     ["Roll a d2 six times", "Roll two 6-sided dice", "Roll a 26-sided die", "Roll six 2-sided dice"], 1),

    ("age_calculator", "AGE", "AGE CALCULATOR", "Exact age from birth date",
     "Enter birth date as YYYY-MM-DD: 1998-05-20",
     "Calculates exact age in years, months, and days from a birth date to today.",
     "Someone born 2000-01-01 turns exactly 25 on 2025-01-01.",
     "If someone was born in 2000, roughly how old are they in 2026?", ["24", "25", "26", "27"], 2),
]

CATEGORIES = [
    ("BASIC MATH", ["gcd", "lcm", "sum", "average", "power", "square_root"]),
    ("NUMBER TOOLS", ["prime", "even_odd", "perfect_number", "prime_factors", "divisors", "reverse_number"]),
    ("SEQUENCES & TABLES", ["factorial", "fibonacci", "multiplication_table"]),
    ("HEALTH", ["bmi", "bmr", "body_fat"]),
    ("EVERYDAY", ["percentage", "unit_converter", "interest", "bill_split"]),
    ("MORE MATH", ["quadratic", "shapes", "base_converter", "weighted_average"]),
    ("FUN & TOOLS", ["random_tool", "age_calculator"]),
]

TOOLS_BY_ID = {t[0]: t for t in TOOLS}


# ---------------------------------------------------------------------------
# REUSABLE ROUNDED WIDGETS
# ---------------------------------------------------------------------------

def add_rounded_bg(widget, color, radius=None, border_color=None, border_width=1.2):
    if radius is None:
        radius = dp(18)

    with widget.canvas.before:
        fill_color = Color(*color)
        rect = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[radius])
        border_line = None
        if border_color:
            Color(*border_color)
            border_line = Line(
                rounded_rectangle=(widget.x, widget.y, widget.width, widget.height, radius),
                width=border_width
            )

    def update(*_args):
        rect.pos = widget.pos
        rect.size = widget.size
        if border_line:
            border_line.rounded_rectangle = (
                widget.x, widget.y, widget.width, widget.height, radius
            )

    widget.bind(pos=update, size=update)
    widget._bg_fill = fill_color
    return fill_color


class IconBadge(Label):
    def __init__(self, text, bg_color=None, size_px=44, font_size=13, **kwargs):
        super().__init__(
            text=text, bold=True, color=T["ON_ACCENT"], font_size=dp(font_size),
            size_hint=(None, None), size=(dp(size_px), dp(size_px)),
            halign="center", valign="middle", **kwargs
        )
        self.bind(size=self._sync)
        add_rounded_bg(self, bg_color or T["ICON_BG"], radius=dp(size_px / 2))

    def _sync(self, *_a):
        self.text_size = self.size

    def set_bg(self, color):
        self._bg_fill.rgba = color


class SectionPill(Label):
    def __init__(self, text, **kwargs):
        super().__init__(
            text=text, bold=True, font_size=dp(12), color=T["PURPLE_LIGHT"],
            size_hint=(None, None), height=dp(30), **kwargs
        )
        add_rounded_bg(self, T["PILL_BG"], radius=dp(15))
        self.bind(texture_size=self._resize)

    def _resize(self, *_a):
        self.width = self.texture_size[0] + dp(30)


class ListItem(ButtonBehavior, BoxLayout):
    def __init__(self, icon_text, title, subtitle, on_release=None, **kwargs):
        super().__init__(
            orientation="horizontal", padding=[dp(14), dp(10)], spacing=dp(12),
            size_hint_y=None, height=dp(64), **kwargs
        )
        add_rounded_bg(self, T["CARD"], radius=dp(18), border_color=T["CARD_BORDER"], border_width=dp(1))

        self.add_widget(IconBadge(icon_text))

        col = BoxLayout(orientation="vertical", spacing=dp(2))
        title_lbl = Label(text=title, font_size=dp(15), bold=True, color=T["TEXT_PRIMARY"],
                           halign="left", valign="middle", size_hint_y=None, height=dp(20))
        title_lbl.bind(size=lambda o, *a: setattr(o, "text_size", o.size))
        sub_lbl = Label(text=subtitle, font_size=dp(12), color=T["MUTED"],
                         halign="left", valign="middle", size_hint_y=None, height=dp(18))
        sub_lbl.bind(size=lambda o, *a: setattr(o, "text_size", o.size))
        col.add_widget(title_lbl)
        col.add_widget(sub_lbl)
        self.add_widget(col)

        chevron = Label(text=">", font_size=dp(18), color=T["MUTED"], size_hint=(None, 1), width=dp(20))
        self.add_widget(chevron)

        if on_release:
            self.bind(on_release=on_release)


class RoundedButton(ButtonBehavior, BoxLayout):
    def __init__(self, text, bg_color=None, text_color=None, font_size=16,
                 height=52, radius=None, on_release=None, **kwargs):
        super().__init__(size_hint_y=None, height=dp(height), **kwargs)
        self.label = Label(text=text, bold=True, font_size=dp(font_size), color=text_color or T["ON_ACCENT"])
        self.add_widget(self.label)
        add_rounded_bg(self, bg_color or T["PURPLE"], radius=radius or dp(height / 2))
        if on_release:
            self.bind(on_release=on_release)


class QuizOption(ButtonBehavior, BoxLayout):
    def __init__(self, text, on_release=None, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(54),
                          padding=[dp(14), 0], **kwargs)
        add_rounded_bg(self, T["PURPLE"], radius=dp(16))
        self.label = Label(text=text, bold=True, font_size=dp(15), color=T["ON_ACCENT"])
        self.add_widget(self.label)
        self.badge = Label(text="", bold=True, font_size=dp(15), color=T["ON_ACCENT"],
                            size_hint=(None, 1), width=dp(22))
        self.add_widget(self.badge)
        if on_release:
            self.bind(on_release=on_release)

    def reset(self):
        self._bg_fill.rgba = T["PURPLE"]
        self.badge.text = ""

    def mark_correct(self):
        self._bg_fill.rgba = T["SELECTED_GREEN"]
        self.badge.text = "OK"

    def mark_wrong(self):
        self._bg_fill.rgba = T["RED"]
        self.badge.text = "X"


class ResultPanel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="horizontal", padding=dp(14), spacing=dp(12),
                          size_hint_y=None, height=dp(80), **kwargs)
        add_rounded_bg(self, T["CARD"], radius=dp(18))

        self.icon = IconBadge("i", bg_color=T["CARD_2"], size_px=40)
        self.add_widget(self.icon)

        self.col = BoxLayout(orientation="vertical", spacing=dp(3), size_hint_y=None)
        self.col.bind(minimum_height=self.col.setter("height"))

        self.title_lbl = Label(text="Result will appear here", bold=True, font_size=dp(14),
                                color=T["TEXT"], halign="left", valign="middle", size_hint_y=None)
        self.title_lbl.bind(width=self._sync_title_width, texture_size=self._sync_title_height)

        self.detail_lbl = Label(text="", font_size=dp(13), color=T["MUTED"],
                                 halign="left", valign="middle", size_hint_y=None)
        self.detail_lbl.bind(width=self._sync_detail_width, texture_size=self._sync_detail_height)

        self.col.add_widget(self.title_lbl)
        self.col.add_widget(self.detail_lbl)
        self.add_widget(self.col)

        self.col.bind(height=self._sync_panel_height)

    def _sync_title_width(self, o, w):
        o.text_size = (w, None)

    def _sync_title_height(self, o, ts):
        o.height = ts[1]

    def _sync_detail_width(self, o, w):
        o.text_size = (w, None)

    def _sync_detail_height(self, o, ts):
        o.height = ts[1]

    def _sync_panel_height(self, *_a):
        self.height = max(dp(80), self.col.height + dp(28))

    def set_result(self, title, detail="", state="neutral"):
        self.title_lbl.text = title
        self.detail_lbl.text = detail
        if state == "success":
            self._bg_fill.rgba = T["GREEN_BG"]
            self.icon.text = "OK"
            self.icon.set_bg(T["SELECTED_GREEN"])
            self.title_lbl.color = T["GREEN"]
        elif state == "fail":
            self._bg_fill.rgba = T["RED_BG"]
            self.icon.text = "X"
            self.icon.set_bg(T["RED"])
            self.title_lbl.color = T["RED"]
        else:
            self._bg_fill.rgba = T["CARD"]
            self.icon.text = "i"
            self.icon.set_bg(T["CARD_2"])
            self.title_lbl.color = T["TEXT"]


class _ClearButton(ButtonBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(size_hint=(None, None), size=(dp(26), dp(26)), **kwargs)
        add_rounded_bg(self, T["CARD_2"], radius=dp(13))
        self.add_widget(Label(text="X", font_size=dp(12), color=T["MUTED"], bold=True))


class ClearableInput(BoxLayout):
    def __init__(self, hint_text="", **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(56),
                          padding=[dp(14), dp(6)], spacing=dp(8), **kwargs)
        add_rounded_bg(self, T["INPUT_BG"], radius=dp(18), border_color=T["INPUT_BORDER"], border_width=dp(1))

        self.text_input = TextInput(
            hint_text=hint_text, multiline=False, font_size=dp(16),
            foreground_color=T["TEXT"], hint_text_color=T["MUTED"], cursor_color=T["PURPLE_LIGHT"],
            background_normal="", background_active="", background_color=(0, 0, 0, 0),
            padding=[0, dp(14)],
        )
        self.add_widget(self.text_input)

        clear_btn = _ClearButton()
        clear_btn.bind(on_release=lambda *_: setattr(self.text_input, "text", ""))
        self.add_widget(clear_btn)

    @property
    def text(self):
        return self.text_input.text

    @text.setter
    def text(self, value):
        self.text_input.text = value


class _RoundIconButton(ButtonBehavior, BoxLayout):
    def __init__(self, text, **kwargs):
        super().__init__(size_hint=(None, None), size=(dp(36), dp(36)), **kwargs)
        self.add_widget(Label(text=text, font_size=dp(16), color=T["PURPLE_LIGHT"], bold=True))


class TopBar(BoxLayout):
    def __init__(self, title, on_back=None, on_home=None, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(44), spacing=dp(8), **kwargs)

        back_btn = _RoundIconButton("<")
        if on_back:
            back_btn.bind(on_release=on_back)
        self.add_widget(back_btn)

        self.add_widget(Label(text=title, bold=True, font_size=dp(19), color=T["TEXT_PRIMARY"]))

        home_btn = _RoundIconButton("Home")
        if on_home:
            home_btn.bind(on_release=on_home)
        self.add_widget(home_btn)


class ThemeToggle(ButtonBehavior, BoxLayout):
    """Small pill button on the Home screen that switches Dark <-> Light theme."""

    def __init__(self, **kwargs):
        super().__init__(size_hint=(None, None), size=(dp(96), dp(34)), **kwargs)
        add_rounded_bg(self, T["CARD_2"], radius=dp(17), border_color=T["CARD_BORDER"], border_width=dp(1))
        label_text = "Light Mode" if CURRENT_THEME == "dark" else "Dark Mode"
        self.add_widget(Label(text=label_text, font_size=dp(11), bold=True, color=T["TEXT_PRIMARY"]))
        self.bind(on_release=lambda *_: App.get_running_app().toggle_theme())


def wrapped_label(text, font_size=13, color=None, bold=False, min_height=20):
    lbl = Label(text=text, font_size=dp(font_size), color=color or T["TEXT"], bold=bold,
                halign="center", valign="middle", size_hint_y=None, height=dp(min_height))

    def _w(o, w):
        o.text_size = (w, None)

    def _h(o, ts):
        o.height = max(dp(min_height), ts[1])

    lbl.bind(width=_w, texture_size=_h)
    return lbl


class HamburgerIcon(ButtonBehavior, BoxLayout):
    """Three-line menu icon, drawn with canvas so it never depends on font glyph support."""

    def __init__(self, on_release=None, **kwargs):
        super().__init__(size_hint=(None, None), size=(dp(36), dp(36)), **kwargs)
        with self.canvas:
            Color(*T["PURPLE_LIGHT"])
            self._bars = [Rectangle(pos=(0, 0), size=(0, 0)) for _ in range(3)]
        self.bind(pos=self._update, size=self._update)
        if on_release:
            self.bind(on_release=on_release)

    def _update(self, *_args):
        bar_h = dp(3)
        gap = dp(6)
        w = self.width * 0.55
        x = self.x + (self.width - w) / 2
        total_h = bar_h * 3 + gap * 2
        y0 = self.y + (self.height - total_h) / 2
        for i, r in enumerate(self._bars):
            r.pos = (x, y0 + i * (bar_h + gap))
            r.size = (w, bar_h)


def _popup_kwargs(height):
    return dict(size_hint=(0.86, None), height=dp(height),
                background="", background_color=T["CARD"],
                title_color=T["TEXT_PRIMARY"], separator_color=T["PURPLE"])


class MenuPopup(Popup):
    """The hamburger menu itself: Language / App Info / More Tools."""

    def __init__(self, **kwargs):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(14))
        content.add_widget(RoundedButton("Language", bg_color=T["CARD_2"], text_color=T["TEXT_PRIMARY"],
                                          height=48, on_release=lambda *_: self._go("language")))
        content.add_widget(RoundedButton("App Info", bg_color=T["CARD_2"], text_color=T["TEXT_PRIMARY"],
                                          height=48, on_release=lambda *_: self._go("info")))
        content.add_widget(RoundedButton("More Tools", bg_color=T["CARD_2"], text_color=T["TEXT_PRIMARY"],
                                          height=48, on_release=lambda *_: self._go("more")))
        super().__init__(title="Menu", content=content, **_popup_kwargs(240), **kwargs)

    def _go(self, where):
        self.dismiss()
        if where == "language":
            LanguagePopup().open()
        elif where == "info":
            InfoPopup().open()
        elif where == "more":
            MoreToolsPopup().open()


class LanguagePopup(Popup):
    def __init__(self, **kwargs):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(14))
        content.add_widget(wrapped_label("English is active.", 14, T["TEXT_PRIMARY"], True, 24))
        content.add_widget(wrapped_label(
            "Persian (Farsi) support needs a Persian font file and two extra libraries "
            "installed first. Ask any time to have it fully enabled.",
            12, T["MUTED"], False, 50))
        content.add_widget(RoundedButton("OK", bg_color=T["PURPLE"], height=46,
                                          on_release=lambda *_: self.dismiss()))
        super().__init__(title="Language", content=content, **_popup_kwargs(230), **kwargs)


class InfoPopup(Popup):
    def __init__(self, **kwargs):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(14))
        content.add_widget(wrapped_label("MATH TOOLS", 20, T["TEXT_PRIMARY"], True, 30))
        content.add_widget(wrapped_label("Version 1.0", 12, T["MUTED"], False, 18))
        content.add_widget(wrapped_label(
            f"{len(TOOLS)} calculators and quizzes across {len(CATEGORIES)} categories.",
            13, T["TEXT"], False, 30))
        content.add_widget(wrapped_label("Built with Python and Kivy.", 12, T["MUTED"], False, 18))
        content.add_widget(RoundedButton("OK", bg_color=T["PURPLE"], height=46,
                                          on_release=lambda *_: self.dismiss()))
        super().__init__(title="App Info", content=content, **_popup_kwargs(270), **kwargs)


class MoreToolsPopup(Popup):
    def __init__(self, **kwargs):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(14))
        content.add_widget(wrapped_label("More tools are on the way. Ideas being considered:",
                                          13, T["TEXT_PRIMARY"], True, 40))
        ideas = ("Currency converter\n"
                 "Date difference calculator\n"
                 "Loan / EMI calculator\n"
                 "Standard deviation & variance\n"
                 "Ratio & proportion solver")
        content.add_widget(wrapped_label(ideas, 12, T["MUTED"], False, 110))
        content.add_widget(RoundedButton("OK", bg_color=T["PURPLE"], height=46,
                                          on_release=lambda *_: self.dismiss()))
        super().__init__(title="More Tools", content=content, **_popup_kwargs(310), **kwargs)


# ---------------------------------------------------------------------------
# SCREENS
# ---------------------------------------------------------------------------

class Splash(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(14))
        root.add_widget(BoxLayout())  # top spacer

        badge = IconBadge("Fx", bg_color=T["ICON_BG"], size_px=88, font_size=28)
        badge_row = BoxLayout(size_hint_y=None, height=dp(88))
        badge_row.add_widget(BoxLayout())
        badge_row.add_widget(badge)
        badge_row.add_widget(BoxLayout())
        root.add_widget(badge_row)

        root.add_widget(Label(text="MATH TOOLS", font_size=dp(30), bold=True, color=T["TEXT_PRIMARY"],
                               size_hint_y=None, height=dp(44)))
        root.add_widget(Label(text="Learn - Calculate - Discover", font_size=dp(13),
                               color=T["PURPLE_LIGHT"], size_hint_y=None, height=dp(26)))

        root.add_widget(BoxLayout())  # bottom spacer
        self.add_widget(root)

    def on_enter(self, *args):
        Clock.schedule_once(self._go_home, 3.5)

    def _go_home(self, *args):
        self.manager.current = "home"


class Home(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=[dp(16), dp(18), dp(16), dp(10)], spacing=dp(4))

        header = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        header.add_widget(HamburgerIcon(on_release=lambda *_: MenuPopup().open()))
        header.add_widget(Label(text="MATH TOOLS", font_size=dp(24), bold=True, color=T["TEXT_PRIMARY"],
                                 halign="left", valign="middle"))
        header.add_widget(ThemeToggle())
        root.add_widget(header)

        root.add_widget(Label(text="Learn - Calculate - Discover", font_size=dp(13), color=T["PURPLE_LIGHT"],
                               size_hint_y=None, height=dp(26)))

        sv = ScrollView(do_scroll_x=False)
        box = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None,
                         padding=[0, dp(6), 0, dp(6)])
        box.bind(minimum_height=box.setter("height"))

        for title, ids in CATEGORIES:
            pill_row = BoxLayout(size_hint_y=None, height=dp(34))
            pill_row.add_widget(SectionPill(title))
            pill_row.add_widget(BoxLayout())
            box.add_widget(pill_row)

            for tid in ids:
                t = TOOLS_BY_ID[tid]
                item = ListItem(icon_text=t[1], title=t[2], subtitle=t[3],
                                 on_release=lambda *_a, name=tid: self._open(name))
                box.add_widget(item)

        sv.add_widget(box)
        root.add_widget(sv)
        self.add_widget(root)

    def _open(self, name):
        self.manager.current = name


class ToolScreen(Screen):
    def __init__(self, tool_id, **kwargs):
        super().__init__(**kwargs)
        self.t = TOOLS_BY_ID[tool_id]
        (self.id_, self.icon, self.title, self.subtitle, self.hint,
         self.lesson, self.example, self.quiz_q, self.quiz_opts, self.quiz_answer) = self.t

        self.quiz_buttons = []
        self.quiz_answered = False

        root = BoxLayout(orientation="vertical", padding=[dp(16), dp(14), dp(16), dp(12)], spacing=dp(10))

        root.add_widget(TopBar(title=self.title,
                                on_back=lambda *_: self._go_home(),
                                on_home=lambda *_: self._go_home()))
        root.add_widget(Label(text=self.subtitle, font_size=dp(13), color=T["MUTED"],
                               size_hint_y=None, height=dp(22)))

        sv = ScrollView(do_scroll_x=False)
        col = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None, padding=[dp(2), dp(4)])
        col.bind(minimum_height=col.setter("height"))

        lesson_box = BoxLayout(orientation="vertical", padding=[dp(16), dp(14)], spacing=dp(6),
                                size_hint_y=None)
        add_rounded_bg(lesson_box, T["CARD"], radius=dp(20))
        lesson_box.add_widget(wrapped_label("HOW IT WORKS", 13, T["YELLOW"], True, 24))
        lesson_box.add_widget(wrapped_label(self.lesson, 13, T["TEXT"], False, 20))
        lesson_box.add_widget(wrapped_label("Example: " + self.example, 12, T["YELLOW"], False, 20))
        lesson_box.bind(minimum_height=lesson_box.setter("height"))
        col.add_widget(lesson_box)

        self.input = ClearableInput(hint_text=self.hint)
        col.add_widget(self.input)

        calc_btn = RoundedButton("CALCULATE", bg_color=T["PURPLE"], height=54,
                                  on_release=lambda *_: self._calculate())
        col.add_widget(calc_btn)

        self.result = ResultPanel()
        col.add_widget(self.result)

        col.add_widget(wrapped_label("QUICK QUESTION", 14, T["YELLOW"], True, 26))
        col.add_widget(wrapped_label(self.quiz_q, 14, T["TEXT"], False, 24))

        grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(116))
        for i, opt in enumerate(self.quiz_opts):
            qb = QuizOption(opt, on_release=lambda *_a, idx=i: self._answer(idx))
            self.quiz_buttons.append(qb)
            grid.add_widget(qb)
        col.add_widget(grid)

        self.quiz_feedback = ResultPanel()
        self.quiz_feedback.set_result("Pick an answer above", "", "neutral")
        col.add_widget(self.quiz_feedback)

        sv.add_widget(col)
        root.add_widget(sv)

        back_btn = RoundedButton("BACK", bg_color=T["PURPLE_DARK"], height=52,
                                  on_release=lambda *_: self._go_home())
        root.add_widget(back_btn)

        self.add_widget(root)

    def _go_home(self):
        self.manager.current = "home"

    def on_leave(self, *args):
        self.input.text = ""
        self.result.set_result("Result will appear here", "", "neutral")
        self.quiz_answered = False
        for qb in self.quiz_buttons:
            qb.reset()
        self.quiz_feedback.set_result("Pick an answer above", "", "neutral")

    def _calculate(self):
        s = self.input.text.strip()
        tid = self.id_
        try:
            if not s:
                raise ValueError("empty")

            if tid == "gcd":
                a, b = parse_numbers(s)[:2]
                self.result.set_result(f"GCD = {f_gcd(a, b)}", "", "success")

            elif tid == "lcm":
                a, b = parse_numbers(s)[:2]
                self.result.set_result(f"LCM = {f_lcm(a, b)}", "", "success")

            elif tid == "sum":
                vals = parse_numbers(s)
                self.result.set_result(f"Sum = {f_sum(vals)}", "", "success")

            elif tid == "average":
                vals = parse_numbers(s)
                r = round(f_average(vals), 4)
                self.result.set_result(f"Average = {r}", "", "success")

            elif tid == "power":
                a, b = parse_numbers(s)[:2]
                self.result.set_result(f"{a}^{b} = {f_power(a, b)}", "", "success")

            elif tid == "square_root":
                n = parse_numbers(s)[0]
                r = f_sqrt(n)
                if r is None:
                    self.result.set_result("No real square root", f"{n} is negative", "fail")
                else:
                    self.result.set_result(f"sqrt({n}) = {r}", "", "success")

            elif tid == "prime":
                n = int(parse_numbers(s)[0])
                if f_is_prime(n):
                    self.result.set_result(f"{n} IS PRIME", "", "success")
                else:
                    self.result.set_result(f"{n} IS NOT PRIME", "", "fail")

            elif tid == "even_odd":
                n = int(parse_numbers(s)[0])
                self.result.set_result(f"{n} is {f_even_odd(n).upper()}", "", "success")

            elif tid == "perfect_number":
                n = int(parse_numbers(s)[0])
                divs = f_divisors(n)[:-1] if n > 1 else []
                if f_perfect_number(n):
                    self.result.set_result(f"{n} IS A PERFECT NUMBER",
                                            " + ".join(map(str, divs)) + f" = {n}", "success")
                else:
                    self.result.set_result(f"{n} IS NOT A PERFECT NUMBER", "", "fail")

            elif tid == "prime_factors":
                n = int(parse_numbers(s)[0])
                if n < 2:
                    self.result.set_result("Enter a number greater than 1", "", "fail")
                else:
                    r = " x ".join(map(str, f_prime_factors(n)))
                    self.result.set_result(r, "", "success")

            elif tid == "divisors":
                n = int(parse_numbers(s)[0])
                if n <= 0:
                    self.result.set_result("Enter a positive number", "", "fail")
                else:
                    r = ", ".join(map(str, f_divisors(n)))
                    self.result.set_result("Divisors:", r, "success")

            elif tid == "reverse_number":
                n = int(parse_numbers(s)[0])
                self.result.set_result(f"Reverse = {f_reverse(n)}", "", "success")

            elif tid == "factorial":
                n = int(parse_numbers(s)[0])
                r = f_factorial(n)
                if r is None:
                    self.result.set_result("Enter n >= 0", "", "fail")
                else:
                    self.result.set_result(f"{n}! = {r}", "", "success")

            elif tid == "fibonacci":
                n = int(parse_numbers(s)[0])
                if not (1 <= n <= 50):
                    self.result.set_result("Enter 1 to 50", "", "fail")
                else:
                    r = f_fibonacci(n)
                    self.result.set_result("Fibonacci:", ", ".join(map(str, r)), "success")

            elif tid == "multiplication_table":
                n = int(parse_numbers(s)[0])
                rows = f_mult_table(n)
                self.result.set_result(f"Table of {n}", "\n".join(rows), "success")

            elif tid == "bmi":
                w, h = parse_numbers(s)[:2]
                bmi = f_bmi(w, h)
                self.result.set_result(f"BMI = {round(bmi, 1)} ({bmi_category(bmi)})", "", "success")

            elif tid == "bmr":
                tokens = s.split()
                w, h, age = float(tokens[0]), float(tokens[1]), float(tokens[2])
                gender = tokens[3]
                bmr = f_bmr(w, h, age, gender)
                self.result.set_result(f"BMR = {round(bmr)} kcal/day", "", "success")

            elif tid == "body_fat":
                tokens = s.split()
                waist, neck, height = float(tokens[0]), float(tokens[1]), float(tokens[2])
                gender = tokens[3]
                hip = float(tokens[4]) if len(tokens) > 4 else None
                bf = f_body_fat(waist, neck, height, gender, hip)
                self.result.set_result(f"Body fat = {round(bf, 1)}%", "", "success")

            elif tid == "percentage":
                x, y = parse_numbers(s)[:2]
                r = f_percentage_of(x, y)
                self.result.set_result(f"{x}% of {y} = {round(r, 2)}", "", "success")

            elif tid == "unit_converter":
                tokens = s.split()
                value = float(tokens[0])
                frm, to = tokens[1], tokens[2]
                r = convert_unit(value, frm, to)
                self.result.set_result(f"{value} {frm} = {round(r, 4)} {to}", "", "success")

            elif tid == "interest":
                tokens = s.split()
                p, rate, t = float(tokens[0]), float(tokens[1]), float(tokens[2])
                kind = tokens[3] if len(tokens) > 3 else "s"
                interest, total = f_interest(p, rate, t, kind)
                self.result.set_result(f"Interest = {round(interest, 2)}", f"Total = {round(total, 2)}", "success")

            elif tid == "bill_split":
                tokens = s.split()
                total, people = float(tokens[0]), int(tokens[1])
                tip = float(tokens[2]) if len(tokens) > 2 else 0
                total_tip, per = f_bill_split(total, people, tip)
                self.result.set_result(f"Total with tip = {round(total_tip, 2)}",
                                        f"Each person pays {round(per, 2)}", "success")

            elif tid == "quadratic":
                a, b, c = parse_numbers(s)[:3]
                kind, roots = f_quadratic(a, b, c)
                if kind == "real2":
                    self.result.set_result(f"x1 = {round(roots[0], 3)}, x2 = {round(roots[1], 3)}", "", "success")
                elif kind == "real1":
                    self.result.set_result(f"x = {round(roots[0], 3)}", "(double root)", "success")
                else:
                    real, imag = roots
                    self.result.set_result(
                        f"x1 = {round(real, 3)}+{round(imag, 3)}i, x2 = {round(real, 3)}-{round(imag, 3)}i",
                        "", "success")

            elif tid == "shapes":
                tokens = s.split()
                shape = tokens[0]
                dims = [float(x) for x in tokens[1:]]
                area = f_shape_area(shape, dims)
                self.result.set_result(f"{shape.title()} area = {round(area, 2)}", "", "success")

            elif tid == "base_converter":
                tokens = s.split()
                num, fb, tb = tokens[0], int(tokens[1]), int(tokens[2])
                r = convert_base(num, fb, tb)
                self.result.set_result(f"{num} (base {fb}) = {r} (base {tb})", "", "success")

            elif tid == "weighted_average":
                nums = parse_numbers(s)
                pairs = list(zip(nums[0::2], nums[1::2]))
                r = f_weighted_average(pairs)
                self.result.set_result(f"Weighted average = {round(r, 2)}", "", "success")

            elif tid == "random_tool":
                low_s = s.lower().strip()
                if "d" in low_s and " " not in low_s:
                    n_part, m_part = low_s.split("d")
                    n = int(n_part) if n_part else 1
                    m = int(m_part)
                    rolls, total = roll_dice(n, m)
                    self.result.set_result(f"Rolled: {rolls}", f"Total = {total}", "success")
                else:
                    a, b = parse_numbers(s)[:2]
                    r = random.randint(int(a), int(b))
                    self.result.set_result(f"Random number = {r}", "", "success")

            elif tid == "age_calculator":
                years, months, days = calculate_age(s.strip())
                self.result.set_result(f"Age = {years} years, {months} months, {days} days", "", "success")

        except Exception:
            self.result.set_result("Please enter valid numbers.", "", "fail")

    def _answer(self, idx):
        if self.quiz_answered:
            return
        self.quiz_answered = True
        for i, qb in enumerate(self.quiz_buttons):
            if i == self.quiz_answer:
                qb.mark_correct()
            elif i == idx:
                qb.mark_wrong()

        if idx == self.quiz_answer:
            self.quiz_feedback.set_result(
                "Correct!", f"{self.quiz_q} -> {self.quiz_opts[self.quiz_answer]}", "success")
        else:
            self.quiz_feedback.set_result(
                "Not quite!", f"Correct answer: {self.quiz_opts[self.quiz_answer]}", "fail")


# ---------------------------------------------------------------------------
# APP
# ---------------------------------------------------------------------------

class MathToolsApp(App):
    def build(self):
        Window.clearcolor = T["BG"]
        self.sm = ScreenManager(transition=NoTransition())
        self.sm.add_widget(Splash(name="splash"))
        self.sm.add_widget(Home(name="home"))
        for tool_id in TOOLS_BY_ID:
            self.sm.add_widget(ToolScreen(tool_id, name=tool_id))
        self.sm.current = "splash"
        return self.sm

    def toggle_theme(self):
        global CURRENT_THEME
        CURRENT_THEME = "light" if CURRENT_THEME == "dark" else "dark"
        T.clear()
        T.update(PALETTES[CURRENT_THEME])
        save_theme_pref(CURRENT_THEME)
        self._rebuild_screens()

    def _rebuild_screens(self):
        current = self.sm.current
        self.sm.clear_widgets()
        self.sm.add_widget(Home(name="home"))
        for tool_id in TOOLS_BY_ID:
            self.sm.add_widget(ToolScreen(tool_id, name=tool_id))
        Window.clearcolor = T["BG"]
        self.sm.current = current if current in self.sm.screen_names else "home"


if __name__ == "__main__":
    MathToolsApp().run()
