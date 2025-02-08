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
DARK_RED = (150, 0, 0)
DARK_BLUE = (0, 0, 150)
GRAY = (100, 100, 100)

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


# Här använder vi en blå gradientbakgrund (mörkblå högst upp, ljusare blå längst ner)
background = create_gradient_surface(SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 128), (0, 0, 255))


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
            # Doldt kort (t.ex. dealerens första kort)
            pygame.draw.rect(surface, DARK_BLUE, (x, y, CARD_WIDTH, CARD_HEIGHT))
            pygame.draw.rect(surface, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)
            font = pygame.font.Font(None, 48)
            text = font.render("?", True, WHITE)
            text_rect = text.get_rect(center=(x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2))
            surface.blit(text, text_rect)
        else:
            # Rita kortets bakgrund
            pygame.draw.rect(surface, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT))
            pygame.draw.rect(surface, BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)
            font = pygame.font.Font(None, 24)
            text = font.render(f"{self.rank}{self.suit}", True, BLACK)
            surface.blit(text, (x + 5, y + 5))
            # Rita kortets "spegel" i nedre högra hörnet
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
            self.__init__()  # Om kortleken tar slut – återställ
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
        # Justera för ess
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
        if self.rect.collidepoint(mouse_pos):
            current_color = self.hover_color
        else:
            current_color = self.base_color
        pygame.draw.rect(surface, current_color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# ------------------------------
# Lån Mini-Game
# ------------------------------
def loan_mini_game():
    """
    Ett mini-game där spelaren måste trycka på mellanslag upprepade gånger för att
    fylla en progressbar innan tiden tar slut (10 sekunder). Om progressbarens
    värde når tröskeln lyckas du och får ett lån (ditt saldo återställs),
    annars är det game over.
    """
    start_time = pygame.time.get_ticks()
    time_limit = 10000  # 10 sekunder
    progress = 0
    required_progress = 100  # Målet
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
                    progress += 5  # Varje tryck ökar progressen

        # Rita mini-game skärmen
        screen.blit(background, (0, 0))
        draw_center_text(screen, "LÅN MINI-GAME", 48, WHITE, 50)
        draw_center_text(screen, "Tryck på mellanslag snabbt!", 32, WHITE, 100)
        timer_text = font.render(f"Resterande tid: {remaining // 1000}.{(remaining % 1000) // 100}s", True, WHITE)
        screen.blit(timer_text, (SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 150))

        # Rita progressbar
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
            return True  # Lyckades

    return False  # Misslyckades


# ------------------------------
# Skärmar och feedback
# ------------------------------
def betting_screen(current_money):
    """
    Satsningsskärm: spelaren kan använda både knappar och tangentbordsinmatning
    för att specificera insatsbeloppet.
    Nu är alla element omplacerade så att de inte stör (ex. inte ligger över korten).
    """
    bet_str = ""  # Stränginmatning från tangentbordet
    bet = 0
    # Placera elementen högst upp
    title_y = 100
    balance_y = 150
    input_box_y = 220
    buttons_y = 290
    confirm_y = 360
    instruction_y = 430

    input_box = pygame.Rect(SCREEN_WIDTH // 2 - 100, input_box_y, 200, 40)
    dec_button = Button((SCREEN_WIDTH // 2 - 220, buttons_y, 100, 50), DARK_RED, "Minska")
    inc_button = Button((SCREEN_WIDTH // 2 + 120, buttons_y, 100, 50), DARK_RED, "Öka")
    confirm_button = Button((SCREEN_WIDTH // 2 - 50, confirm_y, 100, 50), DARK_RED, "Satsa")

    selecting = True
    while selecting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            # Tangentbordsinmatning
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
            # Musinput via knappar
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
        pygame.display.flip()
    return bet


def round_summary_screen(player_hand, dealer_hand, outcome):
    """
    Visar en sammanfattningsskärm med båda handarnas värden innan det
    slutgiltiga resultatet avslöjas.
    """
    continue_button = Button((SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 100, 100, 50), DARK_RED, "Fortsätt")
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
        draw_text(screen, f"Din poäng: {player_hand.get_value()}", 32, WHITE, (100, SCREEN_HEIGHT - 240))
        dealer_hand.draw(screen, 100, 100, hide_first=False)
        draw_text(screen, f"Dealerns poäng: {dealer_hand.get_value()}", 32, WHITE, (100, 60))
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
    """Visar en tydlig Game Over-skiss med information."""
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

    # Dela ut två kort vardera
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
                        outcome = "Du fick för mycket! Du förlorade."
                        player_turn = False
                        round_active = False
                elif stand_button_rect.collidepoint(pos):
                    player_turn = False

        if not player_turn and round_active:
            while dealer_hand.get_value() < 17:
                pygame.time.delay(500)
                dealer_hand.add_card(deck.deal_card())
            player_val = player_hand.get_value()
            dealer_val = dealer_hand.get_value()
            if player_val > 21:
                outcome = "Du fick för mycket! Du förlorade."
            elif dealer_val > 21:
                outcome = "Dealern fick för mycket! Du vann!"
            elif dealer_val > player_val:
                outcome = "Dealern vann!"
            elif dealer_val < player_val:
                outcome = "Du vann!"
            else:
                outcome = "Oavgjort!"
            round_active = False

        screen.blit(background, (0, 0))
        draw_center_text(screen, "Dealerns hand", 36, WHITE, 50)
        draw_center_text(screen, "Din hand", 36, WHITE, SCREEN_HEIGHT - 200)
        dealer_hand.draw(screen, 100, 100, hide_first=player_turn)
        player_hand.draw(screen, 100, SCREEN_HEIGHT - 200, hide_first=False)
        font = pygame.font.Font(None, 28)
        draw_text(screen, f"Värde: {player_hand.get_value()}", 28, WHITE, (100, SCREEN_HEIGHT - 240))
        if not player_turn:
            draw_text(screen, f"Värde: {dealer_hand.get_value()}", 28, WHITE, (100, 60))
        if player_turn:
            hit_button = Button((100, SCREEN_HEIGHT - 100, 150, 50), DARK_RED, "Ta kort")
            stand_button = Button((300, SCREEN_HEIGHT - 100, 150, 50), DARK_RED, "Stanna")
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
    global player_money
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
        draw_center_text(screen, "Välkommen till Avancerat Blackjack!", 64, WHITE, SCREEN_HEIGHT // 2 - 50)
        draw_center_text(screen, "Tryck på en tangent för att starta", 36, WHITE, SCREEN_HEIGHT // 2 + 20)
        pygame.display.flip()

    playing = True
    while playing:
        bet = betting_screen(player_money)
        outcome = game_round(bet)
        if outcome in ["Du fick för mycket! Du förlorade.", "Dealern vann!"]:
            player_money -= bet
        elif outcome in ["Dealern fick för mycket! Du vann!", "Du vann!"]:
            player_money += bet

        # Om spelarens saldo understiger noll triggas lån-mini-gameet
        if player_money <= 0:
            loan_success = loan_mini_game()
            if loan_success:
                player_money = 500  # Lånebelopp
            else:
                game_over_screen()
                playing = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
