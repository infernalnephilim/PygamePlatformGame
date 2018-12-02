# Aleksandra Półtorak Projekt 1
import pygame
from pygame.math import Vector2

playerColor = (153, 0, 204)
backgroundColor = (204, 204, 255)
platformColor = (102, 0, 102)

windowWidth = 1280 # szerokosc okna
windowHeight = 768 # wysokosc okna

FPS = 60

# klasa opisujaca wartosci fizyczne
class Physics(object):
    characterMass = 1.0
    gravity = Vector2(0, 980)
    airResistance = 1.5
    friction = 3.0
    calculationsPerFrame = 8
    timeBetweenFrames = 1.0 / FPS
    timeBetweenPhysicsCalculations = timeBetweenFrames / calculationsPerFrame
    jumpForce = Vector2(0, -700 / timeBetweenPhysicsCalculations)

# klasa opisujaca bohatera gry
class Character(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('character.png').convert_alpha()
        self.image = pygame.transform.flip(self.image, True, False)

        # okreslenie wielkosci i masy bohatera
        self.width = 40
        self.halfWidth = self.width / 2
        self.height = 60
        self.halfHeight = self.height / 2
        self.size = (self.width, self.height)
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect()
        self.mass = Physics.characterMass

        # okreslenie pozycji bohatera
        self.position = Vector2(240, 600)
        self.prevPosition = Vector2()
        self.nextPosition = Vector2()

        # okreslenie predkosci poruszania sie bohatera
        self.velocity = Vector2()
        self.nextVelocity = Vector2()
        self.velocityMAX = 500

        # okreslenie kierunku poruszania sie bohatera
        self.directionX = 0
        self.prevDirectionX = -1

        # zmienna opisujaca czy gracz chce wykonac skok
        self.isGoingToJump = False

    # skok bohatera
    def jump(self):
        if self.velocity.y == 0:
            self.isGoingToJump = True

    # poruszanie sie bohatera
    def move(self, force, timeStep):
        acceleration = force / self.mass

        # obliczenia przy pomocy algorytmu Eulera
        self.nextVelocity = self.velocity + acceleration * timeStep
        self.nextPosition = self.position + self.nextVelocity * timeStep

        self.prevPosition = self.position
        self.position = self.nextPosition
        self.velocity = self.nextVelocity

    # rysowanie bohatera
    def draw(self, gameDisplay):
        # odbicie lustrzane obrazka, jesli bohater zmienia kierunek poruszania sie
        if self.directionX != self.prevDirectionX and self.directionX != 0:
            self.image = pygame.transform.flip(self.image, True, False)

        if self.directionX != 0:
            self.prevDirectionX = self.directionX

        positionX = self.position.x - self.halfWidth
        positionY = self.position.y - self.height
        self.rect.x = positionX
        self.rect.y = self.position.y
        characterPosition = Vector2(positionX, positionY)
        gameDisplay.blit(self.image, characterPosition)

# klasa opisujaca platformy
class Platform(pygame.sprite.Sprite):
    def __init__(self, position, size):
        super().__init__()
        self.image = pygame.image.load('platforms.png')
        self.width = size.x
        self.height = size.y
        self.image = pygame.transform.scale(self.image, (int(self.width), int(self.height)))
        self.rect = self.image.get_rect()

        self.position = position
        self.hasAlreadyCollided = False # czy bohater juz ma kolizje z platforma

    # kolizja bohatera z platforma, jesli nastepuje zwraca True
    def isColliding(self, character):
        position = character.position
        characterLeft = position.x - character.halfWidth
        characterRight = position.x + character.halfWidth
        chatacterTop = position.y - character.height
        characterBottom = position.y

        position = self.position
        width = self.width
        height = self.height
        platformLeft = position.x
        platformRight = position.x + width
        platformTop = position.y
        platformBottom = position.y + height

        # sprawdzenie czy sprite znajduje sie "poza" platforma
        if characterRight < platformLeft or characterLeft > platformRight \
                or chatacterTop > platformBottom or characterBottom < platformTop:
            return False
        else:
            return True

    # rysowanie platformy
    def draw(self, gameDisplay):
        gameDisplay.blit(self.image, self.position)

# klasa opisujaca level gry
class Level1(object):
    def __init__(self):
        self.backgroundImage = pygame.image.load('bg.jpg')
        self.backgroundSize = (windowWidth, windowHeight)
        self.backgroundImage = pygame.transform.scale(self.backgroundImage, self.backgroundSize)
        # tablica platform znajdujacych sie w tym levelu
        self.platforms = [Platform(Vector2(200, 410), Vector2(128, 50)),
                          Platform(Vector2(450, 290), Vector2(128, 50)),
                          Platform(Vector2(1120, 550), Vector2(128, 50)),
                          Platform(Vector2(900, 450), Vector2(128, 50)),
                          Platform(Vector2(750, 320), Vector2(128, 50)),
                          Platform(Vector2(0, 668), Vector2(400, 100)),
                          Platform(Vector2(800, 668), Vector2(500, 100)),
                          Platform(Vector2(180, 200), Vector2(128, 50))]
    # rysowanie tla i platform
    def draw(self, gameDisplay):
        gameDisplay.fill(backgroundColor)
        gameDisplay.blit(self.backgroundImage, (0, 0))
        for platform in self.platforms:
            platform.draw(gameDisplay)

# klasa opisujaca gre, zawiera glowna petle gry
class Game(object):
    def __init__(self):
        pygame.init() # inicjalizacja PyGame
        # ustawienie wielkosci okna gry
        self.displayWidth = windowWidth
        self.displayHeight = windowHeight
        self.gameDisplay = pygame.display.set_mode((self.displayWidth, self.displayHeight))
        # ustawienie tytulu okna
        pygame.display.set_caption('Projekt 1 - Aleksandra Półtorak')

        # zegar
        self.clock = pygame.time.Clock()

        self.character = Character() # utworzenie bohatera
        self.level = Level1() # utworzenie levelu
        self.platforms = self.level.platforms

        self.playingGame = True
        self.gameOver = False

    # funkcja zapobiegajaca wyjsciu bohatera poza lewa i prawa strone okna gry
    def setInvisibleWalls(self):
        character = self.character
        characterLeftBorder = character.rect.left
        characterRightBorder = character.rect.right
        if (characterLeftBorder <= 0 and character.directionX < 0):
            character.directionX = 0
            character.velocity.x = 0
        if (characterRightBorder >= self.displayWidth and character.directionX > 0):
            character.directionX = 0
            character.velocity.x = 0

    # sprawdzenie czy bohater spadl w dziure, jesli tak to ustawia gameOver = True
    def gameOverCollision(self, character):
        floorPosition = self.displayHeight + character.height
        if character.position.y > floorPosition:
            character.position.y = floorPosition
            character.velocity.y = 0
            character.directionX = 0
            self.gameOver = True

    # obsluga kolizji
    def collisions(self):
        character = self.character
        # koniec gry w razie spadniecia do dziury
        self.gameOverCollision(character)
        # kolizje z platformami
        for platform in self.platforms:
            if platform.isColliding(character):
                # warunki potrzebne do sprawdzenia czy bohater stoi na platformie
                # pozycja bohatera miedzy lewa i prawa krawedzia platformy
                condition1 = (platform.position.x - character.halfWidth < character.position.x < platform.position.x
                              + platform.width + character.halfWidth)
                # pozycja bohatera pomiedzy gorna i dolna krawedzia platformy
                condition2 = (platform.position.y < character.position.y < platform.position.y + platform.height / 10.0)
                # bohater spada
                condition3 = character.velocity.y > 0

                onPlatform = condition1 and condition2 and condition3
                if onPlatform: # jesli stoi na platformie
                    character.position.y = platform.position.y  # dol bohatera = gora platformy
                    character.velocity.y = 0
                else: # jesli koliduje w jakis inny sposob z platforma
                    if platform.hasAlreadyCollided:
                        continue
                    else:
                        platform.hasAlreadyCollided = True
                    # zatrzymanie bohatera
                    character.velocity.x = 0
                    character.velocity.y = 0
                    character.directionX = 0
            else:
                platform.hasAlreadyCollided = False

    # funkcja obliczajaca sile dzialajaca na bohatera
    def calculateForces(self):
        character = self.character
        # grawitacja
        force = Physics.gravity * character.mass

        # chodzenie
        walking = Vector2(character.directionX * 1200, 0)
        force += walking

        # predkosc bohatera
        character.nextVelocity.x = max(min(character.velocity.x, character.velocityMAX), -character.velocityMAX)

        # skakanie
        if character.isGoingToJump:
            force += Physics.jumpForce
            character.isGoingToJump = False

        # tarcie po puszczeniu strzalki kierunkowej
        if character.directionX == 0:
            force.x += -3 * Physics.friction * character.velocity.x

        # opor powietrza
        if character.velocity.y != 0:
            force -= Physics.airResistance * character.velocity
        return force

    # funkcja rysujaca scene
    def drawScene(self):
        self.level.draw(self.gameDisplay)
        self.character.draw(self.gameDisplay)
        if self.gameOver:
            self.gameOverText(self.gameDisplay, "Game Over", windowWidth / 2, windowHeight / 2)
        pygame.display.update()

    # funkcja wyswietlajaca tekst "Game Over" po wpadnieciu bohatera do dziury
    def gameOverText(self, gameDisplay, text, x, y):
        font = pygame.font.Font('freesansbold.ttf', 105)
        textSurface = font.render(text, True, (255, 255, 255))
        textRect = textSurface.get_rect()
        textRect.center = (x, y)
        gameDisplay.blit(textSurface, textRect)
        pygame.display.update()

    # glowna petla gry
    def gameLoop(self):
        while self.playingGame:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.playingGame = False
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        self.character.directionX = 0

                if event.type == pygame.KEYDOWN:
                    # jesli gra sie nie skonczyla to reaguj na nacisniecie klawiszy
                    if self.gameOver == False:
                        if event.key == pygame.K_LEFT:
                            self.character.directionX = -1

                        if event.key == pygame.K_RIGHT:
                            self.character.directionX = 1

                        if event.key == pygame.K_UP:
                            self.character.jump()

                    if event.key == pygame.K_ESCAPE:
                        self.playingGame = False

            character = self.character

            # ilosc obliczen fizycznych na klatke
            physicsCalculationsNumber = Physics.calculationsPerFrame

            # petla fizyki
            while physicsCalculationsNumber != 0:
                moveForce = self.calculateForces() # obliczenie sily dzialajacej na bohatera
                character.move(moveForce, Physics.timeBetweenPhysicsCalculations) # ruch bohatera

                self.collisions() # kolizje
                self.setInvisibleWalls() # zapobieganie wyjsciu bohatera za okno gry

                physicsCalculationsNumber -= 1
            self.drawScene() # rysowanie sceny
            self.clock.tick(FPS)


game = Game()
game.gameLoop()

pygame.quit()
quit()
