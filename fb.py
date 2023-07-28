from __future__ import print_function
import pygame
import neat
import os
import random

pygame.font.init() #pygame.font.init() fonksiyonu, Pygame font modülünün yüklenmesini sağlar. Puan ve deneme yazıları için gereklidir.
pygame.init() #pygame.init() fonksiyonu, Pygame kütüphanesinin yüklenmesini sağlar. 
Game_Width = 500
Game_Height = 800 #oyun ekranının boyutlarını ayarlıyoruz.
STAT_FONT = pygame.font.SysFont("Times New Roman", 40) #burada fontu veriyoruz score ve deneme yazıları için.
END_FONT = pygame.font.SysFont("Times New Roman", 80) 
SCREEN = pygame.display.set_mode((Game_Width, Game_Height))
bird_image = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird.png"))) ] #kuş
base_image = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")).convert_alpha()) #zemin
pipe_image = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")).convert_alpha()) #boru
bg_image = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "bg.png")).convert_alpha(), (600, 900)) #background

def drawGame(start, birds, pipes, base, Puan, gen):
    start.blit(bg_image, (0, 0)) # pygame kütüphanesi içindeki Surface sınıfının blit() metodunu kullanarak, backgroundu oyun ekranının sol üst köşesine konumlandırır.
    for pipe in pipes: # her bir boru için draw() metodunu çağırarak, oyun ekranında her bir borunun çizilmesini sağlar.
        pipe.draw(start)
    s = STAT_FONT.render("Puan: " + str(Puan), 0, (255, 255, 0)) #bu satır, oyun ekranında "Puan: " + Puan değişkeninin değerini içeren bir metin nesnesi oluşturur 
    start.blit(s, (10 , 90)) # ve ekranın sağ üst köşesinde bu metni görüntüler. Bu satırın sonucu, oyun ekranındaki metin nesnesinin konumlandırmasıdır. (255, 255, 0) ise bize rengi gösterir.
    s = STAT_FONT.render("Deneme: " + str(gen), 1, (255, 255, 0))
    start.blit(s, (10, 10))
    base.draw(start) #zemini görüntüler. oyun ekranında zemini görüntüler
    for bird in birds:  #her bir kuş için draw() metodunu çağırarak, oyun ekranında her bir kuşun çizilmesini sağlar.
        bird.draw(start)
    pygame.display.update() #pygame.display.update() fonksiyonu, pencerenin içeriğinin ekranda görüntülenmesini sağlar.

class Bird:
    def __init__(self, x, y):
        self.pixels = 0  #kare geçişleri
        self.speed = 0  # hız
        self.x = x  # kuşun başlangıç x koordinatı
        self.y = y  # kuşun başlangıç y koordinatı
        self.img = bird_image[0] #  kuş görselini alıyoruz

    def move(self):
        self.pixels += 1  # her kare 1 geçişinde artırıyoruz
        movement = self.speed * (self.pixels) + 1.5* (self.pixels) ** 2  # yer değiştirme miktarı
        if movement >= 16: # hız çok artarsa düzgün bir görüntü almak için sınırlamamız lazım.
            movement = 16
        if movement < 0:
            movement -= 2
        self.y += movement #y ekseninde yer değiştirildiği için y eksenini arttırıyoruz.
    
    def draw(self, start):
        new_rect = self.img.get_rect(topleft=(self.x, self.y)) # get_rect() fonksiyonunu kullanarak, görüntünün sınır kutusunu alır. Sınır kutusu, görüntünün etrafındaki en küçük dikdörtgen kutudur ve görüntüyü saran bir dikdörtgen olarak düşünülebilir. 
        start.blit(bird_image[0], new_rect.topleft) #topleft parametresi, sınır kutusunun sol üst köşesinin konumunu belirtir.

    def jump(self):
        self.speed = -10  # zıplarken velocitynin negatif olması gerekli çünkü ekranın sol üst köşesi (0,0) noktası
        self.pixels = 0  #kare geçişlerini korumamız lazım yoksa kuş hep aşağı düşer

    def mask(self):
        return pygame.mask.from_surface(self.img) #from_surface() yöntemi, self.img yüzeyinden bir maske oluşturur ve oluşturulan maskeyi döndürür. ileride çarpışma sırasında kullanılacaktır.

class Base: #zemin için class
    def __init__(self, y):
        self.y = y
        self.x = 0 # zeminin x ve y eksenleri
    def draw(self, start):
        start.blit(base_image, (self.x, self.y))#zeminin görüntüsünü ekranda verir koordinatlara göre.

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randrange(50, 450) # boruların intervalinin başladığı yer random geliyor. Çünkü boruların y eksenine göre konumlarının random olması gerekir.
        self.topPipe = pygame.transform.flip(pipe_image, False, True)  # bende sadece alt borunun görseli vardı üst boruyu flip ettirdim görsel olarak sadece boyut değişecek.
        self.bottomPipe = pipe_image  # alt boru
        self.top = self.height - pygame.transform.flip(pipe_image, False, True).get_height()#üst boru için pipe'ın uzunluğunu random sayıdan çıkarıyoruz.
        self.bottom = self.height + 160 #intervalle random sayıyı toplayıp yerini toplayarak alt boru ve bir interval elde ediyoruz. yani iki boru arası mesafe ve alttaki boruyu veriyor bize self.bottom.
        self.passed = False # boru geçildi mi kontrol edeceğiz mainde.
 
    def findCollapse(self, bird):  # kuşun yere ya da boruya çarptığını anlamak için lazım
        bird_mask = bird.mask()
        maskedTop = pygame.mask.from_surface(self.topPipe)
        maskedBottom = pygame.mask.from_surface(self.bottomPipe) # aşağıda overlap etmemiz için maskeleme yapmamız gerekiyor.
        bottomCollapse = bird_mask.overlap(maskedBottom,(self.x - bird.x, self.bottom - round(bird.y)))#overlap() fonksiyonu, iki maske arasındaki en uygun çarpışma noktasını bulur 
        topCollapse = bird_mask.overlap(maskedTop, (self.x - bird.x, self.top - round(bird.y)))#maske yüzeylerinin örtüşen piksellerini karşılaştırarak çarpışma algılama işlemini gerçekleştirir. burada offsetleri tutuyoruz. borunun x'i ile kuşun x'i arasındaki mesafe ve #borunun y'si ile kuşun y'si arasındaki mesafeye bakılıyo alt ve üst boru için.
        if bottomCollapse or topCollapse: # herhangi biri true döndürürse çarpışma vardır demek.
            return True
        return False
    
    def move(self):
        self.x -= 8# borunun hızını x ekseninden çıkartarak gidiyoruz ki boru ekranda kalmasın.

    def draw(self, start):
        start.blit(self.topPipe, (self.x, self.top)) #boruları ekrana bastırıyoruz. blit metoduyla ve konum veriyoruz. üst boru için self.top,
        start.blit(self.bottomPipe, (self.x, self.bottom))#alt boru için ise self.bottomu veriyoruz.

Deneme=0 #kaç deneme yaptığını tutmak için deneme diye bir variable oluşturduk
def main(birdss, config):
    global Deneme 
    Deneme += 1 #her maine geldiğinde deneme sayısı bir artar.
    nn = []  # içine append edilecek neural network arrayi
    genome = []  # genomlar
    birds = []  # networku kullanarak ilerleyen bird

    for _, i in birdss:
        birds.append(Bird(220,250))# her kuşun başlangıç pozisyonu belirlenir.
        nn.append(neat.nn.FeedForwardNetwork.create(i, config))#NEAT algoritması için gerekli olan konfigürasyon dosyası ve i değeri ile birlikte bir ileri beslemeli sinir ağı oluşturulur. Bu sinir ağı, nn listesine eklenir.
        i.fitness = 0 # başlangıçta tüm genomların skorları 0.
        genome.append(i) # tüm genomlar genome'a append edilir.
    clock = pygame.time.Clock()#oyunun belirli bir hızda çalışmasını sağlar. Clock, oyun döngüsünün her turunda, geçen süreyi hesaplayarak, oyunu belirli bir FPS değerinde çalıştırır.
    pipes = [Pipe(600)]#boruların yüksekliği belirlenir
    base = Base(730)#dikey konum belirlenir
    start = pygame.display.set_mode((500,800)) #oyunun görüntüsü ekrana yansıtılır.
    puan = 0 # kuş eğer borudan geçerse puan artar başlangıçta puan 0'dır.
    flag = True # flag false dönerse aşağıdaki döngüden çıkılır ve deneme sayısı bir artarak oyun en baştan başlar ancak bu esnada fitness fonksiyonlarınınd değerleri tabiki kaybolmaz
    while flag:
        clock.tick(30)#30 fps çalıştırıyoruz oyunu yani her saniyede oyunu 30 kare görürüz.
        for event in pygame.event.get():#oyunu kapatma ile ilgili döngü.
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        pipeZeroOrOne  = 0
        if len(birds) > 0: #0 tane kuş varsa oyunu baştan başlat.
            if birds[0].x > pipes[0].topPipe.get_width() + pipes[0].x : #eğer kuş boruyu geçerse borunun indexini  1 yap. yani o borudan geçilmiş anlamına gelir.
                pipeZeroOrOne = 1
        else:
            flag = False
            break

        for i, bird in enumerate(birds):
            bird.move()
            genome[i].fitness += 0.1 # bird hareket ettikçe devam etmesi için fitness skorunu artırıyoruz.
            jumpOrNot = nn[i].activate((bird.y, abs(bird.y - pipes[pipeZeroOrOne].height), abs(bird.y - pipes[pipeZeroOrOne].bottom)))                                                                                                             # sonuca göre aktivasyon fonksiyonu çalışıyor
            if jumpOrNot[0] > 0.5: #yukarıdaki kodda yapay sinir ağı modelini kullanarak, kuşun yüksekliği ve en yakın borular arasındaki dikey mesafelerin farklarını girdi olarak alıyor. 
                bird.jump()
        removePipe = []
        addPipe = False
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.findCollapse(bird) or bird.y + bird.img.get_height() >= 730 or bird.y < 0: # kuşlardan biri boruya çarparsa ya da kuş oyunun dışına çıkarsa fitness scoru bir azalıyor, 
                    genome[x].fitness -= -1  # kuş çarparsa genomun fitness skorunu düşürüyoruz bunun nedeni sonraki jenerasyon için fitness fonksiyonu daha doğru bir seçim yapsın.
                    birds.pop(x)#kuşun elemanı listeden çıkarılır.
                    nn.pop(x)#nnün elemanı listeden çıkarılır.
                    genome.pop(x)#genomun elemanı listeden çıkarılır.
                if not pipe.passed and pipe.x < bird.x: # eğer kuş pipedan geçmişse 
                    pipe.passed = True
                    addPipe = True #yeni bir pipe ekliyoruz

            if pipe.x + pipe.topPipe.get_width() < 0:
                removePipe.append(pipe)
            pipe.move()

        if addPipe: # bird pipe'ı geçiyorsa fitness skorunu artırıyoruz
            puan += 1
            for t in genome:
                t.fitness += 5  # boruyu geçen genomun fitness skoru 5 artıyor
            pipes.append(Pipe(600))

        for k in removePipe: #geçilen pipeları kaldırıyoruz.
            pipes.remove(k)

        drawGame(start, birds, pipes, base, puan, Deneme)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,neat.DefaultSpeciesSet, neat.DefaultStagnation,config_path) # config dosyasını içeri aldık
    p = neat.Population(config)#NEAT algoritmasında kullanılacak bir popülasyon oluşturur.
    p.add_reporter(neat.StdOutReporter(True))#NEAT algoritmasının ilerlemesini izlemek için raporlama işlevleri ekler.
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)#NEAT algoritmasının ilerlemesini izlemek için raporlama işlevleri ekler.
    winner = p.run(main, 50)#En iyi yapay sinir ağı, fitness fonksiyonuna göre seçilir ve winner değişkeninde saklanır.
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    run(config_path)