# -*_ coding: utf-8 -*-
import pygame
import random
import sympy as sp
import operator
import emoji

pygame.init()
x = sp.Symbol('x')

# Screen setup
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🧠Math Master Challenge - Multiple Choice Edition")

# Colors
WHITE = (250, 250, 250)
BLACK = (30, 30, 30)
BLUE = (70, 130, 180)
GREEN = (0, 180, 0)
RED = (200, 50, 50)
GRAY = (210, 210, 210)
LIGHT_BLUE = (100, 170, 230)

# Fonts
TITLE_FONT = pygame.font.SysFont("Arial", 50, bold=True)
TEXT_FONT = pygame.font.SysFont("Arial", 30)
SMALL_FONT = pygame.font.SysFont("Arial", 24)

clock = pygame.time.Clock()

operators = {
    operator.add: '+',
    operator.sub: '-',
    operator.mul: '*',
    operator.truediv: '/'
}


def format_answer(ans):
    if isinstance(ans, list):
        return "[" + ", ".join(str(round(float(a), 2)) for a in ans) + "]"
    elif isinstance(ans, (int, float)):
        return str(round(ans, 2))
    else:
        return str(sp.simplify(ans))


def generate_problem(level):
    if level == 1:
        num1, num2 = random.randint(1, 20), random.randint(1, 20)
        op = random.choice(list(operators.keys()))
        problem = f"{num1} {operators[op]} {num2}"
        answer = round(op(num1, num2), 2)

    elif level == 2:
        num = random.randint(2, 10)
        p_type = random.choice(["square", "cube", "sqrt"])
        if p_type == "square":
            problem = f"{num}² = ?"
            answer = num ** 2
        elif p_type == "cube":
            problem = f"{num}³ = ?"
            answer = num ** 3
        else:
            problem = f"√{num ** 2} = ?"
            answer = abs(num)

    elif level == 3:
        a, b, c = random.randint(1, 5), random.randint(-10, 10), random.randint(-10, 10)
        problem = f"Find roots of {a}x² + {b}x + {c} = 0"
        roots = sp.solve(a * x ** 2 + b * x + c, x)
        roots = [round(float(r), 2) for r in roots]
        answer = roots

    elif level == 4:
        expr = random.choice([x ** 2, x ** 3 + 2 * x, sp.sin(x), sp.exp(x)])
        calc_type = random.choice(["diff", "integrate", "limit"])
        if calc_type == "diff":
            problem = f"d/dx({sp.pretty(expr)}) = ?"
            answer = sp.diff(expr, x)
        elif calc_type == "integrate":
            problem = f"∫ {sp.pretty(expr)} dx = ?"
            answer = sp.integrate(expr, x)
        else:
            problem = f"lim (x→0) {sp.pretty(expr)} = ?"
            answer = sp.limit(expr, x, 0)

    else:  # Level 5
        expr = random.choice([sp.sin(x), sp.cos(x), sp.tan(x), sp.log(x), sp.exp(x)])
        val = random.choice([0, sp.pi / 6, sp.pi / 4, sp.pi / 3, sp.pi / 2])
        problem = f"{sp.pretty(expr)} at x = {val}"
        answer = expr.subs(x, val).evalf()

    return problem, answer


def generate_choices(correct_answer, level):
    choices = [correct_answer]
    if level == 3 and isinstance(correct_answer, list):
        for _ in range(3):
            fake_roots = [r + random.choice([-2, -1, 1, 2]) for r in correct_answer]
            choices.append(fake_roots)
    elif level == 4:
        for _ in range(3):
            try:
                wrong = correct_answer + random.choice([x, -x, 2, -2])
                choices.append(wrong)
            except Exception:
                choices.append(correct_answer)
    elif level == 5:
        if isinstance(correct_answer, (int, float, sp.Float)):
            for _ in range(3):
                wrong = float(correct_answer) + random.choice([-1, -0.5, 0.5, 1])
                choices.append(wrong)
        else:
            for _ in range(3):
                choices.append(correct_answer)
    else:
        for _ in range(3):
            if isinstance(correct_answer, (int, float)):
                wrong = round(correct_answer + random.choice([-3, -2, -1, 1, 2, 3]), 2)
            else:
                wrong = correct_answer
            choices.append(wrong)

    random.shuffle(choices)
    letters = ["A", "B", "C", "D"]
    return dict(zip(letters, [format_answer(c) for c in choices]))


def compare_answers(user_choice, correct_answer):
    try:
        if isinstance(correct_answer, list):
            user_list = [float(x) for x in user_choice.strip("[]").split(",")]
            return sorted([round(a, 2) for a in user_list]) == sorted([round(a, 2) for a in correct_answer])
        elif abs(float(user_choice) - float(correct_answer)) < 0.01:
            return True
    except:
        if str(sp.simplify(user_choice)) == str(sp.simplify(correct_answer)):
            return True
    return False


def draw_restart_button():
    button_rect = pygame.Rect(WIDTH/2 - 100, HEIGHT/2 + 100, 200, 60)
    pygame.draw.rect(screen, LIGHT_BLUE, button_rect, border_radius=10)
    text = TEXT_FONT.render("♻️ Restart", True, WHITE)
    screen.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 + 110))
    return button_rect


def main():
    running = True
    level = 1
    problem, answer = generate_problem(level)
    choices = generate_choices(answer, level)
    score = 0
    total = 0
    feedback = ''
    color = BLACK
    show_feedback = False
    feedback_timer = 0
    wrong_count = 0
    game_over = False
    celebrating = False
    celebrate_start_time = 0

    while running:
        screen.fill(WHITE)
        title = TITLE_FONT.render("Math master Challenge", True, BLUE)
        screen.blit(title, (WIDTH / 2 - title.get_width() / 2, 40))

        # 🎉 Celebration screen
        if celebrating:
            elapsed = pygame.time.get_ticks() - celebrate_start_time
            text = TITLE_FONT.render("Great Job!", True, GREEN)
            screen.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 - 50))
            pygame.display.flip()

            if elapsed > 6000:  # 6 seconds celebration
                celebrating = False
                problem, answer = generate_problem(level)
                choices = generate_choices(answer, level)
                feedback = ''
                show_feedback = False
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                continue  # Skip rest of loop

        elif not game_over:
            level_text = SMALL_FONT.render(f"Press 1–5 to change level | Level: {level}", True, BLACK)
            screen.blit(level_text, (50, 130))

            problem_text = TEXT_FONT.render(f"Q{total + 1}: {problem}", True, BLACK)
            screen.blit(problem_text, (50, 200))

            # Draw choices
            y = 280
            for letter, choice in choices.items():
                pygame.draw.rect(screen, GRAY, (50, y - 5, 700, 45), border_radius=8)
                choice_text = TEXT_FONT.render(f"{letter}) {choice}", True, BLACK)
                screen.blit(choice_text, (70, y))
                y += 60

            # Feedback
            if show_feedback:
                feedback_text = TEXT_FONT.render(feedback, True, color)
                screen.blit(feedback_text, (50, 550))

            score_text = SMALL_FONT.render(f"Score: {score}/{total}", True, BLUE)
            screen.blit(score_text, (50, 620))

            wrong_text = SMALL_FONT.render(f" Wrong attempts: {wrong_count}/3", True, RED)
            screen.blit(wrong_text, (300, 620))

            inst_text = SMALL_FONT.render("Press A–D to answer | ESC to quit", True, BLACK)
            screen.blit(inst_text, (600, 620))

        else:
            game_over_text = TITLE_FONT.render(" Level Failed!", True, RED)
            screen.blit(game_over_text, (WIDTH / 2 - game_over_text.get_width() / 2, HEIGHT / 2 - 50))
            restart_button = draw_restart_button()

        pygame.display.flip()

        # Auto-next question after feedback
        if show_feedback and pygame.time.get_ticks() - feedback_timer > 1500 and not game_over:
            problem, answer = generate_problem(level)
            choices = generate_choices(answer, level)
            feedback = ''
            show_feedback = False

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif not game_over and event.unicode.upper() in ["A", "B", "C", "D"]:
                    total += 1
                    chosen = choices[event.unicode.upper()]
                    is_correct = compare_answers(chosen, answer)

                    if is_correct:
                        score += 1
                        feedback, color = " Correct!", GREEN
                        if score % 5 == 0:  # 🎉 Every 5 correct answers
                            celebrating = True
                            celebrate_start_time = pygame.time.get_ticks()
                    else:
                        wrong_count += 1
                        feedback, color = f" Wrong! Correct: {format_answer(answer)}", RED
                        if wrong_count >= 3:
                            game_over = True

                    show_feedback = True
                    feedback_timer = pygame.time.get_ticks()

                elif not game_over and event.unicode in "12345":
                    level = int(event.unicode)
                    problem, answer = generate_problem(level)
                    choices = generate_choices(answer, level)
                    feedback = ''
                    show_feedback = False
                    wrong_count = 0
                    score = 0
                    total = 0

            elif event.type == pygame.MOUSEBUTTONDOWN and game_over:
                mouse_pos = pygame.mouse.get_pos()
                if draw_restart_button().collidepoint(mouse_pos):
                    # Restart entire game
                    level = 1
                    score = 0
                    total = 0
                    wrong_count = 0
                    feedback = ''
                    game_over = False
                    problem, answer = generate_problem(level)
                    choices = generate_choices(answer, level)

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()