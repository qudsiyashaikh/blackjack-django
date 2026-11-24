import random
import sys
from django.conf import settings
from django.core.management import execute_from_command_line
from django.http import HttpResponse
from django.template import Context, Template
from django.urls import path

settings.configure(
    DEBUG=True,
    ROOT_URLCONF=__name__,
    SECRET_KEY="super-secret-key-for-blackjack-game",
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "APP_DIRS": True,
        }
    ],
)

CARDS = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]


def draw_card():
    return random.choice(CARDS)


def calculate_score(cards):
    score = sum(cards)
    if score == 21 and len(cards) == 2:
        return 0  # Blackjack
    while 11 in cards and score > 21:
        cards[cards.index(11)] = 1
        score = sum(cards)
    return score


def serialize_cards(cards):
    return ",".join(str(c) for c in cards)


def parse_cards(raw):
    if not raw:
        return []
    return [int(x) for x in raw.split(",") if x.strip()]


def blackjack_view(request):
    game_over = False
    message = ""
    result_type = "info"

    if request.method == "POST":
        action = request.POST.get("action", "new")
        user_cards = parse_cards(request.POST.get("user_cards", ""))
        dealer_cards = parse_cards(request.POST.get("dealer_cards", ""))

        if action == "new" or not user_cards or not dealer_cards:
            user_cards = [draw_card(), draw_card()]
            dealer_cards = [draw_card(), draw_card()]
            user_score = calculate_score(user_cards)
            dealer_score = calculate_score(dealer_cards)
            if user_score == 0 or dealer_score == 0 or user_score > 21:
                game_over = True
                message, result_type = get_outcome(user_cards, dealer_cards)
            else:
                message = "Your turn! Choose Hit to draw a card or Stand to end your turn."
        elif action == "hit":
            user_cards.append(draw_card())
            user_score = calculate_score(user_cards)
            if user_score == 0 or user_score > 21:
                game_over = True
                message, result_type = get_outcome(user_cards, dealer_cards)
            else:
                message = "You drew a card. Hit again or Stand?"
        elif action == "stand":
            while calculate_score(dealer_cards) != 0 and calculate_score(dealer_cards) < 17:
                dealer_cards.append(draw_card())
            game_over = True
            message, result_type = get_outcome(user_cards, dealer_cards)
    else:
        user_cards = [draw_card(), draw_card()]
        dealer_cards = [draw_card(), draw_card()]
        user_score = calculate_score(user_cards)
        dealer_score = calculate_score(dealer_cards)
        if user_score == 0 or dealer_score == 0 or user_score > 21:
            game_over = True
            message, result_type = get_outcome(user_cards, dealer_cards)
        else:
            message = "Your turn! Choose Hit to draw a card or Stand to end your turn."

    user_score = calculate_score(user_cards)
    dealer_score = calculate_score(dealer_cards)

    display_user_score = 21 if user_score == 0 else user_score
    if game_over:
        display_dealer_score = 21 if dealer_score == 0 else dealer_score
        dealer_display_cards = dealer_cards
    else:
        display_dealer_score = dealer_cards[0] if dealer_cards else 0
        dealer_display_cards = [dealer_cards[0], "?"] if len(dealer_cards) >= 2 else dealer_cards

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Blackjack - Django</title>
        <style>
            body { font-family: Arial, sans-serif; background: #0f291e; color: #fff; text-align: center; margin-top: 50px; }
            .table { display: inline-block; background: #163b2b; padding: 35px; border-radius: 16px; box-shadow: 0 8px 28px rgba(0,0,0,0.4); width: 460px; border: 2px solid #256347; }
            h2 { margin-top: 0; color: #a7f3d0; }
            .hand { background: rgba(0,0,0,0.22); padding: 15px; border-radius: 10px; margin: 16px 0; }
            .cards { font-size: 22px; font-weight: bold; letter-spacing: 6px; margin: 8px 0; color: #fef08a; }
            .btn { padding: 12px 22px; font-size: 16px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; margin: 6px; }
            .btn-hit { background: #10b981; color: #052e16; }
            .btn-hit:hover { background: #34d399; }
            .btn-stand { background: #f59e0b; color: #1c1917; }
            .btn-stand:hover { background: #fbbf24; }
            .btn-new { background: #38bdf8; color: #082f49; }
            .btn-new:hover { background: #7dd3fc; }
            .msg { margin-top: 18px; padding: 14px; border-radius: 8px; font-size: 17px; font-weight: bold; }
            .info { background: rgba(56, 189, 248, 0.2); color: #bae6fd; }
            .win { background: rgba(16, 185, 129, 0.28); color: #a7f3d0; }
            .lose { background: rgba(239, 68, 68, 0.28); color: #fecaca; }
            .draw { background: rgba(245, 158, 11, 0.28); color: #fde68a; }
        </style>
    </head>
    <body>
        <div class="table">
            <h2>🃏  Blackjack</h2>

            <div class="hand">
                <div>Dealer Cards (Score: {{ display_dealer_score }})</div>
                <div class="cards">
                    {% for c in dealer_display_cards %}[{{ c }}] {% endfor %}
                </div>
            </div>

            <div class="hand">
                <div>Your Cards (Score: {{ display_user_score }})</div>
                <div class="cards">
                    {% for c in user_cards %}[{{ c }}] {% endfor %}
                </div>
            </div>

            <form method="POST">
                {% csrf_token %}
                <input type="hidden" name="user_cards" value="{{ user_cards_str }}">
                <input type="hidden" name="dealer_cards" value="{{ dealer_cards_str }}">

                {% if not game_over %}
                    <button type="submit" name="action" value="hit" class="btn btn-hit">Hit (+ Card)</button>
                    <button type="submit" name="action" value="stand" class="btn btn-stand">Stand</button>
                {% else %}
                    <button type="submit" name="action" value="new" class="btn btn-new">Play Again</button>
                {% endif %}
            </form>

            <div class="msg {{ result_type }}">{{ message }}</div>
        </div>
    </body>
    </html>
    """
    t = Template(html_content)
    c = Context({
        "user_cards": user_cards,
        "dealer_display_cards": dealer_display_cards,
        "display_user_score": display_user_score,
        "display_dealer_score": display_dealer_score,
        "user_cards_str": serialize_cards(user_cards),
        "dealer_cards_str": serialize_cards(dealer_cards),
        "game_over": game_over,
        "message": message,
        "result_type": result_type,
        "request": request,
    })
    return HttpResponse(t.render(c))


def get_outcome(user_cards, dealer_cards):
    user_score = calculate_score(user_cards)
    dealer_score = calculate_score(dealer_cards)

    if dealer_score == 0:
        return "Dealer has Blackjack! You lose.", "lose"
    if user_score == 0:
        return "Blackjack! You win!", "win"
    if user_score > 21:
        return "Bust! You went over 21. You lose.", "lose"
    if dealer_score > 21:
        return "Dealer went over 21! You win!", "win"
    if user_score == dealer_score:
        return "It's a draw!", "draw"
    if user_score > dealer_score:
        return "You win!", "win"
    return "You lose!", "lose"


urlpatterns = [
    path("", blackjack_view),
]

if __name__ == "__main__":
    execute_from_command_line([sys.argv[0], "runserver"])