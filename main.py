from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget


# =========================================================
# WINDOW SETUP
# =========================================================
Window.clearcolor = (0.96, 0.97, 0.99, 1)  # Soft premium background color like the image


# =========================================================
# PREDICTION LOGIC (All Updated Rules Retained Perfectly)
# =========================================================

def get_big_small(num):
    return "Big" if num >= 5 else "Small"


def predict_pattern_1(history):
    if len(history) < 4:
        return "No Prediction"
    p1 = history[-4]
    p3 = history[-2]
    if p1 == p3:
        return "No Prediction"
    steps = (p3 - p1) % 10
    predicted = (p3 + steps) % 10
    return get_big_small(predicted)


def predict_pattern_2(history, period_counts):
    if len(history) < 2:
        return "No Prediction"
    last_num = history[-1]
    current_idx = len(history) - 1
    current_period_parity = period_counts[current_idx] % 2
    lookback = min(20, len(history) - 1)

    for i in range(2, lookback + 1):
        idx = len(history) - i
        if period_counts[idx] % 2 == current_period_parity:
            if history[idx] == last_num:
                if idx + 1 < len(history):
                    return get_big_small(history[idx + 1])
    return "No Prediction"


def predict_pattern_3(history):
    # Main numbers for Pattern 3
    main_numbers = {6, 3, 1, 8}

    if not history:
        return "No Prediction"

    # If a pair of consecutive periods are both main numbers,
    # the next two predictions are No Prediction. This applies
    # regardless of what numbers appear in those next periods.
    for i in range(len(history) - 2, -1, -1):
        if history[i] in main_numbers and history[i + 1] in main_numbers:
            periods_after_pair = (len(history) - 1) - (i + 1)
            if periods_after_pair in (0, 1):
                return "No Prediction"
            break

    # A prediction is calculated only when the latest period
    # ends with a main number.
    if history[-1] not in main_numbers:
        return "No Prediction"

    # Find the latest main number and the previous main number.
    latest_main_index = len(history) - 1
    previous_main_index = None

    for i in range(latest_main_index - 1, -1, -1):
        if history[i] in main_numbers:
            previous_main_index = i
            break

    if previous_main_index is None:
        return "No Prediction"

    # Count only the numbers strictly between the two main numbers.
    middle_numbers = history[previous_main_index + 1:latest_main_index]

    if not middle_numbers:
        return "No Prediction"

    big_count = sum(1 for n in middle_numbers if n >= 5)
    small_count = sum(1 for n in middle_numbers if n < 5)

    if big_count == small_count:
        return "No Prediction"
    return "Big" if big_count > small_count else "Small"


def predict_pattern_4(history):
    if len(history) < 2:
        return "No Prediction"
    small_combo = {0, 2, 4}
    big_combo = {5, 7, 9}

    if len(history) >= 3:
        last_3 = history[-3:]
        if all(n in small_combo for n in last_3) or all(n in big_combo for n in last_3):
            return "No Prediction"

    last_2 = history[-2:]
    if all(n in small_combo for n in last_2):
        return "Small"
    if all(n in big_combo for n in last_2):
        return "Big"
    return "No Prediction"


def predict_new_combo_rules(history):
    if len(history) < 5:
        return "No Prediction"
    last_5 = [get_big_small(n) for n in history[-5:]]

    sequences = {
        ("Small", "Big", "Small", "Small", "Big"): "Big",
        ("Small", "Small", "Big", "Big", "Small"): "Big",
        ("Small", "Small", "Big", "Small", "Big"): "Big",
        ("Big", "Big", "Small", "Big", "Small"): "Small",
        ("Big", "Big", "Small", "Small", "Big"): "Small",
        ("Big", "Big", "Small", "Small", "Small"): "Big",
        ("Small", "Big", "Big", "Big", "Small"): "Small",
        ("Big", "Small", "Small", "Small", "Big"): "Big",
        ("Small", "Small", "Big", "Big", "Big"): "Small"
    }
    return sequences.get(tuple(last_5), "No Prediction")


def predict_sequence_rule(history):
    if len(history) < 2:
        return "No Prediction"
    a = history[-2]
    b = history[-1]

    if (b - a) % 10 == 1:
        return get_big_small((b + 1) % 10)
    if (a - b) % 10 == 1:
        return get_big_small((b - 1) % 10)
    return "No Prediction"


def predict_missing_average_rule(history):
    # Rule 7 starts from the 21st period.
    # The first 20 periods are the initial history.
    if len(history) < 21:
        return "No Prediction"

    votes = []

    for digit in range(10):
        positions = [i for i, n in enumerate(history) if n == digit]
        if len(positions) < 2:
            continue

        # Current missing count from the latest occurrence.
        current_missing = len(history) - 1 - positions[-1]

        # Dynamically use every completed gap between occurrences.
        intervals = [
            positions[i] - positions[i - 1] - 1
            for i in range(1, len(positions))
        ]

        average_missing = sum(intervals) / len(intervals)

        if current_missing == average_missing:
            votes.append("Small" if digit <= 4 else "Big")

    if not votes:
        return "No Prediction"

    big_count = votes.count("Big")
    small_count = votes.count("Small")

    if big_count > small_count:
        return "Big"
    if small_count > big_count:
        return "Small"
    return "No Prediction"


def calculate_final_result(predictions):
    valid_votes = [p for p in predictions if p in ("Big", "Small")]
    if not valid_votes:
        return "No Prediction"
    big_c = valid_votes.count("Big")
    small_c = valid_votes.count("Small")
    if big_c > small_c: return "Big"
    if small_c > big_c: return "Small"
    return "Big and Small"


def calculate_backup_number(history):
    """Calculate the backup number from the last period and its alternative.

    For the next prediction, compare the latest period with the period
    two places before it (the alternative period). Count the clockwise
    gap from the alternative number to the latest number. Then move
    forward by that same gap from the latest number.

    Examples:
      1, 4, 3 -> alternative 1 and latest 3: gap 2, result 5.
      8, 9, 3 -> alternative 8 and latest 3: gap 5, result 8.
      3, 8, 3 -> alternative 3 and latest 3: gap 0, result 3.
    """
    if len(history) < 3:
        return None

    alternative_period = history[-3]
    latest_period = history[-1]
    gap = (latest_period - alternative_period) % 10

    return (latest_period + gap) % 10


# =========================================================
# NEW PREMIUM 3D GLOSSY BALL DESIGN WIDGET
# =========================================================

class NumberCircle(Button):

    def __init__(self, number, number_color, split_colors=None, **kwargs):
        super().__init__(**kwargs)

        self.number = str(number)
        self.number_color = number_color
        self.split_colors = split_colors

        self.size_hint_y = None
        self.height = dp(75)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        self.text = self.number
        self.color = number_color
        self.font_size = "26sp"
        self.bold = True

        with self.canvas.before:
            # 1. Soft Outer Shadow Ring
            self.shadow_color = Color(0, 0, 0, 0.06)
            self.shadow_ellipse = Ellipse()

            # 2. Main Outer Colored Spherical Border
            self.outer_color = Color(1, 1, 1, 1)
            self.outer_circle = Ellipse()

            # 3. Secondary Split Layer (For 0 & 5)
            self.second_color = Color(1, 1, 1, 1)
            self.second_circle = Ellipse()

            # 4. Premium White Inner Core Capsule
            self.inner_color = Color(0.98, 0.98, 0.98, 1)
            self.inner_circle = Ellipse()

            # 5. Top Glossy Shine Reflection Arc (3D Glass Look)
            self.shine_color = Color(1, 1, 1, 0.45)
            self.shine_ellipse = Ellipse()

        self.bind(pos=self.update_circle, size=self.update_circle)

    def update_circle(self, *args):
        # Calculate dynamic bounds perfectly matching proportions
        ball_size = min(self.width, self.height) * 0.92
        x = self.center_x - ball_size / 2
        y = self.center_y - ball_size / 2

        # Draw Outer Soft Drop Shadow
        self.shadow_color.rgba = (0, 0, 0, 0.05)
        self.shadow_ellipse.pos = (x, y - dp(2))
        self.shadow_ellipse.size = (ball_size, ball_size)

        # Setup base color structure matching split logic perfectly
        if self.split_colors and len(self.split_colors) >= 2:
            c1 = self.split_colors[0]
            c2 = self.split_colors[1]

            # Left side split rendering
            self.outer_color.rgb = (c1[0], c1[1], c1[2])
            self.outer_circle.pos = (x, y)
            self.outer_circle.size = (ball_size, ball_size)
            self.outer_circle.angle_start = 0
            self.outer_circle.angle_end = 180

            # Right side split rendering
            self.second_color.rgb = (c2[0], c2[1], c2[2])
            self.second_circle.pos = (x, y)
            self.second_circle.size = (ball_size, ball_size)
            self.second_circle.angle_start = 180
            self.second_circle.angle_end = 360
        else:
            # Solid sphere filling format
            self.outer_color.rgb = (self.number_color[0], self.number_color[1], self.number_color[2]) if hasattr(self.number_color, '__len__') else (0.8, 0.1, 0.1)
            self.outer_circle.pos = (x, y)
            self.outer_circle.size = (ball_size, ball_size)
            self.outer_circle.angle_start = 0
            self.outer_circle.angle_end = 360
            
            # Deactivate second layer logic
            self.second_color.rgba = (0, 0, 0, 0)
            self.second_circle.size = (0, 0)

        # Draw Premium Inner Sphere Core Frame (Creates the clean circular mask inside)
        inner_size = ball_size * 0.76
        ix = self.center_x - inner_size / 2
        iy = self.center_y - inner_size / 2
        
        # Subtle light gray/white radial base to mimic image gradients
        self.inner_color.rgba = (0.96, 0.98, 0.98, 1)
        self.inner_circle.pos = (ix, iy)
        self.inner_circle.size = (inner_size, inner_size)

        # Draw Top Glass Reflection Highlight Accent Layer
        shine_w = inner_size * 0.85
        shine_h = inner_size * 0.4
        sx = self.center_x - shine_w / 2
        sy = (iy + inner_size) - shine_h - dp(2)
        
        self.shine_color.rgba = (1, 1, 1, 0.6)
        self.shine_ellipse.pos = (sx, sy)
        self.shine_ellipse.size = (shine_w, shine_h)
# =========================================================
# MAIN APP
# =========================================================

class WingoPredictorApp(App):

    def build(self):

        self.history = []
        self.period_counts = []

        # =================================================
        # SCROLL VIEW
        # =================================================

        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True
        )

        # =================================================
        # MAIN CONTENT
        # =================================================

        content = BoxLayout(
            orientation="vertical",
            padding=[
                dp(12),
                dp(18),
                dp(12),
                dp(25)
            ],
            spacing=dp(10),
            size_hint_y=None
        )

        content.bind(
            minimum_height=content.setter(
                "height"
            )
        )

        # =================================================
        # TITLE
        # =================================================

        title = Label(
            text="WINGO SMART PREDICTOR",
            font_size="24sp",
            bold=True,
            color=(
                1,
                0.75,
                0,
                1
            ),
            size_hint_y=None,
            height=dp(48)
        )

        content.add_widget(title)

        # =================================================
        # NEXT PREDICTION
        # =================================================

        next_title = Label(
            text="NEXT PREDICTION",
            font_size="22sp",
            bold=True,
            color=(
                0,
                0.35,
                0.05,
                1
            ),
            size_hint_y=None,
            height=dp(42)
        )

        content.add_widget(next_title)

        # =================================================
        # WAITING / PREDICTION STATUS
        # =================================================

        self.result_label = Label(
            text="Waiting...",
            font_size="25sp",
            bold=True,
            color=(
                0.70,
                0.50,
                0,
                1
            ),
            size_hint_y=None,
            height=dp(48)
        )

        content.add_widget(
            self.result_label
        )

        content.add_widget(
            Widget(
                size_hint_y=None,
                height=dp(8)
            )
        )

        # =================================================
        # SELECT NUMBERS
        # =================================================

        select_label = Label(
            text="SELECT NUMBERS",
            font_size="21sp",
            bold=True,
            color=(
                0,
                0.15,
                0.45,
                1
            ),
            size_hint_y=None,
            height=dp(42)
        )

        content.add_widget(
            select_label
        )

        # =================================================
        # NUMBER GRID
        # =================================================

        number_grid = GridLayout(
            cols=5,
            rows=2,
            spacing=[
                dp(5),
                dp(20)
            ],
            padding=[
                dp(4),
                dp(5),
                dp(4),
                dp(5)
            ],
            size_hint_y=None,
            height=dp(200),
            row_default_height=dp(82),
            row_force_default=True
        )

        # =================================================
        # COLORS
        # =================================================

        GREEN = (
            0.0,
            0.70,
            0.35,
            1
        )

        RED = (
            0.90,
            0.05,
            0.08,
            1
        )

        VIOLET = (
            0.50,
            0.05,
            0.90,
            1
        )

        # =================================================
        # NUMBERS 0 - 9
        # =================================================

        btn = NumberCircle(
            0,
            VIOLET,
            split_colors=[
                VIOLET,
                RED
            ]
        )
        btn.bind(
            on_release=lambda x:
            self.number_clicked(0)
        )
        number_grid.add_widget(btn)

        btn = NumberCircle(
            1,
            GREEN
        )
        btn.bind(
            on_release=lambda x:
            self.number_clicked(1)
        )
        number_grid.add_widget(btn)

        btn = NumberCircle(
            2,
            RED
        )
        btn.bind(
            on_release=lambda x:
            self.number_clicked(2)
        )
        number_grid.add_widget(btn)

        btn = NumberCircle(
            3,
            GREEN
        )
        btn.bind(
            on_release=lambda x:
            self.number_clicked(3)
        )
        number_grid.add_widget(btn)

        btn = NumberCircle(
            4,
            RED
        )
        btn.bind(
            on_release=lambda x:
            self.number_clicked(4)
        )
        number_grid.add_widget(btn)

        btn = NumberCircle(
            5,
            VIOLET,
            split_colors=[
                VIOLET,
                GREEN
            ]
        )
        btn.bind(
            on_release=lambda x:
            self.number_clicked(5)
        )
        number_grid.add_widget(btn)

        btn = NumberCircle(
            6,
            RED
        )
        btn.bind(
            on_release=lambda x:
            self.number_clicked(6)
        )
        number_grid.add_widget(btn)

        btn = NumberCircle(
            7,
            GREEN
        )
        btn.bind(
            on_release=lambda x:
            self.number_clicked(7)
        )
        number_grid.add_widget(btn)

        btn = NumberCircle(
            8,
            RED
        )
        btn.bind(
            on_release=lambda x:
            self.number_clicked(8)
        )
        number_grid.add_widget(btn)

        btn = NumberCircle(
            9,
            GREEN
        )
        btn.bind(
            on_release=lambda x:
            self.number_clicked(9)
        )
        number_grid.add_widget(btn)

        content.add_widget(
            number_grid
        )

        content.add_widget(
            Widget(
                size_hint_y=None,
                height=dp(10)
            )
        )

        # =================================================
        # LAST 20 PERIODS
        # =================================================

        history_title = Label(
            text="LAST 20 PERIODS",
            font_size="20sp",
            bold=True,
            color=(
                0.0,
                0.0,
                0.55,
                1
            ),
            size_hint_y=None,
            height=dp(40)
        )

        content.add_widget(
            history_title
        )

        # =================================================
        # HISTORY GRID
        # =================================================

        self.history_grid = GridLayout(
            cols=2,
            spacing=[
                dp(10),
                dp(5)
            ],
            padding=[
                dp(5),
                dp(2)
            ],
            size_hint_y=None
        )

        self.history_grid.bind(
            minimum_height=self.history_grid.setter(
                "height"
            )
        )

        history_scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            size_hint_y=None,
            height=dp(150)
        )

        history_scroll.add_widget(
            self.history_grid
        )

        content.add_widget(
            history_scroll
        )

        # =================================================
        # 7 PREDICTION RULES
        # =================================================

        rules_title = Label(
            text="7 PREDICTION RULES",
            font_size="20sp",
            bold=True,
            color=(
                1,
                0.85,
                0,
                1
            ),
            size_hint_y=None,
            height=dp(42)
        )

        content.add_widget(
            rules_title
        )

        self.rules_box = BoxLayout(
            orientation="vertical",
            spacing=dp(7),
            size_hint_y=None
        )

        self.rules_box.bind(
            minimum_height=self.rules_box.setter(
                "height"
            )
        )

        content.add_widget(
            self.rules_box
        )

        # =================================================
        # FINAL RESULT
        # =================================================

        content.add_widget(
            Widget(
                size_hint_y=None,
                height=dp(8)
            )
        )

        self.final_label = Label(
            text="FINAL RESULT",
            markup=True,
            font_size="23sp",
            bold=True,
            color=(
                1,
                0.35,
                0,
                1
            ),
            size_hint_y=None,
            height=dp(48)
        )

        content.add_widget(
            self.final_label
        )

        # =================================================
        # BACKUP NUMBER
        # =================================================

        self.backup_label = Label(
            text="[color=008B8B]BACKUP NUMBER:[/color] --",
            markup=True,
            font_size="19sp",
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )

        content.add_widget(
            self.backup_label
        )

        # =================================================
        # RESET BUTTON
        # =================================================

        # RESET + LAST ENTRY DELETE
        reset_delete_box = BoxLayout(
            orientation="horizontal",
            spacing=dp(5),
            size_hint_y=None,
            height=dp(48)
        )

        reset_button = Button(
            text="RESET",
            font_size="17sp",
            bold=True,
            size_hint_x=0.75,
            background_normal="",
            background_color=(
                0.80,
                0.10,
                0.10,
                1
            ),
            color=(
                1,
                1,
                1,
                1
            )
        )

        reset_button.bind(
            on_release=lambda x:
            self.reset_all()
        )

        delete_button = Button(
            text="×",
            font_size="24sp",
            bold=True,
            size_hint_x=0.25,
            background_normal="",
            background_color=(
                0.45,
                0.02,
                0.02,
                1
            ),
            color=(
                1,
                1,
                1,
                1
            )
        )

        delete_button.bind(
            on_release=lambda x:
            self.delete_last()
        )

        reset_delete_box.add_widget(reset_button)
        reset_delete_box.add_widget(delete_button)

        content.add_widget(reset_delete_box)

        # =================================================
        # INITIAL DISPLAY
        # =================================================

        self.update_history_display()

        self.clear_predictions()

        # =================================================
        # PUT CONTENT INSIDE SCROLL
        # =================================================

        scroll.add_widget(
            content
        )

        return scroll

    # =====================================================
    # NUMBER CLICK
    # =====================================================

    def number_clicked(self, number):

        # IMPORTANT:
        # DO NOT LIMIT HISTORY TO 20.
        # Every new period is stored.

        self.history.append(number)

        period_number = len(
            self.history
        )

        self.period_counts.append(
            period_number
        )

        self.update_history_display()

        # -----------------------------------------------
        # WAITING
        # -----------------------------------------------

        if len(self.history) < 20:

            remaining = (
                20 - len(self.history)
            )

            self.result_label.text = (
                "Waiting... "
                + str(remaining)
                + " more"
            )

            self.result_label.color = (
                0.70,
                0.50,
                0,
                1
            )

            self.clear_predictions()

            backup_number = calculate_backup_number(self.history)
            if backup_number is not None:
                self.backup_label.text = (
                    "[color=008B8B]BACKUP NUMBER:[/color] "
                    + "[color=000000]"
                    + str(backup_number)
                    + "[/color]"
                )
            else:
                self.backup_label.text = "[color=008B8B]BACKUP NUMBER:[/color] --"

            return

        # -----------------------------------------------
        # 7 RULES
        # -----------------------------------------------

        p1 = predict_pattern_1(
            self.history
        )

        p2 = predict_pattern_2(
            self.history,
            self.period_counts
        )

        p3 = predict_pattern_3(
            self.history
        )

        p4 = predict_pattern_4(
            self.history
        )

        p5 = predict_new_combo_rules(
            self.history
        )

        p6 = predict_sequence_rule(
            self.history
        )

        p7 = predict_missing_average_rule(
            self.history
        )

        predictions = [
            p1,
            p2,
            p3,
            p4,
            p5,
            p6,
            p7
        ]

        self.show_predictions(
            predictions
        )

        # -----------------------------------------------
        # FINAL
        # -----------------------------------------------

        final = calculate_final_result(
            predictions
        )

        if final == "Big":
            self.final_label.text = (
                "[color=33AA33]FINAL RESULT:[/color] "
                "[color=FFC000]Big[/color]"
            )
        elif final == "Small":
            self.final_label.text = (
                "[color=33AA33]FINAL RESULT:[/color] "
                "[color=66CCFF]Small[/color]"
            )
        else:
            self.final_label.text = (
                "[color=33AA33]FINAL RESULT:[/color] "
                + final
            )

        self.final_label.color = (
            0.20,
            0.67,
            0.20,
            1
        )

        self.result_label.text = (
            "Prediction Ready"
        )

        self.result_label.color = (
            0,
            0.35,
            0.05,
            1
        )

        backup_number = calculate_backup_number(self.history)
        if backup_number is not None:
            self.backup_label.text = (
                "[color=008B8B]BACKUP NUMBER:[/color] "
                + "[color=000000]"
                + str(backup_number)
                + "[/color]"
            )
        else:
            self.backup_label.text = "[color=008B8B]BACKUP NUMBER:[/color] --"

    # =====================================================
    # HISTORY DISPLAY
    # =====================================================

    def update_history_display(self):

        self.history_grid.clear_widgets()

        # =================================================
        # ONLY DISPLAY THE LATEST 20 PERIODS
        # HISTORY ITSELF IS NOT LIMITED
        # =================================================

        total = len(self.history)

        start_index = max(
            0,
            total - 20
        )

        visible_periods = list(
            range(
                start_index,
                total
            )
        )

        # Split latest 20 into two columns:
        # first 10 on left, next 10 on right

        left_periods = visible_periods[:10]
        right_periods = visible_periods[10:]

        max_rows = max(
            len(left_periods),
            len(right_periods)
        )

        for row in range(max_rows):

            # -------------------------------------------
            # LEFT COLUMN
            # -------------------------------------------

            if row < len(left_periods):

                index = left_periods[row]

                number = self.history[index]

                period_number = index + 1

                number_color_hex = {
                    0: "8000E6", 1: "00B359", 2: "E60D14",
                    3: "00B359", 4: "E60D14", 5: "8000E6",
                    6: "E60D14", 7: "00B359", 8: "E60D14",
                    9: "00B359"
                }[number]
                big_small = get_big_small(number)
                big_small_color_hex = "FFC000" if big_small == "Big" else "66CCFF"
                text = (
                    "[color=00008B]Period "
                    + str(period_number)
                    + " :[/color] "
                    + "[color=" + number_color_hex + "]"
                    + str(number)
                    + "[/color]  "
                    + "[color=" + big_small_color_hex + "]"
                    + big_small
                    + "[/color]"
                )

            else:

                text = ""

            left_label = Label(
                text=text,
                markup=True,
                font_size="14sp",
                color=(
                    0.05,
                    0.05,
                    0.15,
                    1
                ),
                halign="left",
                valign="middle",
                size_hint_y=None,
                height=dp(28)
            )

            left_label.bind(
                size=lambda instance,
                value: setattr(
                    instance,
                    "text_size",
                    value
                )
            )

            self.history_grid.add_widget(
                left_label
            )

            # -------------------------------------------
            # RIGHT COLUMN
            # -------------------------------------------

            if row < len(right_periods):

                index = right_periods[row]

                number = self.history[index]

                period_number = index + 1

                number_color_hex = {
                    0: "8000E6", 1: "00B359", 2: "E60D14",
                    3: "00B359", 4: "E60D14", 5: "8000E6",
                    6: "E60D14", 7: "00B359", 8: "E60D14",
                    9: "00B359"
                }[number]
                big_small = get_big_small(number)
                big_small_color_hex = "FFC000" if big_small == "Big" else "66CCFF"
                text = (
                    "[color=00008B]Period "
                    + str(period_number)
                    + " :[/color] "
                    + "[color=" + number_color_hex + "]"
                    + str(number)
                    + "[/color]  "
                    + "[color=" + big_small_color_hex + "]"
                    + big_small
                    + "[/color]"
                )

            else:

                text = ""

            right_label = Label(
                text=text,
                markup=True,
                font_size="14sp",
                color=(
                    0.05,
                    0.05,
                    0.15,
                    1
                ),
                halign="left",
                valign="middle",
                size_hint_y=None,
                height=dp(28)
            )

            right_label.bind(
                size=lambda instance,
                value: setattr(
                    instance,
                    "text_size",
                    value
                )
            )

            self.history_grid.add_widget(
                right_label
            )

    # =====================================================
    # CLEAR RULES
    # =====================================================

    def clear_predictions(self):

        self.rules_box.clear_widgets()

        for i in range(1, 8):

            rule_label = Label(
                text=(
                    "Rule "
                    + str(i)
                ),
                font_size="17sp",
                bold=True,
                color=(
                    1.0,
                    0.20,
                    0.60,
                    1
                ),
                size_hint_y=None,
                height=dp(28)
            )

            result_label = Label(
                text="No Prediction",
                font_size="15sp",
                color=(
                    0.20,
                    0.20,
                    0.30,
                    1
                ),
                size_hint_y=None,
                height=dp(28)
            )

            self.rules_box.add_widget(
                rule_label
            )

            self.rules_box.add_widget(
                result_label
            )

            if i < 7:

                self.rules_box.add_widget(
                    Widget(
                        size_hint_y=None,
                        height=dp(5)
                    )
                )

    # =====================================================
    # SHOW PREDICTIONS
    # =====================================================

    def show_predictions(
        self,
        predictions
    ):

        self.rules_box.clear_widgets()

        for i, prediction in enumerate(
            predictions,
            start=1
        ):

            rule_label = Label(
                text=(
                    "Rule "
                    + str(i)
                ),
                font_size="17sp",
                bold=True,
                color=(
                    1.0,
                    0.20,
                    0.60,
                    1
                ),
                size_hint_y=None,
                height=dp(28)
            )

            if prediction == "Big":

                prediction_color = (
                    1,
                    0.75,
                    0,
                    1
                )

            elif prediction == "Small":

                prediction_color = (
                    0.40,
                    0.80,
                    1.0,
                    1
                )

            else:

                prediction_color = (
                    0.25,
                    0.25,
                    0.30,
                    1
                )

            result_label = Label(
                text=prediction,
                font_size="15sp",
                bold=True,
                color=prediction_color,
                size_hint_y=None,
                height=dp(28)
            )

            self.rules_box.add_widget(
                rule_label
            )

            self.rules_box.add_widget(
                result_label
            )

            if i < 7:

                self.rules_box.add_widget(
                    Widget(
                        size_hint_y=None,
                        height=dp(6)
                    )
                )

    # =====================================================
    # DELETE LAST ENTRY
    # =====================================================

    def delete_last(self):

        if not self.history:
            return

        self.history.pop()
        self.period_counts.pop()

        self.update_history_display()

        if len(self.history) < 20:
            remaining = 20 - len(self.history)
            self.result_label.text = (
                "Waiting... " + str(remaining) + " more"
            )
            self.result_label.color = (
                0.70, 0.50, 0, 1
            )
            self.clear_predictions()
            self.final_label.text = "FINAL RESULT"
            self.final_label.color = (
                0.20, 0.67, 0.20, 1
            )
            backup_number = calculate_backup_number(self.history)
            if backup_number is not None:
                self.backup_label.text = (
                    "[color=008B8B]BACKUP NUMBER:[/color] "
                    + "[color=000000]"
                    + str(backup_number)
                    + "[/color]"
                )
            else:
                self.backup_label.text = "[color=008B8B]BACKUP NUMBER:[/color] --"
            return

        predictions = [
            predict_pattern_1(self.history),
            predict_pattern_2(self.history, self.period_counts),
            predict_pattern_3(self.history),
            predict_pattern_4(self.history),
            predict_new_combo_rules(self.history),
            predict_sequence_rule(self.history),
            predict_missing_average_rule(self.history)
        ]

        self.show_predictions(predictions)

        final = calculate_final_result(predictions)

        if final == "Big":
            self.final_label.text = (
                "[color=33AA33]FINAL RESULT:[/color] "
                "[color=FFC000]Big[/color]"
            )
        elif final == "Small":
            self.final_label.text = (
                "[color=33AA33]FINAL RESULT:[/color] "
                "[color=66CCFF]Small[/color]"
            )
        else:
            self.final_label.text = (
                "[color=33AA33]FINAL RESULT:[/color] " + final
            )

        self.final_label.color = (
            0.20, 0.67, 0.20, 1
        )

        self.result_label.text = "Prediction Ready"
        self.result_label.color = (
            0, 0.35, 0.05, 1
        )

        backup_number = calculate_backup_number(self.history)
        if backup_number is not None:
            self.backup_label.text = (
                "[color=008B8B]BACKUP NUMBER:[/color] "
                + "[color=000000]"
                + str(backup_number)
                + "[/color]"
            )
        else:
            self.backup_label.text = "[color=008B8B]BACKUP NUMBER:[/color] --"

    # =====================================================
    # RESET
    # =====================================================

    def reset_all(self):

        self.history = []

        self.period_counts = []

        self.result_label.text = (
            "Waiting..."
        )

        self.result_label.color = (
            0.70,
            0.50,
            0,
            1
        )

        self.final_label.text = (
            "FINAL RESULT"
        )

        self.final_label.color = (
            0.20,
            0.67,
            0.20,
            1
        )

        self.backup_label.text = "[color=008B8B]BACKUP NUMBER:[/color] --"

        self.update_history_display()

        self.clear_predictions()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    WingoPredictorApp().run()