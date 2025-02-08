import pygame
import random
import sys

# ------------------------------
# Initiering och globala inställningar
# ------------------------------
pygame.init()
pygame.font.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30

# Färger
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 100, 0)
LIGHT_GREEN = (0, 150, 0)
DARK_GREEN = (0, 50, 0)
DARK_BLUE = (0, 0, 150)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)  # Gul – för knappar
DARK_RED = (150, 0, 0)  # Lägger till DARK_RED för mini-game

# Kortstorlek
CARD_WIDTH = 80
CARD_HEIGHT = 120

# Skärm, klocka och global variabel för spelarens pengar
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Avancerat Blackjack")
clock = pygame.time.Clock()
player_money = 1000

# Standardfont
DEFAULT_FONT = pygame.font.Font(None, 36)


# ------------------------------
# Hjälpfunktioner för rendering
# ------------------------------
def draw_center_text(surface, text, size, color, y):
    font = pygame.font.Font(None, size)
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y))
    surface.blit(text_surf, text_rect)


def draw_text(surface, text, size, color, pos):
    font = pygame.font.Font(None, size)
    text_surf = font.render(text, True, color)
    surface.blit(text_surf, pos)


def create_gradient_surface(width, height, top_color, bottom_color):
    """Skapar en vertikal gradient som bakgrund."""
    gradient = pygame.Surface((width, height))
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(gradient, (r, g, b), (0, y), (width, y))
    return gradient


# Bakgrund med blå gradient (mörkblå högst upp, ljusare blå längst ner)
background = create_gradient_surface(SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 128), (0, 0, 255))


# ------------------------------
# Inloggningsskärm
# ------------------------------
def login_screen():
    """
    Visar en inloggningsskärm där spelaren anger sitt namn.
    När ett giltigt namn är angivet väljs ett slumpmässigt motståndarnamn.
    Returnerar (player_name, opponent_name).
    """
    input_str = ""
    input_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 20, 300, 40)
    prompt = "Ange ditt namn:"
    login_done = False
    while not login_done:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    input_str = input_str[:-1]
                elif event.key == pygame.K_RETURN:
                    if input_str.strip() != "":
                        login_done = True
                else:
                    input_str += event.unicode
        screen.blit(background, (0, 0))
        draw_center_text(screen, "Logga in", 64, WHITE, SCREEN_HEIGHT // 2 - 100)
        draw_center_text(screen, prompt, 36, WHITE, SCREEN_HEIGHT // 2 - 40)
        pygame.draw.rect(screen, WHITE, input_box, 2)
        input_surf = DEFAULT_FONT.render(input_str, True, WHITE)
        screen.blit(input_surf, (input_box.x + 10, input_box.y + 5))
        draw_center_text(screen, "Tryck Enter när du är klar", 28, WHITE, SCREEN_HEIGHT // 2 + 60)
        pygame.display.flip()
    opponent_list = ["Björn", "Kalle", "Mats", "Sven", "Anders"]
    opponent_name = random.choice(opponent_list)
    return input_str.strip(), opponent_name


# ------------------------------
# Klasser för kortspel
# ------------------------------
class Card:
    def __init__(self, suit, rank):
        self.suit = suit  # Ex: '♥', '♦', '♣', '♠'
        self.rank = rank  # Ex: 'A', '2', ... '10', 'J', 'Q', 'K'

    def get_value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        else:
            return int(self.rank)

    def draw(self, surface, x, y, hidden=False):
        if hidden:
            pygame.draw.rect(surface, DARK_BLUE, (x, y, CARD_WIDTH, CARD_HEIGHT))
            pygame.draw.rect(surface, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)
            font = pygame.font.Font(None, 48)
            text = font.render("?", True, WHITE)
            text_rect = text.get_rect(center=(x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2))
            surface.blit(text, text_rect)
        else:
            pygame.draw.rect(surface, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT))
            pygame.draw.rect(surface, BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)
            font = pygame.font.Font(None, 24)
            text = font.render(f"{self.rank}{self.suit}", True, BLACK)
            surface.blit(text, (x + 5, y + 5))
            text_small = font.render(f"{self.rank}{self.suit}", True, BLACK)
            text_small = pygame.transform.rotate(text_small, 180)
            surface.blit(text_small, (x + CARD_WIDTH - text_small.get_width() - 5,
                                      y + CARD_HEIGHT - text_small.get_height() - 5))


class Deck:
    def __init__(self):
        self.cards = []
        suits = ['♥', '♦', '♣', '♠']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(suit, rank))
        random.shuffle(self.cards)

    def deal_card(self):
        if len(self.cards) == 0:
            self.__init__()
        return self.cards.pop()


class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        total = 0
        aces = 0
        for card in self.cards:
            total += card.get_value()
            if card.rank == 'A':
                aces += 1
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def draw(self, surface, x, y, hide_first=False):
        for i, card in enumerate(self.cards):
            pos_x = x + i * (CARD_WIDTH + 15)
            if i == 0 and hide_first:
                card.draw(surface, pos_x, y, hidden=True)
            else:
                card.draw(surface, pos_x, y, hidden=False)


# ------------------------------
# Enkel knapp-klass med hovereffekt
# ------------------------------
class Button:
    def __init__(self, rect, color, text, text_color=WHITE):
        self.rect = pygame.Rect(rect)
        self.base_color = color
        self.hover_color = tuple(min(255, c + 50) for c in color)
        self.text = text
        self.text_color = text_color
        self.font = pygame.font.Font(None, 36)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.base_color
        pygame.draw.rect(surface, current_color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# ------------------------------
# Dealer-turn med "mänsklig" interaktion
# ------------------------------
def dealer_turn(dealer_hand, deck):
    dealer_comments = [
        "Hmm, låt mig tänka...",
        "Jag tar ett kort till.",
        "Inte tillräckligt högt än!",
        "Nu drar jag!"
    ]
    while dealer_hand.get_value() < 17:
        comment = random.choice(dealer_comments)
        screen.blit(background, (0, 0))
        dealer_hand.draw(screen, 100, 100, hide_first=False)
        draw_center_text(screen, comment, 36, WHITE, SCREEN_HEIGHT // 2)
        pygame.display.flip()
        pygame.time.delay(1000)
        dealer_hand.add_card(deck.deal_card())
    comment = "Jag stannar nu."
    screen.blit(background, (0, 0))
    dealer_hand.draw(screen, 100, 100, hide_first=False)
    draw_center_text(screen, comment, 36, WHITE, SCREEN_HEIGHT // 2)
    pygame.display.flip()
    pygame.time.delay(1000)


# ------------------------------
# Lån Mini-Game
# ------------------------------
def loan_mini_game():
    """
    Mini-game: Tryck på mellanslag upprepade gånger under 10 sekunder för att fylla progressbaren.
    Lyckas du får du ett lån (saldo återställs), misslyckas du – game over.
    """
    start_time = pygame.time.get_ticks()
    time_limit = 10000  # 10 sekunder
    progress = 0
    required_progress = 100
    font = pygame.font.Font(None, 36)

    while True:
        dt = clock.tick(FPS)
        current_time = pygame.time.get_ticks()
        elapsed = current_time - start_time
        remaining = max(0, time_limit - elapsed)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    progress += 5
        screen.blit(background, (0, 0))
        draw_center_text(screen, "LÅN MINI-GAME", 48, WHITE, 50)
        draw_center_text(screen, "Tryck på mellanslag snabbt!", 32, WHITE, 100)
        timer_text = font.render(f"Resterande tid: {remaining // 1000}.{(remaining % 1000) // 100}s", True, WHITE)
        screen.blit(timer_text, (SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 150))
        bar_width = 400
        bar_height = 30
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = 250
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        fill_width = int((progress / required_progress) * bar_width)
        fill_width = min(fill_width, bar_width)
        pygame.draw.rect(screen, DARK_RED, (bar_x, bar_y, fill_width, bar_height))
        progress_text = font.render(f"{min(progress, required_progress)} / {required_progress}", True, WHITE)
        screen.blit(progress_text, (SCREEN_WIDTH // 2 - progress_text.get_width() // 2, bar_y + bar_height + 10))
        pygame.display.flip()
        if remaining <= 0:
            break
        if progress >= required_progress:
            return True
    return False


# ------------------------------
# Skärmar och feedback
# ------------------------------
def betting_screen(current_money):
    """
    Satsningsskärm med både knapp- och tangentbordsinmatning.
    Elementen är placerade högst upp, och spelar-/motståndarens namn visas.
    """
    bet_str = ""
    bet = 0
    title_y = 100
    balance_y = 150
    input_box_y = 220
    buttons_y = 290
    confirm_y = 360
    instruction_y = 430

    draw_text(screen, f"Spelare: {player_name}", 28, WHITE, (50, 20))
    draw_text(screen, f"Motståndare: {opponent_name}", 28, WHITE, (50, 50))

    input_box = pygame.Rect(SCREEN_WIDTH // 2 - 100, input_box_y, 200, 40)
    dec_button = Button((SCREEN_WIDTH // 2 - 220, buttons_y, 100, 50), YELLOW, "Minska", text_color=BLACK)
    inc_button = Button((SCREEN_WIDTH // 2 + 120, buttons_y, 100, 50), YELLOW, "Öka", text_color=BLACK)
    confirm_button = Button((SCREEN_WIDTH // 2 - 50, confirm_y, 100, 50), YELLOW, "Satsa", text_color=BLACK)

    selecting = True
    while selecting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    bet_str = bet_str[:-1]
                elif event.key == pygame.K_RETURN:
                    if bet > 0:
                        selecting = False
                else:
                    if event.unicode.isdigit():
                        bet_str += event.unicode
                bet = int(bet_str) if bet_str != "" else 0
                if bet > current_money:
                    bet = current_money
                    bet_str = str(bet)
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if inc_button.is_clicked(pos) and bet < current_money:
                    bet += 10
                    bet_str = str(bet)
                elif dec_button.is_clicked(pos) and bet >= 10:
                    bet = max(0, bet - 10)
                    bet_str = str(bet)
                elif confirm_button.is_clicked(pos) and bet > 0:
                    selecting = False

        screen.blit(background, (0, 0))
        draw_center_text(screen, "Satsa pengar", 48, WHITE, title_y)
        draw_center_text(screen, f"Du har: {current_money} kr", 36, WHITE, balance_y)
        pygame.draw.rect(screen, WHITE, input_box, 2)
        input_font = pygame.font.Font(None, 32)
        input_text = input_font.render(bet_str if bet_str != "" else "0", True, WHITE)
        screen.blit(input_text, (input_box.x + 10, input_box.y + 5))
        draw_center_text(screen, f"Aktuell insats: {bet} kr", 36, WHITE, confirm_y - 30)
        dec_button.draw(screen)
        inc_button.draw(screen)
        confirm_button.draw(screen)
        draw_center_text(screen, "Använd tangentbordet eller knapparna för att ange insats", 24, WHITE, instruction_y)
        draw_text(screen, f"Spelare: {player_name}", 28, WHITE, (50, 20))
        draw_text(screen, f"Motståndare: {opponent_name}", 28, WHITE, (50, 50))
        pygame.display.flip()
    return bet


def round_summary_screen(player_hand, dealer_hand, outcome):
    """
    Visar en runda­sammanfattning med båda handarnas värden samt namn.
    """
    continue_button = Button((SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 100, 100, 50), YELLOW, "Fortsätt",
                             text_color=BLACK)
    summary_shown = True
    while summary_shown:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if continue_button.is_clicked(pygame.mouse.get_pos()):
                    summary_shown = False

        screen.blit(background, (0, 0))
        draw_center_text(screen, "Runda Sammanfattning", 48, WHITE, 50)
        player_hand.draw(screen, 100, SCREEN_HEIGHT - 200, hide_first=False)
        draw_text(screen, f"{player_name}'s poäng: {player_hand.get_value()}", 32, WHITE, (100, SCREEN_HEIGHT - 240))
        dealer_hand.draw(screen, 100, 100, hide_first=False)
        draw_text(screen, f"{opponent_name}'s poäng: {dealer_hand.get_value()}", 32, WHITE, (100, 60))
        draw_center_text(screen, "Tryck på 'Fortsätt' för att se resultatet", 28, WHITE, SCREEN_HEIGHT // 2)
        continue_button.draw(screen)
        pygame.display.flip()

    result_shown = True
    while result_shown:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                result_shown = False
        screen.blit(background, (0, 0))
        draw_center_text(screen, outcome, 64, WHITE, SCREEN_HEIGHT // 2)
        draw_center_text(screen, "Tryck på en tangent för att fortsätta", 28, WHITE, SCREEN_HEIGHT // 2 + 70)
        pygame.display.flip()


def game_over_screen():
    """Visar en tydlig Game Over-skiss."""
    over = True
    while over:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                over = False
        screen.blit(background, (0, 0))
        draw_center_text(screen, "Game Over!", 64, WHITE, SCREEN_HEIGHT // 2 - 50)
        draw_center_text(screen, "Tryck på en tangent för att avsluta", 32, WHITE, SCREEN_HEIGHT // 2 + 20)
        pygame.display.flip()


# ------------------------------
# Huvudspelets runda
# ------------------------------
def game_round(bet):
    deck = Deck()
    player_hand = Hand()
    dealer_hand = Hand()

    player_hand.add_card(deck.deal_card())
    player_hand.add_card(deck.deal_card())
    dealer_hand.add_card(deck.deal_card())
    dealer_hand.add_card(deck.deal_card())

    outcome = ""
    player_turn = True
    round_active = True

    while round_active:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and player_turn:
                pos = pygame.mouse.get_pos()
                hit_button_rect = pygame.Rect(100, SCREEN_HEIGHT - 100, 150, 50)
                stand_button_rect = pygame.Rect(300, SCREEN_HEIGHT - 100, 150, 50)
                if hit_button_rect.collidepoint(pos):
                    player_hand.add_card(deck.deal_card())
                    if player_hand.get_value() > 21:
                        outcome = f"{player_name}, du fick för mycket! Du förlorade."
                        player_turn = False
                        round_active = False
                elif stand_button_rect.collidepoint(pos):
                    player_turn = False

        if not player_turn and round_active:
            dealer_turn(dealer_hand, deck)
            player_val = player_hand.get_value()
            dealer_val = dealer_hand.get_value()
            if player_val > 21:
                outcome = f"{player_name}, du fick för mycket! Du förlorade."
            elif dealer_val > 21:
                outcome = f"{opponent_name} fick för mycket! Du vann!"
            elif dealer_val > player_val:
                outcome = f"{opponent_name} vann!"
            elif dealer_val < player_val:
                outcome = f"Du vann, {player_name}!"
            else:
                outcome = "Oavgjort!"
            round_active = False

        screen.blit(background, (0, 0))
        draw_center_text(screen, f"{opponent_name}'s hand", 36, WHITE, 50)
        draw_center_text(screen, f"{player_name}'s hand", 36, WHITE, SCREEN_HEIGHT - 200)
        dealer_hand.draw(screen, 100, 100, hide_first=player_turn)
        player_hand.draw(screen, 100, SCREEN_HEIGHT - 200, hide_first=False)
        font = pygame.font.Font(None, 28)
        draw_text(screen, f"Värde: {player_hand.get_value()}", 28, WHITE, (100, SCREEN_HEIGHT - 240))
        if not player_turn:
            draw_text(screen, f"Värde: {dealer_hand.get_value()}", 28, WHITE, (100, 60))
        if player_turn:
            hit_button = Button((100, SCREEN_HEIGHT - 100, 150, 50), YELLOW, "Ta kort", text_color=BLACK)
            stand_button = Button((300, SCREEN_HEIGHT - 100, 150, 50), YELLOW, "Stanna", text_color=BLACK)
            hit_button.draw(screen)
            stand_button.draw(screen)
        draw_text(screen, f"Pengar: {player_money} kr", 28, WHITE, (600, SCREEN_HEIGHT - 240))
        pygame.display.flip()

    round_summary_screen(player_hand, dealer_hand, outcome)
    return outcome


# ------------------------------
# Huvudloopen för spelet
# ------------------------------
def main():
    global player_money, player_name, opponent_name
    player_name, opponent_name = login_screen()

    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                waiting = False
        screen.blit(background, (0, 0))
        draw_center_text(screen, f"Välkommen, {player_name}!", 64, WHITE, SCREEN_HEIGHT // 2 - 100)
        draw_center_text(screen, f"Motståndare: {opponent_name}", 36, WHITE, SCREEN_HEIGHT // 2 - 30)
        draw_center_text(screen, "Tryck på en tangent för att starta", 36, WHITE, SCREEN_HEIGHT // 2 + 20)
        pygame.display.flip()

    playing = True
    while playing:
        bet = betting_screen(player_money)
        outcome = game_round(bet)
        if outcome in [f"{player_name}, du fick för mycket! Du förlorade.", f"{opponent_name} vann!"]:
            player_money -= bet
        elif outcome in [f"{opponent_name} fick för mycket! Du vann!", f"Du vann, {player_name}!"]:
            player_money += bet

        if player_money <= 0:
            loan_success = loan_mini_game()
            if loan_success:
                player_money = 500
            else:
                game_over_screen()
                playing = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
