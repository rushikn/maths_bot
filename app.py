import random
import streamlit as st

st.set_page_config(
    page_title="Math Practice",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
      .block-container { max-width: 850px; padding-top: 2rem; padding-bottom: 3rem; }
      [data-testid="stSidebar"] { border-right: 1px solid rgba(128,128,128,.2); }
      .hero { text-align:center; padding: 1.2rem 0 .7rem 0; }
      .hero h1 { font-size: 2.25rem; margin-bottom: .25rem; }
      .hero p { opacity: .72; font-size: 1rem; }
      .question-card {
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 22px;
        padding: 2rem 1.5rem 1.4rem 1.5rem;
        text-align: center;
        margin: 1.2rem 0 1rem 0;
        background: rgba(128,128,128,.035);
      }
      .question-label { font-size: .9rem; opacity: .7; margin-bottom: .6rem; }
      .question { font-size: clamp(2.5rem, 7vw, 4rem); font-weight: 750; letter-spacing: -1px; }
      .subtle { text-align:center; opacity:.7; font-size:.9rem; }
      div.stButton > button { border-radius: 12px; min-height: 2.8rem; font-weight: 600; }
      div[data-testid="stFormSubmitButton"] button { border-radius: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Session state helpers
# -----------------------------
def init_state():
    defaults = {
        "section": "Tables Practice",
        "active": False,
        "finished": False,
        "current_question": None,
        "previous_question": None,
        "feedback": None,
        "feedback_answer": None,
        "feedback_correct": None,
        "correct": 0,
        "wrong": 0,
        "history": [],
        "question_number": 0,
        "from_table": 1,
        "to_table": 10,
        "square_min": 1,
        "square_max": 30,
        "cube_min": 1,
        "cube_max": 15,
        "range_signature": None,
        "applied_range_signature": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_session():
    st.session_state.active = False
    st.session_state.finished = False
    st.session_state.current_question = None
    st.session_state.previous_question = None
    st.session_state.feedback = None
    st.session_state.feedback_answer = None
    st.session_state.feedback_correct = None
    st.session_state.correct = 0
    st.session_state.wrong = 0
    st.session_state.history = []
    st.session_state.question_number = 0
    st.session_state.range_signature = None
    st.session_state.awaiting_continue = False
    st.session_state.feedback_question = None
    st.session_state.feedback_user_answer = None

def make_question(section):
    if section == "Tables Practice":
        low = int(st.session_state.from_table)
        high = int(st.session_state.to_table)

        # Both numbers stay within the selected range.
        first = random.randint(low, high)
        second = random.randint(low, high)

        return {"display": f"{first} × {second}", "answer": first * second,
                "left": first, "right": second}

    if section == "Squares Practice":
        low = int(st.session_state.square_min)
        high = int(st.session_state.square_max)
        n = random.randint(low, high)
        return {"display": f"{n}²", "answer": n * n, "left": n, "right": n}

    low = int(st.session_state.cube_min)
    high = int(st.session_state.cube_max)
    n = random.randint(low, high)
    return {"display": f"{n}³", "answer": n ** 3, "left": n, "right": n}

def next_question():
    new_question = make_question(st.session_state.section)
    # Avoid showing the exact same question twice in a row.
    attempts = 0
    while (
        st.session_state.previous_question is not None
        and new_question["display"] == st.session_state.previous_question
        and attempts < 20
    ):
        new_question = make_question(st.session_state.section)
        attempts += 1
    st.session_state.previous_question = new_question["display"]
    st.session_state.current_question = new_question
    st.session_state.question_number += 1
    st.session_state.feedback = None
    st.session_state.feedback_answer = None
    st.session_state.feedback_correct = None

def start_practice():
    reset_session()
    st.session_state.active = True
    st.session_state.finished = False
    st.session_state.range_signature = get_range_signature()
    next_question()

def get_range_signature():
    section = st.session_state.section
    if section == "Tables Practice":
        return (section, st.session_state.from_table, st.session_state.to_table)
    if section == "Squares Practice":
        return (section, st.session_state.square_min, st.session_state.square_max)
    return (section, st.session_state.cube_min, st.session_state.cube_max)

def submit_answer():
    question = st.session_state.current_question
    raw = st.session_state.get("answer_input", "")
    try:
        user_answer = int(str(raw).strip())
    except (TypeError, ValueError):
        st.session_state.feedback = "Please enter a whole number."
        st.session_state.feedback_correct = None
        st.session_state.feedback_answer = None
        return

    is_correct = user_answer == question["answer"]
    st.session_state.history.append({
        "question": question["display"],
        "your_answer": user_answer,
        "correct_answer": question["answer"],
        "result": "Correct" if is_correct else "Wrong",
    })
    if is_correct:
        st.session_state.correct += 1
        # Correct answer: move straight to a new random question.
        next_question()
    else:
        st.session_state.wrong += 1
        # Keep the same question visible while showing the correct answer.
        st.session_state.feedback = "wrong"
        st.session_state.feedback_answer = question["answer"]
        st.session_state.feedback_correct = False
        st.session_state.feedback_question = question["display"]
        st.session_state.feedback_user_answer = user_answer
        st.session_state.awaiting_continue = True
    # The answer form uses clear_on_submit=True, so Streamlit clears the input.

def continue_after_wrong():
    st.session_state.awaiting_continue = False
    next_question()

init_state()

# -----------------------------
# Sidebar navigation
# -----------------------------
with st.sidebar:
    st.markdown("## 🧠 Math Practice")
    st.caption("Choose what you want to practise.")
    section = st.radio(
        "Practice sections",
        ["Tables Practice", "Squares Practice", "Cubes Practice"],
        index=["Tables Practice", "Squares Practice", "Cubes Practice"].index(st.session_state.section),
        label_visibility="collapsed",
    )
    if section != st.session_state.section:
        st.session_state.section = section
        reset_session()
        st.rerun()

    st.divider()
    if st.session_state.section == "Tables Practice":
        st.markdown("### Multiplication range")
        with st.form("tables_range_form"):
            st.number_input("From table", min_value=1, max_value=100, step=1, key="from_table")
            st.number_input("To table", min_value=1, max_value=100, step=1, key="to_table")
            apply_range = st.form_submit_button("Apply Range", use_container_width=True)
        st.caption("Both numbers are randomly selected within your chosen table range.")
        valid_range = st.session_state.from_table <= st.session_state.to_table
        if apply_range:
            if valid_range:
                reset_session()
                st.session_state.applied_range_signature = get_range_signature()
                st.success(f"Applied: Tables {st.session_state.from_table}–{st.session_state.to_table}")
            else:
                st.error("The starting table must be less than or equal to the ending table.")
    elif st.session_state.section == "Squares Practice":
        st.markdown("### Number range")
        with st.form("squares_range_form"):
            st.number_input("From number", min_value=1, max_value=500, step=1, key="square_min")
            st.number_input("To number", min_value=1, max_value=500, step=1, key="square_max")
            apply_range = st.form_submit_button("Apply Range", use_container_width=True)
        valid_range = st.session_state.square_min <= st.session_state.square_max
        if apply_range:
            if valid_range:
                reset_session()
                st.session_state.applied_range_signature = get_range_signature()
                st.success(f"Applied: Numbers {st.session_state.square_min}–{st.session_state.square_max}")
            else:
                st.error("The starting number must be less than or equal to the ending number.")
    else:
        st.markdown("### Number range")
        with st.form("cubes_range_form"):
            st.number_input("From number", min_value=1, max_value=100, step=1, key="cube_min")
            st.number_input("To number", min_value=1, max_value=100, step=1, key="cube_max")
            apply_range = st.form_submit_button("Apply Range", use_container_width=True)
        valid_range = st.session_state.cube_min <= st.session_state.cube_max
        if apply_range:
            if valid_range:
                reset_session()
                st.session_state.applied_range_signature = get_range_signature()
                st.success(f"Applied: Numbers {st.session_state.cube_min}–{st.session_state.cube_max}")
            else:
                st.error("The starting number must be less than or equal to the ending number.")

    st.divider()
    st.caption("Tip: answer using your keyboard and press Enter.")

# -----------------------------
# Main screen
# -----------------------------
section_titles = {
    "Tables Practice": ("✖️ Tables Practice", "Build multiplication speed with unpredictable questions."),
    "Squares Practice": ("² Squares Practice", "Recall square numbers quickly, without a fixed sequence."),
    "Cubes Practice": ("³ Cubes Practice", "Practise cube numbers through random recall."),
}
title, subtitle = section_titles[st.session_state.section]
st.markdown(
    f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>',
    unsafe_allow_html=True,
)

if st.session_state.section == "Tables Practice":
    range_text = f"Tables {st.session_state.from_table}–{st.session_state.to_table}"
elif st.session_state.section == "Squares Practice":
    range_text = f"Numbers {st.session_state.square_min}–{st.session_state.square_max}"
else:
    range_text = f"Numbers {st.session_state.cube_min}–{st.session_state.cube_max}"

st.markdown(f'<p class="subtle">{range_text}</p>', unsafe_allow_html=True)

if not valid_range:
    st.error("The starting number must be less than or equal to the ending number.")
    st.stop()

# Keep the range fixed during a session. If changed, ask to restart.
current_signature = get_range_signature()
if st.session_state.active and st.session_state.range_signature != current_signature:
    st.warning("You changed the range. Stop or restart the practice to apply the new range.")
    if st.button("Restart with new range", use_container_width=True):
        start_practice()
        st.rerun()

if not st.session_state.active and not st.session_state.finished:
    st.write("")
    st.write("")
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        if st.button("▶ Start Practice", type="primary", use_container_width=True):
            start_practice()
            st.rerun()
    st.markdown('<p class="subtle">Your questions will be random. No fixed order.</p>', unsafe_allow_html=True)

elif st.session_state.active:
    total = st.session_state.correct + st.session_state.wrong
    accuracy = round((st.session_state.correct / total) * 100, 1) if total else 0
    m1, m2, m3 = st.columns(3)
    m1.metric("Attempted", total)
    m2.metric("Correct", st.session_state.correct)
    m3.metric("Accuracy", f"{accuracy}%")

    question = st.session_state.current_question
    st.markdown(
        f"""
        <div class="question-card">
          <div class="question-label">QUESTION {st.session_state.question_number}</div>
          <div class="question">{question['display']} = ?</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.get("awaiting_continue", False):
        st.error(
            f"Not quite! Your answer: **{st.session_state.get('feedback_user_answer')}**. "
            f"Correct answer: **{st.session_state.get('feedback_answer')}**."
        )
        if st.button("Next Question →", type="primary", use_container_width=True):
            continue_after_wrong()
            st.rerun()
    else:
        with st.form("answer_form", clear_on_submit=True):
            st.text_input(
                "Your answer",
                key="answer_input",
                placeholder="Type your answer and press Enter",
                label_visibility="collapsed",
                autocomplete="off",
            )
            st.form_submit_button("Submit ↵", type="primary", use_container_width=True, on_click=submit_answer)

    st.write("")
    if st.button("■ Stop Practice", use_container_width=True):
        st.session_state.active = False
        st.session_state.finished = True
        st.session_state.awaiting_continue = False
        st.rerun()

elif st.session_state.finished:
    total = st.session_state.correct + st.session_state.wrong
    accuracy = round((st.session_state.correct / total) * 100, 1) if total else 0
    st.markdown("## 🎉 Practice complete")
    st.markdown("Here is your session summary.")
    a, b, c = st.columns(3)
    a.metric("Attempted", total)
    b.metric("Correct", st.session_state.correct)
    c.metric("Wrong", st.session_state.wrong)
    st.progress(accuracy / 100 if total else 0)
    st.caption(f"Accuracy: {accuracy}%")

    if st.session_state.history:
        with st.expander("Review your answers", expanded=True):
            for i, item in enumerate(reversed(st.session_state.history), start=1):
                if item["result"] == "Correct":
                    st.markdown(f"✅ **{item['question']}** — Your answer: {item['your_answer']}")
                else:
                    st.markdown(
                        f"❌ **{item['question']}** — Your answer: {item['your_answer']} · "
                        f"Correct answer: **{item['correct_answer']}**"
                    )

    if st.button("Practice Again", type="primary", use_container_width=True):
        start_practice()
        st.rerun()

# Initialize state used by answer flow after init.
if "awaiting_continue" not in st.session_state:
    st.session_state.awaiting_continue = False
if "feedback_question" not in st.session_state:
    st.session_state.feedback_question = None
if "feedback_user_answer" not in st.session_state:
    st.session_state.feedback_user_answer = None
