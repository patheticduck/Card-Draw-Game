import pygame  # Pygame kütüphanesi oyun oluşturmak için kullanılıyor
import random
import os

pygame.init()

# Oyun ekranı boyutlarını ayarlar
WIDTH, HEIGHT = 1220, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Oyun penceresini oluşturur
pygame.display.set_caption("Kart Çekme Oyunu")  # Pencere başlığını ayarlar

# Renk tanımları (RGB formatında) ayarladık
LIGHT_GREEN = (144, 238, 144)
BLACK = (0, 0, 0)
RED = (200, 50, 50)

# Yazı tipi ayarı (varsayılan yazı tipi, boyut 36) olarak belirledik
font = pygame.font.Font(None, 36)

# Deste görselini yükler ve boyutunu ayarlaradık
deck_image = pygame.image.load(os.path.join("kartlar", "deste.png"))
deck_image = pygame.transform.scale(deck_image, (100, 150))  # Görseli uygun boyuta getir
deck_position = (WIDTH // 2 - 50, HEIGHT // 2 - 70)  # Destenin ekrandaki konumu

# Kartların arka yüz PNG'sini yükler ve boyutunu ayarlaradık
card_back_image = pygame.image.load(os.path.join("kartlar", "card_back.png"))
card_back_image = pygame.transform.scale(card_back_image, (100, 150))

# Kart görsellerini yükleyen fonksiyon
def kart_yukle():
    kart_resimleri = {}  # Kart resimlerini saklamak için bir sözlük dizin oluşturduk
    suits = ['Kupa', 'Maça', 'Karo', 'Sinek']  # Kart türleri (maça, kupa vb.)
    for suit in suits:
        for value in range(1, 14):  # 1'den 13'e kadar olan kart değerleri (as'tan papaza)
            file_name = f"{suit.lower()}_{value}.png"
            path = os.path.join("kartlar", file_name)

            image = pygame.image.load(path)

            kart_resimleri[(suit, value)] = pygame.transform.scale(image, (100, 150))  # Görseli boyutlandırma kodu
    return kart_resimleri

# Kart görselleri yüklenir
kart_resimleri = kart_yukle()

# Oyun için gerekli değişkenler
drawn_cards = []
suits = ['Kupa', 'Maça', 'Karo', 'Sinek']
values = list(range(1, 14))

total_score = 0  # Oyuncunun toplam puanı
remaining_draws = 10  # Kalan çekme hakkı
last_scores = []  # Geçmiş skorlar (son 3 oyun) ekranda görüntüleme
max_score = 0  # En yüksek skor
score_added = False  # Skorun eklenip eklenmediğini kontrol eder

# "ÇEK" butonunun koordinatları
button_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 200, 100, 50)
# "Tekrar Oyna" butonunun koordinatları
new_game_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 150, 200, 50)

running = True  # Oyun döngüsünün çalışıp çalışmadığını kontrol eden kodumuz
game_over = False  # Oyunun bitip bitmediğini kontrol eden kodumuz

# Kart destesini oluşturur ve karıştırır
deck = [(suit, value) for suit in suits for value in values]
random.shuffle(deck)

# Animasyon değişkenlerimiz
animating_card = None  # Şu anda hareket eden kart
animation_progress = 0  # Animasyonun ilerleme durumu [0, 1] arasında
flipping = False  # Kartın dönüp dönmediğini kontrol eder
animation_speed = 0.007  # Animasyon hızı

# Yeni oyun başlatan fonksiyon
def yeni_oyun_baslat():
    global deck, drawn_cards, total_score, remaining_draws, game_over, score_added, animating_card, flipping
    deck = [(suit, value) for suit in suits for value in values]  # Yeni deste oluşturur
    random.shuffle(deck)  # Desteyi karıştırır
    drawn_cards = []  # Çekilmiş kartları sıfırlar
    total_score = 0  # Toplam puanı sıfırlar
    remaining_draws = 10  # Çekme hakkını sıfırlar
    game_over = False  # Oyunun bitti durumunu sıfırlar
    score_added = False  # Skor eklenme durumunu sıfırlar
    animating_card = None  # Animasyon sıfırlanır
    flipping = False  # Kart dönme durumu sıfırlanır

# Kart animasyonunu başlatan fonksiyon
def animasyon_baslat(card, hedef_x, hedef_y):
    global animating_card, animation_progress, flipping
    animating_card = {
        "card": card,
        "start_x": deck_position[0],  # Animasyon başlangıç x konumu
        "start_y": deck_position[1],  # Animasyon başlangıç y konumu
        "end_x": hedef_x,  # Animasyon hedef x konumu
        "end_y": hedef_y,  # Animasyon hedef y konumu
    }
    animation_progress = 0  # Animasyon başlangıç durumu
    flipping = False  # Kart dönme durumu sıfırlanır

# Animasyonu güncelleyen fonksiyon
def animasyonu_guncelle():
    global animation_progress, animating_card, drawn_cards, flipping
    if animating_card:
        animation_progress += animation_speed
        if animation_progress >= 1:
            animation_progress = 1
            if flipping:
                drawn_cards.append(animating_card["card"])
                animating_card = None
            else:
                flipping = True
                animation_progress = 0
        else:
            # Kartın animasyon sırasındaki geçici koordinatlarını hesaplar
            current_x = animating_card["start_x"] + animation_progress * (animating_card["end_x"] - animating_card["start_x"])
            current_y = animating_card["start_y"] + animation_progress * (animating_card["end_y"] - animating_card["start_y"])
            return current_x, current_y
    return None

# Oyun döngüsü kodumuz
while running:
    screen.fill(LIGHT_GREEN)  # Arka plan rengini açık yeşil yapan kod

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Oyundan çıkış işlemi
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:  # Fareye tıklama işlemi
            if button_rect.collidepoint(event.pos) and remaining_draws > 0 and not game_over and not animating_card:
                # Eğer "ÇEK" butonuna tıklandıysa ve hak varsa kart çek
                card = deck.pop()  # Desteden bir kart al
                remaining_draws -= 1  # Kalan çekme hakkını azalt
                hedef_x = 20 + len(drawn_cards) * 120  # Yeni kartın hedef x koordinatı
                hedef_y = 150  # Yeni kartın hedef y koordinatı
                animasyon_baslat(card, hedef_x, hedef_y)  # Animasyonu başlat
                total_score += card[1]  # Kartın değerini toplam puana ekle
                if remaining_draws == 0:  # Eğer hak bitmişse oyun biter
                    game_over = True
            elif game_over and new_game_button.collidepoint(event.pos):
                yeni_oyun_baslat()  # "Tekrar Oyna" butonuna tıklandıysa yeni oyunu başlat

    # Desteyi ekrana çiz
    screen.blit(deck_image, deck_position)

    # Animasyonu güncelle ve çiz
    animasyon_koordinatlari = animasyonu_guncelle()
    if animasyon_koordinatlari:
        if flipping:
            progress = animation_progress * 2
            if progress < 1:  # Kart arka yüzünü göster
                flipped_width = int(100 * (1 - progress))  # Kart genişliği daralır
                flipped_image = pygame.transform.scale(card_back_image, (flipped_width, 150))
                flipped_x = animasyon_koordinatlari[0] + (100 - flipped_width) // 2
                screen.blit(flipped_image, (flipped_x, animasyon_koordinatlari[1]))
            else:  # Kart ön yüzünü göster
                progress -= 1
                flipped_width = int(100 * progress)  # Kart genişliği artar
                flipped_image = pygame.transform.scale(kart_resimleri[animating_card["card"]], (flipped_width, 150))
                flipped_x = animasyon_koordinatlari[0] + (100 - flipped_width) // 2
                screen.blit(flipped_image, (flipped_x, animasyon_koordinatlari[1]))
        else:  # Kart hareket ediyor
            screen.blit(card_back_image, animasyon_koordinatlari)

    # Toplam puanı ekrana yazdıran kodumuz
    text = font.render(f"Toplam Puan: {total_score}", True, BLACK)
    screen.blit(text, (20, 20))
    draws_text = font.render(f"Kalan Hak: {remaining_draws}", True, BLACK)
    screen.blit(draws_text, (20, 60))

    # Skor tahtasını yazdıran kodumuz
    scoreboard_text = font.render(f"Scoreboard: {', '.join(map(str, last_scores))}", True, BLACK)
    max_score_text = font.render(f"En Yüksek Puan: {max_score}", True, RED)
    screen.blit(scoreboard_text, (WIDTH // 2 - 200, 20))
    screen.blit(max_score_text, (WIDTH // 2 - 200, 60))

    # Çekilmiş kartları ekrana çizen kodumuz
    x_offset = 20
    y_offset = 150
    for card in drawn_cards:
        card_image = kart_resimleri[card]
        screen.blit(card_image, (x_offset, y_offset))
        x_offset += 120

    if not game_over:
        # "ÇEK" butonunu çizen kodumuz
        pygame.draw.rect(screen, RED, button_rect)
        button_text = font.render("ÇEK", True, BLACK)
        screen.blit(button_text, (button_rect.x + 20, button_rect.y + 10))

    if game_over:
        # Eğer skor eklenmemişse skor listesini güncelle
        if not score_added:
            last_scores.insert(0, total_score)  # Skoru listeye ekler
            if len(last_scores) > 3:  # Sadece son 3 skor tutulur
                last_scores.pop()
            if total_score > max_score:  # Eğer yeni skor en yüksek skor ise güncelle
                max_score = total_score
            score_added = True

        # "Tekrar Oyna" butonunu çizen kodumuz
        pygame.draw.rect(screen, RED, new_game_button)
        new_game_text = font.render("Tekrar Oyna", True, BLACK)
        screen.blit(new_game_text, (new_game_button.x + 50, new_game_button.y + 10))

    pygame.display.flip()

pygame.quit()
